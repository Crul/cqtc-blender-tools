bl_info = {
	"name": "CQTC Super Efectos",
	"description": "Plugin para hacer efectos varios",
	"location": "Properties > Render > Añadir Super Efectos",
	"category": "CosoQueTeCoso",
	"version": (1, 0),
	"blender": (2, 78, 0),
}
 
if "bpy" in locals():
	import imp
	imp.reload(createSuperEfectoOperator)
	imp.reload(superEfectoPanel)
	imp.reload(superEfectoProperties)
	imp.reload(templates)
else:
	from .superEfectoPanel import SuperEfectoPanel
	from .superEfectoProperties import SuperEfectoProperties
	from .templates import AddSuperEfectoTemplateOperator, LoadSuperEfectoTemplateOperator, SetSuperEfectoTemplateNameOperator, RemoveSuperEfectoTemplateOperator
	from .createSuperEfectoOperator import CreateSuperEfectoOperator
	
 
import bpy
from bpy.props import *

def register():
	bpy.utils.register_class(CreateSuperEfectoOperator)
	bpy.utils.register_class(SuperEfectoPanel)
	bpy.utils.register_class(SuperEfectoProperties)
	bpy.utils.register_class(AddSuperEfectoTemplateOperator)
	bpy.utils.register_class(LoadSuperEfectoTemplateOperator)
	bpy.utils.register_class(SetSuperEfectoTemplateNameOperator)
	bpy.utils.register_class(RemoveSuperEfectoTemplateOperator)
	bpy.types.Scene.super_efecto = bpy.props.PointerProperty(type=SuperEfectoProperties)


def unregister():
	bpy.utils.unregister_class(CreateSuperEfectoOperator)
	bpy.utils.unregister_class(SuperEfectoPanel)
	bpy.utils.unregister_class(SuperEfectoProperties)
	bpy.utils.unregister_class(AddSuperEfectoTemplateOperator)
	bpy.utils.unregister_class(LoadSuperEfectoTemplateOperator)
	bpy.utils.unregister_class(SetSuperEfectoTemplateNameOperator)
	bpy.utils.unregister_class(RemoveSuperEfectoTemplateOperator)
	del bpy.types.Scene.super_efecto


if __name__ == "__main__":
	register()
