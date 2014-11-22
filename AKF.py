from __future__ import division
from pykalman import AdditiveUnscentedKalmanFilter
import numpy as np
import numpy.linalg as la

def AFK(y):
	#Inputs: GPS coordinates; nx2 vector
	#Outputs: smoothed states; nx2 vector

	def TransObsFunc(state): #Same functions for simplified filter
    return state

	alpha = 0.8 #Tuning parameter for smoothness
	akf = AdditiveUnscentedKalmanFilter(
	    TransObsFunc, TransObsFunc,
	    np.eye(2)*alpha, np.eye(2),
	    [y[0,0], y[0,1]], np.eye(2))
	return akf.filter(y)[0]
