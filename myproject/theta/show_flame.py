import os
import pyvista as pv
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.colors as colors

# Set input and output directories
# Options: backcurve80, backcurve320, headcurve80, headcurve320, valley_losAlamos
input_directory = r"F:\Firetec\headcurve320"
output_directory = r"E:\MM804\project\myproject\results\headcurve320"

# Make sure the output directory exists
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Loop through all .vts files in the directory
for _, filename in enumerate(os.listdir(input_directory)):
    
    if filename.endswith(".vts"):
        grid_file_path = os.path.join(input_directory, filename)
        i = int(filename.split('.')[1]) // 1000
        # Skip frames 37 and 38 if needed
        if i > 9: continue
        print(f"Processing file: {grid_file_path}")

        # ======== Read VTS file ========
        grid = pv.read(grid_file_path)

        # ======== Read structured grid ========
        reader = vtk.vtkXMLStructuredGridReader()
        reader.SetFileName(grid_file_path)
        reader.Update()
        grid = reader.GetOutput()

        bounds = np.array(grid.GetBounds())
        extent = np.array(grid.GetExtent())
        resampled_dims = [300, 250, 150]
        spacing = (bounds[1::2] - bounds[::2]) / (np.array(resampled_dims) - 1)
        origin = bounds[::2]

        # ======== Extract `theta` field ========
        resample = vtk.vtkResampleToImage()
        resample.AddInputDataObject(grid)
        resample.SetSamplingDimensions(resampled_dims)
        resample.SetSamplingBounds(bounds)
        resample.Update()
        image = resample.GetOutput()

        theta_array = image.GetPointData().GetArray("theta")
        theta_image = vtk.vtkImageData()
        theta_image.DeepCopy(image)
        theta_image.GetPointData().SetScalars(theta_array)

        # ======== Extract terrain ========
        extractor = vtk.vtkExtractGrid()
        extractor.SetInputData(grid)
        extractor.SetVOI(extent[0], extent[1], extent[2], extent[3], 0, 5)
        extractor.Update()
        terrain = extractor.GetOutput()

        terrain_mapper = vtk.vtkDataSetMapper()
        terrain_mapper.SetInputData(terrain)
        terrain_mapper.ScalarVisibilityOff()
        terrain_actor = vtk.vtkActor()
        terrain_actor.SetMapper(terrain_mapper)
        terrain_actor.GetProperty().SetColor(0.0, 0.6, 0.0)  # Green color
        terrain_actor.GetProperty().SetAmbient(0.4)          # Increase ambient light
        terrain_actor.GetProperty().SetDiffuse(0.6)          # Increase diffuse reflection
        terrain_actor.GetProperty().SetSpecular(0.2)         # Add a bit of specular highlight

        # ======== Theta volume mapper ========
        volume_mapper = vtk.vtkSmartVolumeMapper()
        volume_mapper.SetInputData(theta_image)

        volume_color = vtk.vtkColorTransferFunction()
        volume_color.AddRGBPoint(330, 0.0, 0.0, 1.0)
        volume_color.AddRGBPoint(350, 1.0, 0.0, 0.0)

        volume_opacity = vtk.vtkPiecewiseFunction()
        volume_opacity.AddPoint(330, 0.0)
        volume_opacity.AddPoint(340, 0.2)
        volume_opacity.AddPoint(350, 0.4)

        volume_prop = vtk.vtkVolumeProperty()
        volume_prop.SetColor(volume_color)
        volume_prop.SetScalarOpacity(volume_opacity)
        volume_prop.ShadeOn()
        volume_prop.SetInterpolationTypeToLinear()

        volume_actor = vtk.vtkVolume()
        volume_actor.SetMapper(volume_mapper)
        volume_actor.SetProperty(volume_prop)

        # ======== Renderer ========
        renderer = vtk.vtkRenderer()
        renderer.AddActor(terrain_actor)
        renderer.AddActor(volume_actor)
        # renderer.SetBackground(0.32, 0.34, 0.43)
        renderer.ResetCamera()
        renderer.SetBackground(0.9, 0.9, 0.95)

        camera = renderer.GetActiveCamera()
        camera.SetClippingRange(1, 20000)
        camera.SetPosition(1400, -1500, 2500)
        camera.SetFocalPoint(300, -100, 250)
        camera.SetViewUp(-0.4, 0.7, 0.6)
        # camera.Zoom(1.3)

        # ======== Render window ========
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        render_window.SetSize(1920, 1080)

        # ======== Interactor ========
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)

        # ======== Render and export image ========
        render_window.Render()  # Must call this before exporting image

        # Export image
        window_to_image = vtk.vtkWindowToImageFilter()
        window_to_image.SetInput(render_window)
        window_to_image.SetScale(1)  # You can set resolution scaling
        window_to_image.SetInputBufferTypeToRGB()
        window_to_image.ReadFrontBufferOff()  # Read from back buffer
        window_to_image.Update()

        output_img_path = os.path.join(output_directory, f"{i:03d}.png")
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(output_img_path)
        writer.SetInputConnection(window_to_image.GetOutputPort())
        writer.Write()

        # ======== Launch interactive window (optional) ========
        # interactor.Start()
        # """
