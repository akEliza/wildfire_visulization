import vtk
import numpy as np
import glob
import os
import matplotlib.pyplot as plt

# 设定 VTS 文件路径
vts_files = sorted(glob.glob("F:\\Firetec\\headcurve320\\*.vts"))

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

# 选择 z=0 层，得到 2D 数据
initial_rhof_1 = rhof_1_full[0, :, :]

# 初始化燃烧时间步矩阵
burn_time = np.full((ny, nx), np.nan)

# 设定燃烧阈值（90% 初始值）
burn_threshold = 0.9 * initial_rhof_1

# 遍历所有时间步，找到首次燃烧的时间
for t, vts_file in enumerate(vts_files):
    reader.SetFileName(vts_file)
    reader.Update()
    data = reader.GetOutput()

    # 读取 `rhof_1` 并 reshape 成 3D
    rhof_1_full = np.array(data.GetPointData().GetArray("rhof_1")).reshape((nz, ny, nx))

    # 取 z=0 层
    rhof_1 = rhof_1_full[0, :, :]

    # 计算燃烧开始的时间步
    burning_now = (rhof_1 < burn_threshold) & np.isnan(burn_time)
    burn_time[burning_now] = t

# 处理 NaN 值（未燃烧的体素设为最大时间步）
burn_time = np.nan_to_num(burn_time, nan=np.max(burn_time))

# 保存数据
np.save("fig1/burn_time_headcurve320.npy", burn_time)
