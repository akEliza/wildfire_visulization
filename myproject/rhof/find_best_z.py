import vtk
import numpy as np
import glob
import os
import matplotlib.pyplot as plt

# Set the path to VTS files
vts_files = sorted(glob.glob("E:\\MM804\\project\\SciVis2022_data\\mountain_backcurve40\\*.vts"))

# Read the first timestep to get the grid dimensions
reader = vtk.vtkXMLStructuredGridReader()
reader.SetFileName(vts_files[0])
reader.Update()
data = reader.GetOutput()

# Get the full grid dimensions (nx, ny, nz)
dims = data.GetDimensions()
nx, ny, nz = dims  # VTK format typically uses (X, Y, Z)

# Extract `rhof_1` and reshape into a 3D array
rhof_1_full = np.array(data.GetPointData().GetArray("rhof_1")).reshape((nz, ny, nx))  # Note the order
# Sum rhof_1 across x and y for each z-layer
z_sums = np.sum(rhof_1_full, axis=(1, 2))  # Sum along x and y axes
best_z = np.argmax(z_sums)  # Find the z-layer with the strongest burning

print(f"🔥 The most intense burning occurs at height layer z = {best_z}")
