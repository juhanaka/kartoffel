import sys
import numpy as np
import matplotlib.pyplot as plt
import math


DELIMITER = ';'


def read_gps_file(f):
    headers = f.readline().split(DELIMITER)
    headers = [header.strip() for header in headers]
    n_fields = len(headers)
    data = [[] for _ in range(n_fields)]
    for i, line in enumerate(f):
        for j, el in enumerate(line.split(DELIMITER)):
            data[j].append(el)
    data = {headers[i]: [d for d in data[i]] for i in range(n_fields)}
    return data

def plot_vector_field(data):
    lat = np.array([float(l) for l in data['lat']]) 
    lon = np.array([float(l) for l in data['long']]) 
    course = [math.radians(-float(c)+90) if float(c) >=0 else None for c in data['course']]
    speed = [float(s) if float(s)>=0 else 0.0 for s in data['speed']]
    course_x = [math.cos(c)*speed[i] for i, c in enumerate(course)]
    course_y = [math.sin(c)*speed[i] for i, c in enumerate(course)]
    course_x = np.array(course_x)
    course_y = np.array(course_y)
    plt.figure()
    plt.quiver(lon,lat, course_x, course_y, scale=600)
    plt.show()
    

def main(argv):
    if len(argv) != 2:
        raise Exception('args: filepath')
    with open(argv[1]) as f:
        data = read_gps_file(f)
    plot_vector_field(data)

if __name__ == '__main__':
    main(sys.argv)
