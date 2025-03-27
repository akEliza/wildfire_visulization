import vtk
import numpy as np
import glob
import os
import matplotlib.pyplot as plt

# 设定 VTS 文件路径
vts_files = sorted(glob.glob("E:\\MM804\\project\\SciVis2022_data\\mountain_backcurve40\\*.vts"))

# 读取第一个时间步，获取网格尺寸
reader = vtk.vtkXMLStructuredGridReader()
reader.SetFileName(vts_files[0])
reader.Update()
data = reader.GetOutput()

# 获取完整网格尺寸 (nx, ny, nz)
dims = data.GetDimensions()
nx, ny, nz = dims  # VTK 格式一般是 (X, Y, Z)

# 提取 `rhof_1` 并 reshape 成 3D 数组
rhof_1_full = np.array(data.GetPointData().GetArray("rhof_1")).reshape((nz, ny, nx))  # 注意顺序
# 计算 rhof_1 在不同 z 层的总量
z_sums = np.sum(rhof_1_full, axis=(1, 2))  # 沿 x, y 方向求和
best_z = np.argmax(z_sums)  # 找到燃烧最强烈的 z 层

print(f"🔥 火势最强的高度层 z = {best_z}")
