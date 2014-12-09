import utils
import db_wrapper
from emission_probability import compute_emission_probabilities
from transition_probability import compute_transition_probabilities

RADIUS = 50
N = 10
WAY_N_LIMIT = 5

def viterbi(observations, projection, radius, way_n_limit):
    segments_table = []
    probabilities_table = []
    segments, emission_probabilities, point = compute_emission_probabilities(observations[0],
                                                                             radius,
                                                                             way_n_limit)
    for i, segment in enumerate(segments):
        segments[i]['previous'] = None 
        segments[i]['direction'] = None
    segments_table.append(segments)
    probabilities_table.append(emission_probabilities)
    # Store the mercator projected observations for further use
    mercator_points = []

    for t, obs in enumerate(observations):
        if t == 0:
            continue
        previous_point = point
        segments, emission_probabilities, point = compute_emission_probabilities(obs,
                                                                                 radius,
                                                                                 way_n_limit)
        mercator_points.append(point)
        transition_probabilities = compute_transition_probabilities(previous_point,
                                                                    point,
                                                                    segments_table[t-1],
                                                                    segments)
        segments_table.append([])
        probabilities_table.append([])
        for i, emission_probability in enumerate(emission_probabilities):
            candidates = []
            for j, previous_probability in enumerate(probabilities_table[t-1]):
                candidates.append(
                    previous_probability * transition_probabilities[j][i] * emission_probability
                )
            idx, highest_probability = max(enumerate(candidates), key=lambda x: x[1])
            probabilities_table[t].append(highest_probability)
            segments[i]['previous'] = idx
            segments[i]['direction'] = utils.calculate_direction(segments_table[t-1][idx], segments[i])
            segments_table[t].append(segments[i])
    last_idx, last_val = max(enumerate(probabilities_table[t]), key=lambda x: x[1])
    idx = last_idx
    result = []
    for _t in range(len(observations))[::-1]:
        cur =  segments_table[_t][idx]
        result.append(cur)
        if _t != 0:
            idx = cur['previous']
    probabilities_table = [[1]]
    segments_table = [[segments_table[t][last_idx]]]
    if projection:
        return result[::-1], mercator_points
    node_ids = utils.get_node_ids(result[::-1])
    return node_ids

def run_viterbi(observations_filename, **kwargs):
    window = kwargs['window'] if 'window' in kwargs else WINDOW
    start = kwargs['start'] if 'start' in kwargs else None
    end = kwargs['end'] if 'end' in kwargs else None
    buf = kwargs['buf'] if 'buf' in kwargs else 0
    projection = kwargs['projection'] if 'projection' in kwargs else None
    radius = kwargs['radius'] if 'radius' in kwargs else RADIUS
    way_n_limit = kwargs['way_n_limit'] if 'way_n_limit' in kwargs else WAY_N_LIMIT

    observations = []
    results = []
    with open(observations_filename) as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            line = line.split(',')
            observations.append((float(line[3]), float(line[4]), float(line[7]), float(line[6])))
    if start is not None and end is not None:
        observations = observations[start:end]
    if projection is None:
        return run_viterbi_nodes(observations, window, buf, radius, way_n_limit)
    return run_viterbi_projection(observations, window, buf, radius, way_n_limit)

# Run viterbi and get node ids of segment start and endpoint
def run_viterbi_nodes(observations, window, buf, radius, way_n_limit):
    results = []
    for i in range(len(observations) - window):
        if i == 0:
            results += viterbi(observations[i:i+window-buf], False)
        else:
            results.append(viterbi(observations[i:i+window], False)[-(1+buf)])
    return results

# Run viterbi and get coordinates of point-to-linesegment projection of the observation to the predicted road segment
def run_viterbi_projection(observations, window, buf, radius, way_n_limit):
    results = []
    for i in range(len(observations) - window):
        if i == 0:
            segments, mercator_points = viterbi(observations[i:i+window-buf], True)
            projected_points = [utils.get_projection(segments[j]['endpoints'], observations[j][0:2]) for j in range(len(mercator_points))]
            latlong_proj_points = [db_wrapper.transform_point_merc_latlong(point) for point in projected_points]
            results += projected_points
        else:
            segments, mercator_points = viterbi(observations[i:i+window], True)
            projected_point = utils.get_projection(segments[-(1+buf)]['endpoints'], mercator_points[-(1+buf)][0:2])
            results.append(db_wrapper.transform_point_merc_latlong(projected_point))
    write_points_to_file(results)
    
def check_errors(predictions, gtruth):
    predictions = [(int(x[0]), int(x[1])) for x in predictions]
    gtruth = [(int(x[0]), int(x[1])) for x in gtruth]
    errors = [1 if predictions[_][::-1] != gtruth[_] and predictions[_] != gtruth[_] else 0 for _ in range(len(predictions))]
    return float(sum(errors))/len(errors)

def write_points_to_file(result_sequence):
    with open('result_nodes.csv', 'w') as resf:
        for i, point in enumerate(result_sequence):
            resf.write('{0},{1}\n'.format(*point))

