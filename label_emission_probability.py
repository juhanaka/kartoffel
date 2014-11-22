import utils
import viterbi
from db_wrapper import query_ways_within_radius
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

# Function to label emission probability training data
def label_emission_data(file_to_label, **kwargs):

    radius = kwargs['radius'] if 'radius' in kwargs else RADIUS
    filename = kwargs['filename'] if 'filename' in kwargs else None
    window = kwargs['window'] if 'window' in kwargs else WINDOW
    n = kwargs['n'] if 'n' in kwargs else N
    tmpfile = 'results_file'
    viterbi.run_viterbi(file_to_label,filename=tmpfile, radius=radius, window=window,n=n)
    observations = read_observations(file_to_label)
    results = read_resulting_path('results_file')
    labeled =[]

    for t, obs in enumerate(observations):
        possible_segments=emission_probability.compute_emission_probabilities(obs,radius,n)
        for seg in possible_segments:
            node_ids=utils.get_node_ids(seg[2])
            if node_ids == results[t]:
                labeled.append((seg[4],seg[5], 1))
            else:
                labeled.append((seg[4],seg[5], -1))
    if filename is not None:
        with open(filename, 'w') as f:
            f.write('Distance Score, Tangent Score, Result\n')
            for l in labeled:
                f.write(l[0] + ', ' + l[1] +', '+l[2]+ '\n')
                return
    return labeled

