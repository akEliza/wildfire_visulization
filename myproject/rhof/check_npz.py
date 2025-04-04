import numpy as np

# load .npz 
file_path = r"E:\MM804\project\preprocessed_dataset\mountain_backcurve40\output.1000.npz"
data = np.load(file_path)

# check keys
print("Keys in npz file:", data.files)

# check each key detail
for key in data.files:
    print(f"Key: {key}, Shape: {data[key].shape}, Dtype: {data[key].dtype}")
