import os

folder = r'E:\MM804\project\myproject\results_vorticity\backcurve40'  # Current directory
files = [f for f in os.listdir(folder) if f.lower().endswith(".png")]

# Custom sort by numeric order, extracting number part from filename (if any)
def extract_number(filename):
    digits = ''.join(filter(str.isdigit, filename))
    return int(digits) if digits else float('inf')

# Sort the file list
files.sort(key=extract_number)

# Rename files to 001.png ~ 072.png
for i, old_name in enumerate(files, start=1):
    new_name = f"{i:03d}.png"
    old_path = os.path.join(folder, old_name)
    new_path = os.path.join(folder, new_name)
    os.rename(old_path, new_path)
    print(f"{old_name} → {new_name}")
