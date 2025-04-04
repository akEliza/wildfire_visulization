import numpy as np

data = np.load("burn_time_backcurve40.npy")
# print(data.shape) #(500, 600)
# filter non-nan value
non_nan_values = data[~np.isnan(data)]

print(non_nan_values.shape)
