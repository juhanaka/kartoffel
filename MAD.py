import numpy as np
def MAD(proj):
	#Mean Absolute Deviation estimate
	#Inputs: projections to ways of (UKF) GPS proj; nx1 vector
	#Outputs: Gaussian error estimate
	#Gaussian K=1.4826
	K=1.4826
	return K*np.median(abs(np.subtract(proj,np.median(proj))))
