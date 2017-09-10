import bpy.props
import bpy.types
from .super_effect_creator import SuperEffectCreator

class CreateSuperEffectOperator(bpy.types.Operator):
	bl_idname = "super_effect.create"
	bl_label = "Crear Transición"
	operation_type =  bpy.props.StringProperty()
	super_effect_creator = SuperEffectCreator()

	def execute(self, context):
		error = self.super_effect_creator.create(context, self.operation_type)
		if error:
			(error_result, error_msg) = error
			self.report(error_result, error_msg)
			return {"CANCELLED"}
	
		return {"FINISHED"}
