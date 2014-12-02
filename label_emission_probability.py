import utils
import viterbi
from db_wrapper import get_node_id
import emission_probability

RADIUS = 20
N = 10
WINDOW = 50

# Function to read resulting file
def read_resulting_path(resulting_path_filename):
    results=[]
    with open(resulting_path_filename) as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            line = line.split(',')
            results.append((float(line[0]), float(line[1])))
        return results

# Function to read the observations
def read_observations(filename):
    observations = []
    with open(filename) as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            line = line.split(',')
            observations.append((float(line[3]), float(line[4]), float(line[7]), float(line[6])))
    return observations

# Function to label emission probability training data
def label_emission_data(file_to_label, **kwargs):
    radius = kwargs['radius'] if 'radius' in kwargs else RADIUS
    filename = kwargs['filename'] if 'filename' in kwargs else None
    window = kwargs['window'] if 'window' in kwargs else WINDOW
    n = kwargs['n'] if 'n' in kwargs else N

    tmpfile = 'results_file'
    viterbi.run_viterbi(file_to_label,filename=tmpfile, radius=radius, window=window,n=n)
    observations = read_observations(file_to_label)
    results = read_resulting_path(tmpfile)
    labeled =[]

    for t, obs in enumerate(observations):
        possible_segments, prob, point = emission_probability.compute_emission_probabilities(obs,radius,n)   
        for i,seg in enumerate(possible_segments):
            start_node = get_node_id(seg['way_osm_id'],seg['index_in_way'])
            end_node = get_node_id(seg['way_osm_id'],seg['index_in_way']+1)
            node_ids=(start_node[0],end_node[0])
            node_ids2 = (end_node[0],start_node[0])
            if ((node_ids == results[t]) or (node_ids2 == results[t])):
                labeled.append((node_ids,seg['distance_score'],seg['tangent_score'], 1))
            else:
                labeled.append((node_ids,seg['distance_score'],seg['tangent_score'], -1))
    if filename is not None:
        with open(filename, 'w') as f:
            f.write('Label, Distance Score, Tangent Score \n')
            for l in labeled:
                f.write(str(l[3]) + ', ' + str(l[1]) +', '+str(l[2]) + '\n')
        return
    return labeled

