import numpy as np
from matplotlib import pyplot as plt
import matplotlib.cm as cm
from scipy.ndimage import generic_filter

# Replace NaN values using a 3x3 neighborhood mean (preserve non-NaN values)
def nanmean_filter(values):
    center = values[len(values)//2]
    if np.isnan(center):
        return np.nanmean(values)
    else:
        return center

# Load data
burn_time = np.load(r"E:\MM804\project\myproject\fig1\burn_time_headcurve320.npy")

# Get array shape (height, width)
height, width = burn_time.shape

# Create a boolean mask to find locations where the value is 34
mask_34 = (burn_time == 34)

# Create a mask for the rectangular region (note: y is row index, x is column index)
y_indices, x_indices = np.indices(burn_time.shape)
inside_box = (x_indices >= 90) & (x_indices <= 320) & (y_indices >= 180) & (y_indices <= 310)

# Find elements with value 34 that are outside the specified region
# mask_34_outside = mask_34 & (~inside_box)

# Replace these values with NaN
burn_time[mask_34] = np.nan

# Apply smoothing filter to fill NaN regions
burn_time = generic_filter(burn_time, nanmean_filter, size=3)
burn_time = generic_filter(burn_time, nanmean_filter, size=3)
burn_time = generic_filter(burn_time, nanmean_filter, size=3)

# Set colormap, displaying NaN values as white
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
