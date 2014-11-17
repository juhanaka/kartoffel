import re
import sys
from plot_gps_data import read_gps_file
from db_wrapper import query_ways_within_radius, get_node_id
from emission_probability import _add_distances, _add_segments

DEFAULT_MAX_DISTANCE = 50

# Simple map matching algorithm that picks the road segment closest to the observation
def simple_match(filename, **kwargs):
    max_distance = kwargs['max_distance'] if 'max_distance' in kwargs else DEFAULT_MAX_DISTANCE
    with open(filename, 'r') as f:
        data = read_gps_file(f, delimiter=',')
    points = zip(data['lat'], data['long'])
    matches = []
    for i, point in enumerate(points):
        # Don't query the same point twice
        if i==0 or point != points[i-1]:
            point_merc, ways = query_ways_within_radius(point[0], point[1], max_distance)
            min_dist = sys.maxint
            min_way = None
            min_idx = None
            if ways:
                _add_segments(ways)
                _add_distances(ways, point_merc)
                for way in ways:
                    if way['osm_id'] < 0:
                        continue
                    local_min_idx, local_min_dist = min(enumerate(way['distances']), key=lambda x: x[1])
                    if local_min_dist <= min_dist:
                        min_dist = local_min_dist
                        min_idx = local_min_idx
                        min_way = way['osm_id']
        point_dict = {'point_index': i, 'point': point_merc, 'way': min_way, 'index_of_segment': min_idx}
        matches.append(point_dict)
    return matches

def remove_consecutive_duplicates(node_ids):
    cleaned_node_ids = []
    i = 1
    cleaned_node_ids.append(node_ids[0])
    while(i<len(node_ids)):
        if node_ids[i] != node_ids[i-1]:
            cleaned_node_ids.append(node_ids[i])
        i += 1
    return cleaned_node_ids

# Get the node ids of the start and endpoints of the nodes
def get_node_ids(matches):
    node_ids = []
    for i, match in enumerate(matches):
        if match['way'] is None:
            node_ids.append(None)
            continue
        # Don't query the same point twice
        if i == 0 or match['way'] != matches[i-1]['way'] or match['index_of_segment'] != matches[i-1]['index_of_segment']:
            start_node = get_node_id(match['way'], match['index_of_segment'])
            start_node = re.findall(r'\d+', str(start_node))[0]
            end_node = get_node_id(match['way'], match['index_of_segment'] + 1)
            end_node = re.findall(r'\d+', str(end_node))[0]
        node_ids.append((start_node, end_node))
    return node_ids
 
def write_to_file(node_ids, filename):
    with open(filename, 'w') as f:
        f.write('Segment start id, Segment end id\n')
        for node in node_ids:
            if node is None:
                f.write('NA\n')
            else:
                f.write(node[0] + ', ' + node[1] + '\n')


