import os

folder = r'E:\MM804\project\myproject\results_vorticity\backcurve40'  # 当前目录
files = [f for f in os.listdir(folder) if f.lower().endswith(".png")]

# 自定义排序（数字顺序），提取其中的数字部分（如果有）
def extract_number(filename):
    digits = ''.join(filter(str.isdigit, filename))
    return int(digits) if digits else float('inf')

# 排序文件列表
files.sort(key=extract_number)

# 重命名为 01.png ~ 72.png
for i, old_name in enumerate(files, start=1):
    new_name = f"{i:03d}.png"
    old_path = os.path.join(folder, old_name)
    new_path = os.path.join(folder, new_name)
    os.rename(old_path, new_path)
    print(f"{old_name} → {new_name}")
