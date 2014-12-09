import math
import utils

W_DIST = 0.6639
W_BT = 0.3360

# Bactrack score assigns a penalty on going back through where you came from.
# If the previous segment's start is in the next segment's endpoints, i.e.
# you're backtracking through the start point to get to the next one, return 0.
# Else return 1
def _compute_backtrack_scores(segments1, segments2):
    scores = [[] for _ in range(len(segments1))]
    for i, segment1 in enumerate(segments1):
        for segment2 in segments2:
            if segment1['direction'] is None or segment1['endpoints'] == segment2['endpoints']:
                scores[i].append(1.0)
                continue
            elif segment1['direction'] == 1:
                segment1_start = segment1['endpoints'][0]
                segment1_end = segment1['endpoints'][1]
            elif segment1['direction'] == -1:
                segment1_end = segment1['endpoints'][0]
                segment1_start = segment1['endpoints'][1]

            if segment1_start in segment2['endpoints']:
                scores[i].append(0.0)
            else:
                scores[i].append(1.0)
    return scores

def _compute_distance_scores(obs1, obs2, segments1, segments2):
    scores = [[] for _ in range(len(segments1))]
    base_dist = utils.euclidean_dist(obs1, obs2)
    for i, segment1 in enumerate(segments1):
        projection1 = utils.get_projection(segment1['endpoints'], obs1)
        for segment2 in segments2:
            projection2 = utils.get_projection(segment2['endpoints'], obs2)
            dist = utils.euclidean_dist(projection1, projection2)
            dist_diff = abs(dist - base_dist)
            scores[i].append(1.0/(1.0+dist_diff))
    return scores


def compute_transition_probabilities(obs1, obs2, segments1, segments2):
    obs1 = obs1[:2]
    obs2 = obs2[:2]
    dist_scores = _compute_distance_scores(obs1, obs2, segments1, segments2)
    backtrack_scores = _compute_backtrack_scores(segments1, segments2)
    scores = [[] for _ in range(len(dist_scores))]
    for i in range(len(dist_scores)):
        for j in range(len(dist_scores[0])):
            scores[i].append(W_DIST*dist_scores[i][j] + W_BT*backtrack_scores[i][j])
    return scores

def compute_transition_probabilities_training(obs1, obs2, segments1, segments2, t, TRANSITION_PROBS):
    obs1 = obs1[:2]
    obs2 = obs2[:2]
    dist_scores = _compute_distance_scores(obs1, obs2, segments1, segments2)
    backtrack_scores = _compute_backtrack_scores(segments1, segments2)
    scores = [[] for _ in range(len(dist_scores))]
    TRANSITION_PROBS[t] = {}
    for i in range(len(dist_scores)):
        for j in range(len(dist_scores[0])):
            segment1_str = '{0},{1}'.format(segments1[i]['way_osm_id'], segments1[i]['index_in_way'])
            segment2_str = '{0},{1}'.format(segments2[j]['way_osm_id'], segments2[j]['index_in_way'])
            if segment1_str in TRANSITION_PROBS[t]:
                TRANSITION_PROBS[t][segment1_str][segment2_str] = [dist_scores[i][j], backtrack_scores[i][j], 0]
            else:
                TRANSITION_PROBS[t][segment1_str] = {segment2_str: [dist_scores[i][j], backtrack_scores[i][j], 0]}
            scores[i].append(W_DIST*dist_scores[i][j] + W_BT*backtrack_scores[i][j])
    return scores

