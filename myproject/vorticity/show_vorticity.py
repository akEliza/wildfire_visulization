import os
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk

# 输入和输出路径
input_directory = r"F:\Firetec\valley_losAlamos"
output_directory = r"E:\MM804\project\myproject\results_vorticity\valley_losAlamos"

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# ===== 色图设置 =====
def create_flame_colormap():
    ctf = vtk.vtkColorTransferFunction()
    ctf.AddRGBPoint(330, 0.0, 0.0, 1.0)  # 蓝
    ctf.AddRGBPoint(350, 1.0, 0.0, 0.0)  # 红
    return ctf

def create_flame_opacity():
    pf = vtk.vtkPiecewiseFunction()
    pf.AddPoint(330, 0.0)
    pf.AddPoint(340, 0.2)
    pf.AddPoint(350, 0.4)
    return pf

def create_vorticity_colormap():
    ctf = vtk.vtkColorTransferFunction()
    ctf.SetColorSpaceToRGB()
    ctf.AddRGBPoint(0.0, 0.2, 0.2, 1.0)    # 蓝
    ctf.AddRGBPoint(1.5, 1.0, 1.0, 1.0)    # 白
    ctf.AddRGBPoint(3.0, 1.0, 0.2, 0.2)    # 红
    return ctf

def create_vorticity_opacity():
    pf = vtk.vtkPiecewiseFunction()
    pf.AddPoint(0.0, 0)
    pf.AddPoint(0.395686, 0)
    pf.AddPoint(3.18132, 0.1525)
    return pf

# 遍历所有 .vts 文件
for _, filename in enumerate(os.listdir(input_directory)):
    if filename.endswith(".vts"):
        grid_file_path = os.path.join(input_directory, filename)
        i = int(filename.split('.')[1]) // 1000
        print(f"处理文件: {grid_file_path}")

        # ===== 读取数据 =====
        reader = vtk.vtkXMLStructuredGridReader()
        reader.SetFileName(grid_file_path)
        reader.Update()
        grid = reader.GetOutput()

        bounds = np.array(grid.GetBounds())
        extent = np.array(grid.GetExtent())
        resampled_dims = [300, 250, 150]
        spacing = (bounds[1::2] - bounds[:-1:2]) / (np.array(resampled_dims) - 1)
        origin = bounds[::2]

        # ===== 重采样为 ImageData =====
        resample = vtk.vtkResampleToImage()
        resample.AddInputDataObject(grid)
        resample.SetSamplingDimensions(resampled_dims)
        resample.SetSamplingBounds(bounds)
        resample.Update()
        image = resample.GetOutput()

        # ===== 火焰字段 =====
        theta_array = image.GetPointData().GetArray("theta")
        theta_image = vtk.vtkImageData()
        theta_image.DeepCopy(image)
        theta_image.GetPointData().SetScalars(theta_array)

        # ===== 地形提取 =====
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
        terrain_actor.GetProperty().SetColor(0.0, 0.6, 0.0)
        terrain_actor.GetProperty().SetAmbient(0.4)
        terrain_actor.GetProperty().SetDiffuse(0.6)
        terrain_actor.GetProperty().SetSpecular(0.2)

        # ===== 火焰 volume actor =====
        flame_color = create_flame_colormap()
        flame_opacity = create_flame_opacity()

        flame_mapper = vtk.vtkSmartVolumeMapper()
        flame_mapper.SetInputData(theta_image)

        flame_prop = vtk.vtkVolumeProperty()
        flame_prop.SetColor(flame_color)
        flame_prop.SetScalarOpacity(flame_opacity)
        flame_prop.ShadeOn()
        flame_prop.SetInterpolationTypeToLinear()

        flame_actor = vtk.vtkVolume()
        flame_actor.SetMapper(flame_mapper)
        flame_actor.SetProperty(flame_prop)

        # ===== 计算涡量 vector -> vorticity magnitude =====
        u_array = image.GetPointData().GetArray("u")
        v_array = image.GetPointData().GetArray("v")
        w_array = image.GetPointData().GetArray("w")

        velocity_array = vtk.vtkFloatArray()
        velocity_array.SetName("velocity")
        velocity_array.SetNumberOfComponents(3)

        for idx in range(u_array.GetNumberOfTuples()):
            u, v, w = u_array.GetTuple1(idx), v_array.GetTuple1(idx), w_array.GetTuple1(idx)
            velocity_array.InsertNextTuple3(u, v, w)

        image.GetPointData().AddArray(velocity_array)
        image.GetPointData().SetVectors(velocity_array)

        # CellDerivatives → Vorticity
        cell_deriv = vtk.vtkCellDerivatives()
        cell_deriv.SetInputData(image)
        cell_deriv.SetVectorModeToComputeVorticity()
        cell_deriv.SetTensorModeToPassTensors()
        cell_deriv.Update()

        c2p = vtk.vtkCellDataToPointData()
        c2p.SetInputConnection(cell_deriv.GetOutputPort())
        c2p.SetInputArrayToProcess(0, 0, 0, vtk.VTK_SCALAR_MODE_USE_CELL_DATA, "Vorticity")
        c2p.SetProcessAllArrays(True)
        c2p.Update()

        vort_np = vtk_to_numpy(c2p.GetOutput().GetPointData().GetArray("Vorticity"))
        vort_mag = np.linalg.norm(vort_np, ord=2, axis=1)
        vort_mag_3d = vort_mag.reshape(resampled_dims)
        vort_mag_3d[-5:, :, :] = 0  # Z 方向裁剪顶部
        vort_vtk_array = numpy_to_vtk(vort_mag_3d.reshape(-1))
        vort_vtk_array.SetName("vortMag")

        vort_image = vtk.vtkImageData()
        vort_image.DeepCopy(image)
        vort_image.GetPointData().SetScalars(vort_vtk_array)

        # ===== 涡量 volume actor =====
        vort_color = create_vorticity_colormap()
        vort_opacity = create_vorticity_opacity()

        vort_mapper = vtk.vtkSmartVolumeMapper()
        vort_mapper.SetInputData(vort_image)
        vort_mapper.Update()

        vort_prop = vtk.vtkVolumeProperty()
        vort_prop.SetColor(vort_color)
        vort_prop.SetScalarOpacity(vort_opacity)
        vort_prop.SetInterpolationTypeToLinear()

        vort_actor = vtk.vtkVolume()
        vort_actor.SetMapper(vort_mapper)
        vort_actor.SetProperty(vort_prop)

        # ===== 渲染器设置 =====
        renderer = vtk.vtkRenderer()
        renderer.SetBackground((0.9, 0.9, 0.95))  # 黑色背景
        renderer.AddActor(terrain_actor)
        renderer.AddActor(flame_actor)
        renderer.AddActor(vort_actor)
        renderer.ResetCamera()

        camera = renderer.GetActiveCamera()
        camera.SetClippingRange(1, 20000)
        camera.SetPosition(1400, -1500, 2500)
        camera.SetFocalPoint(300, -100, 250)
        camera.SetViewUp(-0.4, 0.7, 0.6)

        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        render_window.SetSize(1920, 1080)

        render_window.Render()
        window_to_image = vtk.vtkWindowToImageFilter()
        window_to_image.SetInput(render_window)
        window_to_image.SetScale(1)
        window_to_image.SetInputBufferTypeToRGB()
        window_to_image.ReadFrontBufferOff()
        window_to_image.Update()

        output_img_path = os.path.join(output_directory, f"{i:03d}.png")
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(output_img_path)
        writer.SetInputConnection(window_to_image.GetOutputPort())
        writer.Write()
