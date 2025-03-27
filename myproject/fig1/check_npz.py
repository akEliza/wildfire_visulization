import numpy as np

# 读取 .npz 文件
file_path = r"E:\MM804\project\preprocessed_dataset\mountain_backcurve40\output.1000.npz"
data = np.load(file_path)

# 查看文件中的所有数组键
print("Keys in npz file:", data.files)

# 逐个查看每个键对应的数据形状和类型
for key in data.files:
    print(f"Key: {key}, Shape: {data[key].shape}, Dtype: {data[key].dtype}")
