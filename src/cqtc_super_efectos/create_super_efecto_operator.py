import bpy.props
import bpy.types
from .super_efecto_creator import SuperEfectoCreator

class CreateSuperEfectoOperator(bpy.types.Operator):
	bl_idname = "super_efecto.create"
	bl_label = "Crear Transición"
	operation_type =  bpy.props.StringProperty()
	super_efecto_creator = SuperEfectoCreator()

	def execute(self, context):
		error = self.super_efecto_creator.create(context, self.operation_type)
		if error:
			(error_result, error_msg) = error
			self.report(error_result, error_msg)
			return {"CANCELLED"}
	
		return {"FINISHED"}
