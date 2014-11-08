import math

# Takes an array of ways, checks which nodes of the ways are within 'radius' meters of 'base_point'
# Returns array of dicts, where each dict has the osm_id of the way, and the indices of the nodes
# within the radius.
def indices_of_nodes_within_radius(base_point, ways, radius):
    results = []
    for way in ways:
        indices = [point_idx for point_idx, point in enumerate(way['points']) if euclidean_dist(point, base_point) <= radius]
        nodes = {'osm_id': way['osm_id'], 'indices': indices}
        results.append(nodes)
    return results

def test(lat, lon, radius):
    point, ways = query_ways_within_radius(lat, lon, radius)
    print indices_of_nodes_within_radius(point, ways, radius)


def euclidean_dist(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


def linestring_to_point_array(linestring):
    # Linestring is in format: 'LINESTRING(lon1 lat1, lon2 lat2, ... , )'
    # First slice all unnecessary things off the string
    linestring = linestring[11:-1]
    # split the string into points
    points = linestring.split(',')
    # split to a tuple of long and lat
    points = [tuple(map(float, p.split())) for p in points]
    points = tuple(points)  # Order is important, so make it tuple
    return points
    

