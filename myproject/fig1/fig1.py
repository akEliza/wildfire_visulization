import numpy as np
from matplotlib import pyplot as plt
import matplotlib.cm as cm
from scipy.ndimage import generic_filter

# 用 3x3 邻域平均替换 NaN 值（保留非 NaN）
def nanmean_filter(values):
    center = values[len(values)//2]
    if np.isnan(center):
        return np.nanmean(values)
    else:
        return center

# 读取数据
burn_time = np.load(r"E:\MM804\project\myproject\fig1\burn_time_headcurve320.npy")

# 获取数组的 shape（高度、宽度）
height, width = burn_time.shape

# 创建布尔掩码：找到值为 34 的位置
mask_34 = (burn_time == 34)

# 创建矩形区域的掩码（注意 y 是行，x 是列）
y_indices, x_indices = np.indices(burn_time.shape)
inside_box = (x_indices >= 90) & (x_indices <= 320) & (y_indices >= 180) & (y_indices <= 310)

# 找出不在区域内、且值为 34 的元素
# mask_34_outside = mask_34 & (~inside_box)

# 替换这些值为 nan
burn_time[mask_34] = np.nan
# 应用模糊滤波，填补空白区域
burn_time = generic_filter(burn_time, nanmean_filter, size=3)
burn_time = generic_filter(burn_time, nanmean_filter, size=3)
burn_time = generic_filter(burn_time, nanmean_filter, size=3)
# 设置颜色映射，NaN 显示为白色
cmap = plt.colormaps["viridis"].copy()
cmap.set_bad(color='white')

plt.figure(figsize=(6, 6))
plt.imshow(burn_time, cmap=cmap, origin="lower", interpolation="nearest")
plt.colorbar(label="Time Step")
plt.xlabel("x")
plt.ylabel("y")
plt.title("Fire Spread for Headcurve 320")
plt.savefig(r"E:\MM804\project\myproject\fig1\output\headcurve320.png", dpi=300)
plt.show()

"""
import numpy as np
import matplotlib.pyplot as plt

# 读取数据
burn_time = np.load(r"E:\MM804\project\myproject\fig1\burn_time_headcurve320.npy")

# 确保背景区域（NaN 或者非火焰区域）不会被绘制
burn_time_cleaned = np.where(np.isnan(burn_time), np.nan, burn_time)  # 确保 NaN 仍然是 NaN
burn_time_cleaned[burn_time_cleaned <= 0] = np.nan  # 把 0 或者负值也设为 NaN，防止杂色

# 复制 colormap 并设置 NaN 为透明
cmap = plt.cm.viridis.copy()
cmap.set_bad(color='white', alpha=0)  # 让 NaN 变透明

# 可视化
plt.figure(figsize=(8, 6))
plt.imshow(burn_time_cleaned, cmap=cmap, origin="lower", interpolation="none")  # 关闭插值
plt.colorbar(label="Time Step")
plt.xlabel("x")
plt.ylabel("y")
plt.title("Fire Spread for Headcurve 320")

# 保存和显示
plt.savefig(r"E:\MM804\project\myproject\fig1\output\headcurve320.png", dpi=300)
plt.show()
"""