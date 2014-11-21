import numpy as np
import math
from db_wrapper import query_ways_within_radius
import utils

GPS_SIGMA = 10.0
W_DIST = 0.8
W_TANG = 0.2

# SUMMARY
#--------------------
# The main datastructure in this file is the ways array, which contains all the
# OSM ways within a certain distance of the observation. A way in the ways array
# is a dict: ways[0] = {'osm_id': 264056469L, 'points': [(x1,y1), (x2,y2) ... ] 
# With each function, the ways dictionary is extended with different attributes.


# A segment is the line between two consecutive nodes
# it is stored as a tuple containing its endpoints
def _add_segments(ways):
    for way in ways:
        way['segments'] = []
            
        for i, point in enumerate(way['points']):
            if i != 0:
                way['segments'].append((way['points'][i-1], point))
    return ways

# Add distances from each segment to base_point
def _add_distances(ways, base_point):
    for way in ways:
        way['distances'] = [utils.point_to_lineseg_dist(segment, base_point) for segment in way['segments']]
    return ways

# Add angle of the tangent of each segment
# The tangent is the line between the two endpoints of the segment
def _add_tangents(ways):
    for way in ways:
        way['angles'] = []
        for segment in way['segments']:
            delta_y = segment[1][1] - segment[0][1]
            delta_x = segment[1][0] - segment[0][0]
            if delta_x == 0:
                way['angles'].append(math.pi/2 if delta_y > 0 else -math.pi/2)
            else:
                way['angles'].append(math.atan2(delta_y, delta_x) if delta_x !=0 else math.pi/2)
    return ways 


# Tangent score is the inner product of the tangent vector and inferred heading vector
# Since we have the angles of both, the tangent is cosine squared of the angle between
# the two vectors
def _add_tangent_scores(ways, base_angle):
    for way in ways:
        tangent_scores = []
        for angle in way['angles']:
            if not way['oneway']: 
                converted_angle = angle % math.pi
                converted_base = base_angle % math.pi
                diff_angle = converted_angle - converted_base
            else:
                diff_angle = angle-base_angle
            tangent_scores.append((math.cos(diff_angle)+1)/2)
        way['tangent_scores'] = tangent_scores
    return ways

# Distance score = Probability that observation came from a road segment
# given that GPS error is Gaussian around the road segment with stdev sigma
def _add_distance_scores(ways, sigma):
    p = lambda dist: (1/(math.sqrt(2*math.pi)*sigma))*math.exp(-0.5*(dist/sigma)**2)
    for way in ways:
        way['distance_scores'] = [p(dist) for dist in way['distances']]
    return ways

def _add_emission_probabilities(ways):
    for way in ways:
        way['emission_probabilities'] = [way['distance_scores'][i]*W_DIST + way['tangent_scores'][i]*W_TANG for i in range(len(way['segments']))]
    return ways

# Return n segments with highest emission probabilities
def _get_top_n(ways, n):
    segments = []
    probabilities = []
    for way in ways:
        for i, p in enumerate(way['emission_probabilities']):
            segments.append({'way_osm_id': way['osm_id'], 'index_in_way': i, 'endpoints': way['segments'][i], 'direction': None})
            probabilities.append(p)
    combined = zip(segments, probabilities)
    combined.sort(key=lambda el: -el[1])
    segments = [x[0] for x in combined]
    probabilities = [x[1] for x in combined]
    return segments[:n], probabilities[:n]

# Observation provided in form: (lat, lon, course) all in degrees
# Radius in meters
# n is the number of segments returned with the top emission probabilities
def compute_emission_probabilities(observation, radius, n):
    lat, lon, course, speed = observation
    course = math.radians(-course+90)
    point, ways = query_ways_within_radius(lat, lon, radius)
    if ways is None or point is None:
        return
    ways = _add_segments(ways)
    ways = _add_distances(ways, point)
    ways = _add_tangents(ways)
    ways = _add_tangent_scores(ways, course)
    ways = _add_distance_scores(ways, GPS_SIGMA)
    ways = _add_emission_probabilities(ways)
    segments, probabilities = _get_top_n(ways, n)
    return segments, probabilities, point

