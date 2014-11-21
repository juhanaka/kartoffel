import math
import utils

W_DIST = 1.0
W_BT = 0.0

                
def _compute_backtrack_scores(segments1, segments2):
    scores = [[] for _ in range(len(segments1))]
    for i, segment1 in enumerate(segments1):
        for segment2 in segments2:
            scores[i].append(1)
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
            scores[i].append((1.0/(1.0+dist_diff))**(1/2))
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

