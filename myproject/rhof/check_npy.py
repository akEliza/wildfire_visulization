import numpy as np

data = np.load("burn_time_backcurve40.npy")
# print(data.shape) #(500, 600)
# 筛选出非 NaN 值
non_nan_values = data[~np.isnan(data)]

# 打印结果
print(non_nan_values.shape)
