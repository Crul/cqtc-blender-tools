import bpy.props
from cqtc_operator import CqtcOperator
import bpy_utils

class ChangeStripsChannelOperator(CqtcOperator):
	bl_idname = "cqtc_tools_channel.change"
	bl_label = "Cambiar canal de las secuencias"
	up_or_down =  bpy.props.BoolProperty(default=True)
	
	def execute(self, context):
		if len(context.selected_sequences) == 0:
			return self.return_error("No hay strips seleccionadas")
		
		selected_sequences = sorted(context.selected_sequences,
			key=lambda s : s.channel,
			reverse=self.up_or_down)
		
		for sequence in selected_sequences:
			sequence.channel = bpy_utils.get_available_channel_for_strip(context, sequence, self.up_or_down)
		
		return {"FINISHED"}
