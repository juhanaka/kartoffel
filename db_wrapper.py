import psycopg2
import math
import re

DBNAME = 'osm'
LINE_TABLE = 'planet_osm_line'


def connect():
    try:
        conn = psycopg2.connect("dbname='"+DBNAME+"' user='juhanakangaspunta' host='localhost'")
    except:
        print 'Unable to connect to database ' + DBNAME
    return conn.cursor()

# Query the database for ways that have nodes within 'radius' meters from the point defined
# by 'lat' and 'lon'
# Returns:
# 1) the point defined by 'lat' and 'lon' in mercator projection
# 2) An array containing dictionaries of all the ways that are within the radius.
#    The dictionary contains the osm_id of the way and a tuple of node-tuples in mercator projection.
def query_ways_within_radius(lat, lon, radius):
    cur = connect()
    # PostGIS format of a point. Long/Lat as this stage:
    pointstr = "'POINT({0} {1})'".format(lon, lat) 
    # PostGIS function to generate a point from text:
    pointgenstr = 'ST_PointFromText({0}, {1})'.format(pointstr, 4326) 
    # PostGIS function to transform point from lat/long to mercator:
    point_in_merc_str = 'ST_Transform({0}, {1})'.format(pointgenstr, 900913) 
    # Build query string from the pieces:
    qstring = """SELECT ST_AsText({1}), osm_id, ST_AsText(way)
              FROM {0} WHERE ST_DWithin(way, {1}, {2}) = true""".format(LINE_TABLE,
                                                                        point_in_merc_str,
                                                                        radius)
    cur.execute(qstring)
    rows = cur.fetchall()
    # First cell of each row is the point in mercator projection as text.
    # Making the PostGIS database do the lat/long -> mercator conversion.
    # The point is in form 'POINT(long, lat)' so extract the floating point coordinates
    # with regex
    point_in_merc = re.findall(r"[-+]?\d*\.\d+|\d+", rows[0][0])
    point_in_merc = [float(d) for d in point_in_merc]
    ways = []
    for row in rows:
        # second element of each row is the osm_id of the way
        osm_id = row[1]
        # third element of each row is the linestring of the way as a string.
        # call linestring_to_point_array to convert the string into an array of points
        point_array = linestring_to_point_array(row[2])
        way = {'osm_id': osm_id, 'points': point_array}
        ways.append(way)
    return point_in_merc, ways 


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
    
