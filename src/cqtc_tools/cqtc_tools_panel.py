import bpy.types

class CqtcToolsPanel(bpy.types.Panel):
	bl_label = "Herramientas"
	bl_idname = "SCENE_PT_cqtc_tools"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"

	def draw(self, context):
		layout = self.layout
		
		selected_sequences_count = len(context.selected_sequences) if context.selected_sequences else 0
		layout.row().label("%i tiras seleccionadas" % selected_sequences_count)
		
		split = layout.split()
		
		col = split.column()
		split_2 = col.split(percentage=0.66)
		split_2.column().prop(context.scene.cqtc_tools_proxy, "jpeg_quality")
		split_2.column().prop(context.scene.cqtc_tools_proxy, "rebuild")
		
		row = col.row()
		row.scale_y = 2.0
		row.operator("cqtc_tools_proxy.set_proxy")
		
		col = split.column(align=True)
		row = col.row(align=True)
		row.scale_y = 1.5
		move_channel_up_operator = row.operator("cqtc_tools_channel.change", text="Subir strips")
		move_channel_up_operator.up_or_down = True
		
		row = col.row(align=True)
		row.scale_y = 1.5
		move_channel_up_operator = row.operator("cqtc_tools_channel.change", text="Bajar strips")
		move_channel_up_operator.up_or_down = False
