import bpy
from .super_efecto_panel import SuperEfectoPanel
from .super_efecto_properties import SuperEfectoProperties
from .templates import AddSuperEfectoTemplateOperator, LoadSuperEfectoTemplateOperator, SetSuperEfectoTemplateNameOperator, RemoveSuperEfectoTemplateOperator
from .create_super_efecto_operator import CreateSuperEfectoOperator

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
