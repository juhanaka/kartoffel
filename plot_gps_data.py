# Plots Sensor Log gps observations as a vector field
# Command line arguments: filepath to Sensor Log csv file

import sys
import numpy as np
import matplotlib.pyplot as plt
import math


DELIMITER = ';'

# Read file and return contents as a dict: {'measure_name': [value1, value2,...]}
# Values are not converted but are raw strings.
def read_gps_file(f, **kwargs):
    delimiter = kwargs['delimiter'] if 'delimiter' in kwargs else DELIMITER
    headers = f.readline().split(delimiter)
    headers = [header.strip() for header in headers]
    n_fields = len(headers)
    data = [[] for _ in range(n_fields)]
    for i, line in enumerate(f):
        for j, el in enumerate(line.split(delimiter)):
            data[j].append(el)
    data = {headers[i]: [d for d in data[i]] for i in range(n_fields)}
    return data


# Displays a vector field plot of GPS and sensor observations.
# Tail position of a vector == long, lat
# Vector length == speed
# Vector direction == course
def plot_vector_field(data):
    lat = np.array([float(l) for l in data['lat']]) 
    lon = np.array([float(l) for l in data['long']]) 
    # need angle conversion. Original angle is 0 north 90 east 180 south 270 west.
    # converting to north -90, east 0, and so on
    course = [math.radians(-float(c)+90) if float(c) >=0 else None for c in data['course']]
    speed = [float(s) if float(s)>=0 else 0.0 for s in data['speed']]
    course_x = [math.cos(c)*speed[i] for i, c in enumerate(course)]
    course_y = [math.sin(c)*speed[i] for i, c in enumerate(course)]
    course_x = np.array(course_x)
    course_y = np.array(course_y)
    plt.figure()
    plt.quiver(lon,lat, course_x, course_y, scale=500)
    plt.show()
 

# Display a correlation coefficient matrix for selected features.
def covariances(data):
    variable_names  = ['speed','course','accelerationX',
                       'accelerationY','HeadingX','HeadingY',
                       'TrueHeading','MagneticHeading',
                       'motionUserAccelerationX','motionUserAccelerationY']
    variable_list = [map(float, data[key]) for key in variable_names]
    variables = np.array(variable_list)
    cov_matrix = np.corrcoef(variables)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    cax = ax.matshow(cov_matrix)
    plt.xticks(range(len(variable_names)), variable_names, rotation=90)
    plt.yticks(range(len(variable_names)), variable_names)
    fig.colorbar(cax)
    plt.show()


def main(argv):
    if len(argv) != 2:
        raise Exception('args: filepath')
    with open(argv[1]) as f:
        data = read_gps_file(f)
    covariances(data)
    plot_vector_field(data)

if __name__ == '__main__':
    main(sys.argv)
