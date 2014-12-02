import viterbi_training
from label_emission_probability import read_resulting_path
from db_wrapper import get_node_id

RADIUS = 30
N = 10
WINDOW = 50

def label_transition_data(filename_to_label,  **kwargs):
    radius = kwargs['radius'] if 'radius' in kwargs else RADIUS
    filename = kwargs['filename'] if 'filename' in kwargs else None
    window = kwargs['window'] if 'window' in kwargs else WINDOW
    n = kwargs['n'] if 'n' in kwargs else N


    transition_probabilities = viterbi_training.run_viterbi(filename_to_label,filename=filename, radius=radius, window=window,n=n)
    results = read_resulting_path('matched_files/Shopping2Rental_matched.csv')

    if filename is not None:
        with open(filename, 'w') as f:
            f.write('Label, Distance Score, Backtrack Score \n')
            for t, time in enumerate(transition_probabilities):
                for seg1 in transition_probabilities[t]:
                    for seg2 in transition_probabilities[t][seg1]:
                        [way2_id,way2_index] = str(seg2).split(',')
                        start_node = get_node_id(int(way2_id), int(way2_index))
                        end_node = get_node_id(int(way2_id), int(way2_index)+1)
                        node_ids=(start_node[0],end_node[0])
                        node_ids2 = (end_node[0],start_node[0])
                        if ((node_ids == results[t]) or (node_ids2 == results[t])):
                            f.write('1, '+str(transition_probabilities[t][seg1][seg2][0]) + ', ' + str(transition_probabilities[t][seg1][seg2][1]) +'\n')
                        else:
                            f.write('-1, ' +str(transition_probabilities[t][seg1][seg2][0]) + ', ' + str(transition_probabilities[t][seg1][seg2][1]) +'\n')
        return
    return
                    