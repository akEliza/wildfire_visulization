import os
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy

data_category = ['backcurve40' , 'headcurve40', 'backcurve80',  'backcurve320' , 'headcurve80' , 'headcurve320',  'valley_losAlamos']
# 输入和输出路径
input_directory = r"F:\Firetec\valley_losAlamos"
output_directory = r"E:\MM804\project\myproject\results\valley_losAlamos"

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# 颜色映射函数
def create_flame_colormap():
    ctf = vtk.vtkColorTransferFunction()
    ctf.AddRGBPoint(330, 0.0, 0.0, 1.0)  # 蓝色
    ctf.AddRGBPoint(350, 1.0, 0.0, 0.0)  # 红色
    return ctf

def create_flame_opacity():
    pf = vtk.vtkPiecewiseFunction()
    pf.AddPoint(330, 0.0)
    pf.AddPoint(340, 0.2)
    pf.AddPoint(350, 0.4)
    return pf

def create_wind_colormap():
    ctf = vtk.vtkColorTransferFunction()
    ctf.SetColorSpaceToRGB()
    ctf.AddRGBPoint(0.0, 0.2, 0.2, 1.0)   # 蓝
    ctf.AddRGBPoint(13.5, 1.0, 1.0, 1.0)  # 白
    ctf.AddRGBPoint(27.0, 1.0, 0.0, 0.0)  # 红
    return ctf

# 遍历 .vts 文件
for _, filename in enumerate(os.listdir(input_directory)):
    if filename.endswith(".vts"):
        grid_file_path = os.path.join(input_directory, filename)
        i = int(filename.split('.')[1]) // 1000
        print(f"处理文件: {grid_file_path}")

        # 读取 VTK 数据
        reader = vtk.vtkXMLStructuredGridReader()
        reader.SetFileName(grid_file_path)
        reader.Update()
        grid = reader.GetOutput()

        bounds = np.array(grid.GetBounds())
        extent = np.array(grid.GetExtent())
        resampled_dims = [300, 250, 150]

        spacing = (bounds[1::2] - bounds[::2]) / (np.array(resampled_dims) - 1)
        origin = bounds[::2]

        # Resample 数据
        resample = vtk.vtkResampleToImage()
        resample.AddInputDataObject(grid)
        resample.SetSamplingDimensions(resampled_dims)
        resample.SetSamplingBounds(bounds)
        resample.Update()
        image = resample.GetOutput()

        # ====== 火焰字段 ======
        theta_array = image.GetPointData().GetArray("theta")
        theta_image = vtk.vtkImageData()
        theta_image.DeepCopy(image)
        theta_image.GetPointData().SetScalars(theta_array)

        # ====== 地形提取 ======
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

        # ====== 火焰体渲染设置 ======
        flame_color = create_flame_colormap()
        flame_opacity = create_flame_opacity()

        volume_mapper = vtk.vtkSmartVolumeMapper()
        volume_mapper.SetInputData(theta_image)

        volume_prop = vtk.vtkVolumeProperty()
        volume_prop.SetColor(flame_color)
        volume_prop.SetScalarOpacity(flame_opacity)
        volume_prop.ShadeOn()
        volume_prop.SetInterpolationTypeToLinear()

        volume_actor = vtk.vtkVolume()
        volume_actor.SetMapper(volume_mapper)
        volume_actor.SetProperty(volume_prop)

        # ====== 风速向量场和 magnitude ======
        u_array = image.GetPointData().GetArray("u")
        v_array = image.GetPointData().GetArray("v")
        w_array = image.GetPointData().GetArray("w")

        magnitude_array = vtk.vtkFloatArray()
        magnitude_array.SetName("wind_mag")
        magnitude_array.SetNumberOfComponents(1)

        vector_array = vtk.vtkFloatArray()
        vector_array.SetName("velocity")
        vector_array.SetNumberOfComponents(3)

        for idx in range(u_array.GetNumberOfTuples()):
            u = u_array.GetTuple1(idx)
            v = v_array.GetTuple1(idx)
            w = w_array.GetTuple1(idx)
            mag = np.sqrt(u ** 2 + v ** 2 + w ** 2)
            magnitude_array.InsertNextValue(mag)
            vector_array.InsertNextTuple3(u, v, w)

        image.GetPointData().AddArray(vector_array)
        image.GetPointData().AddArray(magnitude_array)
        image.GetPointData().SetVectors(vector_array)
        image.GetPointData().SetScalars(magnitude_array)

        # ====== 流线生成 ======
        line_seed = vtk.vtkLineSource()
        line_seed.SetPoint1(3.15, -750, 222)
        line_seed.SetPoint2(3.15, 750, 222)
        line_seed.SetResolution(300)
        line_seed.Update()

        stream_tracer = vtk.vtkStreamTracer()
        stream_tracer.SetInputData(image)
        stream_tracer.SetSourceConnection(line_seed.GetOutputPort())
        stream_tracer.SetIntegrator(vtk.vtkRungeKutta4())
        stream_tracer.SetIntegrationDirectionToBoth()
        stream_tracer.SetMaximumPropagation(2000)
        stream_tracer.SetInitialIntegrationStep(0.1)
        stream_tracer.SetMinimumIntegrationStep(0.05)
        stream_tracer.SetMaximumIntegrationStep(0.5)
        stream_tracer.SetMaximumNumberOfSteps(3000)
        stream_tracer.SetTerminalSpeed(1e-13)
        stream_tracer.Update()

        # ====== 流线颜色映射 ======
        wind_colormap = create_wind_colormap()

        streamline_mapper = vtk.vtkPolyDataMapper()
        streamline_mapper.SetInputConnection(stream_tracer.GetOutputPort())
        streamline_mapper.SetScalarModeToUsePointFieldData()
        streamline_mapper.SelectColorArray("wind_mag")
        streamline_mapper.SetLookupTable(wind_colormap)
        streamline_mapper.SetScalarRange(0, 27)

        streamline_actor = vtk.vtkActor()
        streamline_actor.SetMapper(streamline_mapper)
        streamline_actor.GetProperty().SetLineWidth(0.5)

        # ====== 渲染器设置 ======
        renderer = vtk.vtkRenderer()
        renderer.SetBackground(0.9, 0.9, 0.95)
        renderer.AddActor(terrain_actor)
        renderer.AddActor(volume_actor)
        renderer.AddActor(streamline_actor)
        renderer.ResetCamera()

        # 相机设置
        camera = renderer.GetActiveCamera()
        camera.SetClippingRange(1, 20000)
        camera.SetPosition(1400, -1500, 2500)
        camera.SetFocalPoint(300, -100, 250)
        camera.SetViewUp(-0.4, 0.7, 0.6)

        # 渲染窗口设置
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        render_window.SetSize(1920, 1080)

        # 导出图像
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
