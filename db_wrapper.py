import psycopg2
import re
import utils


DBNAME = 'gis'#'osm_slim'
USERNAME='toto2'#'juhanakangaspunta'
LINE_TABLE = 'planet_osm_line'


def connect():
    try:
        conn = psycopg2.connect("dbname='"+DBNAME+"' user='"+USERNAME+"' host='localhost'")
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
              FROM {0} WHERE ST_DWithin(way, {1}, {2})""".format(LINE_TABLE,
                                                                        point_in_merc_str,
                                                                        radius)
    cur.execute(qstring)
    rows = cur.fetchall()
    # First cell of each row is the point in mercator projection as text.
    # Making the PostGIS database do the lat/long -> mercator conversion.
    # The point is in form 'POINT(long, lat)' so extract the floating point coordinates
    # with regex
    if not rows:
        return None, None
    point_in_merc = re.findall(r"[-+]?\d*\.\d+|\d+", rows[0][0])
    point_in_merc = [float(d) for d in point_in_merc]
    ways = []
    for row in rows:
        # second element of each row is the osm_id of the way
        osm_id = row[1]
        if osm_id < 0:
            continue
        # third element of each row is the linestring of the way as a string.
        # call linestring_to_point_array to convert the string into an array of points
        point_array = utils.linestring_to_point_array(row[2])
        way = {'osm_id': osm_id, 'points': point_array}
        ways.append(way)
    return point_in_merc, ways 

def get_node_id(way_id, index):
    cur = connect()
    qstring = 'SELECT nodes[{0}] FROM planet_osm_ways WHERE id = {1}'.format(index+1, way_id)
    cur.execute(qstring)
    rows = cur.fetchall()
    if not len(rows):
        print way_id, index
    return rows[0] if len(rows) else None


