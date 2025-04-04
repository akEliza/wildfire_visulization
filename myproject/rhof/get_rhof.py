import vtk
import numpy as np
import glob
import os
import matplotlib.pyplot as plt

# Set the path to VTS files
vts_files = sorted(glob.glob("F:\\Firetec\\headcurve320\\*.vts"))

# Read the first timestep to get grid dimensions
reader = vtk.vtkXMLStructuredGridReader()
reader.SetFileName(vts_files[0])
reader.Update()
data = reader.GetOutput()

# Get full grid dimensions (nx, ny, nz)
dims = data.GetDimensions()
nx, ny, nz = dims  # VTK format is typically (X, Y, Z)

# Extract `rhof_1` and reshape into a 3D array
rhof_1_full = np.array(data.GetPointData().GetArray("rhof_1")).reshape((nz, ny, nx))  # Note the order

# Select the z = 0 layer to get 2D data
initial_rhof_1 = rhof_1_full[0, :, :]

# Initialize burn time matrix
burn_time = np.full((ny, nx), np.nan)

# Set burn threshold (90% of initial value)
burn_threshold = 0.9 * initial_rhof_1

# Loop through all timesteps and find the first burn time
for t, vts_file in enumerate(vts_files):
    reader.SetFileName(vts_file)
    reader.Update()
    data = reader.GetOutput()

    # Read `rhof_1` and reshape into 3D
    rhof_1_full = np.array(data.GetPointData().GetArray("rhof_1")).reshape((nz, ny, nx))

    # Take z = 0 layer
    rhof_1 = rhof_1_full[0, :, :]

    # Compute when burning starts
    burning_now = (rhof_1 < burn_threshold) & np.isnan(burn_time)
    burn_time[burning_now] = t

# Handle NaN values (unburned voxels are set to the max timestep)
burn_time = np.nan_to_num(burn_time, nan=np.max(burn_time))

# Save the data
np.save("fig1/burn_time_headcurve320.npy", burn_time)
