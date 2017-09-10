import os
import zipfile

current_path = os.path.dirname(__file__)
src_folder = "src"
src_path = os.path.join(current_path, src_folder)

build_path = r"build"
if not os.path.exists(build_path):
    os.makedirs(build_path)

addons = ["cqtc_super_effects", "cqtc_tools"]
for addon in addons:
	output_fullpath = os.path.join(build_path, ("%s.zip" % addon))
	if os.path.exists(output_fullpath):
		os.remove(output_fullpath)
	
	output_file = zipfile.ZipFile(output_fullpath, "w")
	
	addon_files_by_folder = [(name, files) for name, sub_folders, files in os.walk(os.path.join(src_path, addon)) if "__pycache__" not in name ]
	for addon_folder, addon_files in addon_files_by_folder:
		for addon_file in addon_files:
			file_path = os.path.join(addon_folder, addon_file)
			output_file_path = file_path[len(src_folder):]
			output_file.write(file_path, output_file_path, zipfile.ZIP_DEFLATED)
			
			
	print("Addon %s build: %s" % (addon, output_fullpath))
