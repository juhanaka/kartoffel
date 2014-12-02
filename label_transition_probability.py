import viterbi_training

RADIUS = 30
N = 10
WINDOW = 50

def label_transition_data(filename_to_label,  **kwargs):
    radius = kwargs['radius'] if 'radius' in kwargs else RADIUS
    filename = kwargs['filename'] if 'filename' in kwargs else None
    window = kwargs['window'] if 'window' in kwargs else WINDOW
    n = kwargs['n'] if 'n' in kwargs else N


    transition_probabilities = viterbi_training.run_viterbi(filename_to_label,filename=filename, radius=radius, window=window,n=n)
    

    if filename is not None:
        with open(filename, 'w') as f:
            f.write('Label, Distance Score, Backtrack Score \n')
            for t, time in enumerate(transition_probabilities):
                for seg1 in transition_probabilities[t]:
                    for seg2 in transition_probabilities[t][seg1]:
                        if (transition_probabilities[t][seg1][seg2][2]==0 ):
                            f.write('-1, '+str(transition_probabilities[t][seg1][seg2][0]) + ', ' + str(transition_probabilities[t][seg1][seg2][1]) +','+str(seg1)+','+str(seg2)+ '\n')
                        else:
                            f.write('1, ' +str(transition_probabilities[t][seg1][seg2][0]) + ', ' + str(transition_probabilities[t][seg1][seg2][1]) +','+str(seg1)+','+str(seg2)+ '\n')
        return
    return
                    