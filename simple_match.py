import re
import sys
from plot_gps_data import read_gps_file
from db_wrapper import query_ways_within_radius, get_node_id
from emission_probability import add_distances

def simple_match(filename):
    with open(filename, 'r') as f:
        data = read_gps_file(f, delimiter=',')
    points = zip(data['lat'], data['long'])
    matches = []
    for i, point in enumerate(points):
        point, ways = query_ways_within_radius(point[0], point[1], 100)
        add_distances(ways, point)
        min_dist = sys.maxint
        min_way = None
        min_idx = None
        for way in ways:
            if way['osm_id'] < 0:
                continue
            local_min_idx, local_min_dist = min(enumerate(way['distances']), key=lambda x: x[1])
            if local_min_dist <= min_dist:
                min_dist = local_min_dist
                min_idx = local_min_idx
                min_way = way['osm_id']
        point_dict = {'point_index': i, 'point': point, 'way': min_way, 'index_of_node': min_idx}
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

def get_node_ids(matches):
    node_ids = []
    for match in matches:
        node = get_node_id(match['way'], match['index_of_node'])
        node = re.findall(r'\d+', str(node))[0]
        node_ids.append(node)
    return node_ids
 
def write_to_file(node_ids, filename):
    with open(filename, 'w') as f:
        for node in node_ids:
            f.write(node + '\n')


