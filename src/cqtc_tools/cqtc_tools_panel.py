import cqtc_panel

class CqtcToolsPanel(cqtc_panel.CqtcPanel):
	bl_label = "Herramientas"
	bl_idname = "SCENE_PT_cqtc_tools"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"

	def draw(self, context):
		layout = self.layout
		
		self.draw_selected_sequences_info(layout, context)
		
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
