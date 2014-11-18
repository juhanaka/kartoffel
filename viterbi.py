import utils
from emission_probability import compute_emission_probabilities
from transition_probability import compute_transition_probabilities

RADIUS = 20
N = 10


def viterbi(observations, **kwargs):
    radius = kwargs['radius'] if 'radius' in kwargs else RADIUS
    filename = kwargs['filename'] if 'filename' in kwargs else None
    n = kwargs['n'] if 'n' in kwargs else N

    value_table = []
    backtrack_table = []
    value_table.append(compute_emission_probabilities(observations[0],
                                                      radius, n))
    backtrack_table.append(compute_emission_probabilities(observations[0],
                                                          radius, n))
    
    for t, obs in enumerate(observations):
        if t == 0:
            continue
        emission_probabilities = compute_emission_probabilities(obs, radius, n)
        transition_probabilities = compute_transition_probabilities(value_table[t-1],
                                                                    emission_probabilities)
        value_table.append([])
        backtrack_table.append([])
        for i, segment_i_at_t in enumerate(emission_probabilities):
            candidates = []
            for j, segment_j_at_tminus1 in enumerate(value_table[t-1]):
                candidates.append(segment_j_at_tminus1[3] * transition_probabilities[j][i] * emission_probabilities[i][3])
            idx, value = max(enumerate(candidates), key=lambda x: x[1])
            value_table[t].append((segment_i_at_t[0], segment_i_at_t[1], segment_i_at_t[2], value))
            backtrack_table[t].append((segment_i_at_t[0], segment_i_at_t[1], segment_i_at_t[2], idx))
    last_idx, last_val = max(enumerate(value_table[t]), key=lambda x: x[1][3])
    idx = last_idx
    result_sequence = []
    for t in range(len(observations))[::-1]:
        cur =  backtrack_table[t][idx]
        idx = backtrack_table[t][idx][3]
        result_sequence.append(cur)
    node_ids = utils.get_node_ids(result_sequence[::-1])
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
            observations.append((float(line[3]), float(line[4]), float(line[7])))
    start = kwargs.pop('start') if 'start' in kwargs else 0
    end = kwargs.pop('end') if 'end' in kwargs else len(observations)
    return viterbi(observations[start:end], **kwargs)
