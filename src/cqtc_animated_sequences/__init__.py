bl_info = {
	"name": "CQTC Añadir Sequencias Animadas",
	"description": "Plugin para añadir sequencias animadas de imágenes",
	"location": "Properties > Render > Añadir Sequencias Animadas",
	"category": "CosoQueTeCoso",
	"version": (1, 0),
	"blender": (2, 78, 0),
}

if "bpy" in locals():
	import imp
	imp.reload(blender_addon)
else:
	from . import blender_addon

def register():
	blender_addon.register(__name__)

def unregister():
	blender_addon.unregister(__name__)

if __name__ == "__main__":
	register()
