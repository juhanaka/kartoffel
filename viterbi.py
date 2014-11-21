import utils
from emission_probability import compute_emission_probabilities
from transition_probability import compute_transition_probabilities

RADIUS = 20
N = 10
WINDOW = 50

# Viterbi algorithm
# kwargs: filename to write in, radius to look segments from, n max number of states considered at time t
# window size
def viterbi(observations, **kwargs):
    radius = kwargs['radius'] if 'radius' in kwargs else RADIUS
    filename = kwargs['filename'] if 'filename' in kwargs else None
    window = kwargs['window'] if 'window' in kwargs else WINDOW
    n = kwargs['n'] if 'n' in kwargs else N
    return_gps = kwargs['return_gps'] if 'return_gps' in kwargs else False

    print 'Running viterbi. window size: {0}, max states {1}, max radius {2}'.format(window,n,radius)

    result_sequence = []
    segments_table = []
    probabilities_table = []
    segments, emission_probabilities, point = compute_emission_probabilities(observations[0],radius, n)
    for i, segment in enumerate(segments):
        segments[i]['previous'] = None 
        segments[i]['direction'] = None
    segments_table.append(segments)
    probabilities_table.append(emission_probabilities)
    for window_idx in range(len(observations) / window + 1):
        current_obs = observations[window_idx*window:(window_idx+1)*window]
        if (len(current_obs) == 0):
            break
        for t, obs in enumerate(current_obs):
            if t == 0:
                continue
            previous_point = point
            segments, emission_probabilities, point = compute_emission_probabilities(obs, radius, n)
            transition_probabilities = compute_transition_probabilities(previous_point,
                                                                        point,
                                                                        segments_table[t-1],
                                                                        segments)
            segments_table.append([])
            probabilities_table.append([])
            for i, emission_probability in enumerate(emission_probabilities):
                candidates = []
                for j, previous_probability in enumerate(probabilities_table[t-1]):
                    candidates.append(previous_probability * transition_probabilities[j][i] * emission_probability)
                idx, highest_probability = max(enumerate(candidates), key=lambda x: x[1])
                probabilities_table[t].append(highest_probability)
                segments[i]['previous'] = idx
                segments[i]['direction'] = utils.calculate_direction(segments_table[t-1][idx], segments[i])
                segments_table[t].append(segments[i])
        last_idx, last_val = max(enumerate(probabilities_table[t]), key=lambda x: x[1])
        idx = last_idx
        intermediate_result = []
        for _t in range(len(current_obs))[::-1]:
            cur =  segments_table[_t][idx]
            intermediate_result.append(cur)
            if _t != 0:
                idx = cur['previous']
        probabilities_table = [[1]]
        segments_table = [[segments_table[t][last_idx]]]
        result_sequence = result_sequence + intermediate_result[::-1]
    if return_gps:
        node_gps = utils.get_node_gps_points(result_sequence)
        start_points = ['{0},{1}'.format(point[0][0], point[0][1]) for point in node_gps]
        end_points = ['{0},{1}'.format(point[1][0], point[1][1]) for point in node_gps]
        with open('result_nodes.csv', 'w') as resf:
            for i, point in enumerate(start_points):
                resf.write(point+'\n')
                resf.write(end_points[i]+'\n')
        return
    node_ids = utils.get_node_ids(result_sequence)
    if filename is not None:
        utils.write_to_file(node_ids, filename)
        return
    return node_ids

def run_viterbi(observations_filename, **kwargs):
    observations = []
    with open(observations_filename) as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            line = line.split(',')
            observations.append((float(line[3]), float(line[4]), float(line[7]), float(line[6])))
    start = kwargs.pop('start') if 'start' in kwargs else 0
    end = kwargs.pop('end') if 'end' in kwargs else len(observations)
    return viterbi(observations[start:end], **kwargs)



