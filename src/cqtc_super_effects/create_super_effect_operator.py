import bpy.props
from cqtc_operator import CqtcOperator
from .super_effect_creator import SuperEffectCreator

class CreateSuperEffectOperator(CqtcOperator):
	bl_idname = "super_effect.create"
	bl_label = "Crear Transición"
	operation_type =  bpy.props.StringProperty()
	super_effect_creator = SuperEffectCreator()

	def execute(self, context):
		error = self.super_effect_creator.create(context, self.operation_type)
		if error:
			return self.return_error(error)
	
		return {"FINISHED"}
