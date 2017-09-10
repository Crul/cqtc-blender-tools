import bpy.props
import bpy.types

class ChangeStripsChannelOperator(bpy.types.Operator):
	bl_idname = "cqtc_tools_channel.change"
	bl_label = "Cambiar canal de las secuencias"
	up_or_down =  bpy.props.BoolProperty(default=True)
			
	def execute(self, context):
		if len(context.selected_sequences) == 0:
			self.report({"ERROR"}, "No hay strips seleccionadas" )
			return {"CANCELLED"}
		
		selected_sequences = sorted(context.selected_sequences, \
			key=lambda s : s.channel, \
			reverse=self.up_or_down)
		
		for sequence in selected_sequences:
			sequence.channel = self.get_available_channel(context, sequence, self.up_or_down)
		
		return {"FINISHED"}
		
	
	def get_available_channel(self, context, target_sequence, up_or_down):
		max_channel = 20
		
		channel_range = []
		if up_or_down:
			channel_range = range(target_sequence.channel + 1, max_channel)
		else:
			channel_range = reversed(range(1, target_sequence.channel))
	
		for channel in channel_range:
			is_channel_available = True
			
			for sequence in context.scene.sequence_editor.sequences:
				is_sequence_in_channel_and_interval = (sequence.channel == channel \
					and sequence.frame_final_start < target_sequence.frame_final_start \
					and sequence.frame_final_end > target_sequence.frame_final_end)
					
				if is_sequence_in_channel_and_interval:
					is_channel_available = False
					break
							
			if is_channel_available:
				return channel
						
		return target_sequence.channel
