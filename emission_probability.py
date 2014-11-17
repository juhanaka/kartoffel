import numpy as np
import math
import db_wrapper
import utils

GPS_SIGMA = 3.0

def add_segments(ways):
    for way in ways:
        way['segments'] = []
            
        for i, point in enumerate(way['points']):
            if i != 0:
                way['segments'].append((way['points'][i-1], point))
    return ways

def add_distances(ways, base_point):
    for way in ways:
        way['distances'] = [utils.point_to_lineseg_dist(segment, base_point) for segment in way['segments']]
    return ways

# Add angle of the tangent of each segment
# The tangent is the line between the two endpoints of the segment
def add_tangents(ways):
    for way in ways:
        way['angles'] = []
        for segment in way['segments']:
            delta_y = segment[1][1] - segment[0][1]
            delta_x = segment[1][0] - segment[0][0]
            way['angles'].append(math.atan(delta_y / delta_x))
    return ways 


# Tangent score is the inner product of the tangent vector and inferred heading vector
# Since we have the angles of both, the tangent is cosine squared of the angle between
# the two vectors
def add_tangent_scores(ways, base_angle):
    for way in ways:
        tangent_scores = [math.cos(angle-base_angle) for angle in way['angles']]
        way['tangent_scores'] = tangent_scores
    return ways

# Distance score = Probability that observation came from a road segment
# given that GPS error is Gaussian around the road segment with stdev sigma
def add_distance_scores(ways, sigma):
    p = lambda dist: (1/(math.sqrt(2*math.pi)*sigma))*math.exp(-0.5*(dist/sigma)**2)
    for way in ways:
        way['distance_scores'] = [p(dist) for dist in way['distances']]
    return ways


# Takes an array of ways, checks which nodes of the ways are within 'radius' meters of 'base_point'
# Returns array of dicts, where each dict has the osm_id of the way, and the indices of the nodes
# within the radius.
def indices_of_nodes_within_radius(base_point, ways, radius):
    results = []
    for way in ways:
        indices = [point_idx for point_idx, point in enumerate(way['points']) if utils.euclidean_dist(point, base_point) <= radius]
        nodes = {'osm_id': way['osm_id'], 'indices': indices}
        results.append(nodes)
    return results


def test(lat, lon, radius):
    point, ways = db_wrapper.query_ways_within_radius(lat, lon, radius)
    if ways is None or point is None:
        return
    ways = add_segments(ways)
    ways = add_distances(ways, point)
    ways = add_tangents(ways)
    ways = add_tangent_scores(ways, 0)
    ways = add_distance_scores(ways, GPS_SIGMA)
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    print pp.pprint(ways)
