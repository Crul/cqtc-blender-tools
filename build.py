import os
import shutil
import zipfile

build_path = "build"
src_path = "src"
addons = [ addon for addon in next(os.walk(src_path))[1] if addon not in ["modules", "__pycache__"] ]

def build():
	if not os.path.exists(build_path):
		os.makedirs(build_path)
	
	build_modules()
	build_addons()


def build_modules():
	build_modules_path = os.path.join(build_path, "modules")
	if os.path.exists(build_modules_path):
		shutil.rmtree(build_modules_path)

	os.makedirs(build_modules_path)
	
	modules_path = os.path.join(src_path, "modules")
	for module_file_path, module_file in ___file_tree_generator(modules_path):
		output_file_path = os.path.join(build_modules_path, module_file)
		shutil.copyfile(module_file_path, output_file_path)
		print("Module %s\n" % output_file_path)


def build_addons():
	for addon in addons:
		output_fullpath = os.path.join(build_path, ("%s.zip" % addon))
		if os.path.exists(output_fullpath):
			os.remove(output_fullpath)
		
		output_file = zipfile.ZipFile(output_fullpath, "w")
		addon_path = os.path.join(src_path, addon)
		addon_files = []
		for addon_file_path, addon_file in ___file_tree_generator(addon_path):
			output_file_path = addon_file_path[len(src_path):]
			output_file.write(addon_file_path, output_file_path, zipfile.ZIP_DEFLATED)
			addon_files.append(output_file_path)
		
		addon_info = "Addon %s build: %s" % (addon, output_fullpath)
		addon_info += " > ".join("%s\n" % f for f in ([""] + addon_files))
		print(addon_info)


def ___file_tree_generator(folder_path):
	files_by_folder = [(name, files) for name, sub_folders, files in os.walk(folder_path) if "__pycache__" not in name ]
	for folder, files in files_by_folder:
		for file in files:
			file_path = os.path.join(folder, file)
			yield file_path, file


if __name__ == "__main__":
	build()
