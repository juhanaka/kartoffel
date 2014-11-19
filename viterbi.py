import utils
from emission_probability import compute_emission_probabilities
from transition_probability import compute_transition_probabilities

RADIUS = 20
N = 10
WINDOW = 50


def viterbi(observations, **kwargs):
    radius = kwargs['radius'] if 'radius' in kwargs else RADIUS
    filename = kwargs['filename'] if 'filename' in kwargs else None
    window = kwargs['window'] if 'window' in kwargs else WINDOW
    n = kwargs['n'] if 'n' in kwargs else N

    result_sequence = []
    value_table = []
    backtrack_table = []
    value_table.append(compute_emission_probabilities(observations[0],
                                                      radius, n))
    backtrack_table.append(compute_emission_probabilities(observations[0],
                                                          radius, n))
    for window_idx in range(len(observations) / window + 1):
        current_obs = observations[window_idx*window:(window_idx+1)*window]
        if (len(current_obs) == 0):
            break
        for t, obs in enumerate(current_obs):
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
        intermediate_result = []
        for _t in range(len(current_obs))[::-1]:
            cur =  backtrack_table[_t][idx]
            idx = backtrack_table[_t][idx][3]
            intermediate_result.append(cur)
        value_table = [[value_table[t][last_idx]]]
        backtrack_table = [[backtrack_table[t][last_idx]]]
        result_sequence = result_sequence + intermediate_result[::-1]
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
            observations.append((float(line[3]), float(line[4]), float(line[7])))
    start = kwargs.pop('start') if 'start' in kwargs else 0
    end = kwargs.pop('end') if 'end' in kwargs else len(observations)
    return viterbi(observations[start:end], **kwargs)


