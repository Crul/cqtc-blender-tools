import cqtc_panel

class NumberedIntroPanel(cqtc_panel.CqtcPanel):
	bl_label = cqtc_panel.CqtcPanel.translate_cls("Add Numbered Intros")
	bl_idname = "SCENE_PT_numbered_intro"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		
		row = layout.row()
		row.prop(context.scene.numbered_intro, "next_number")
		row.prop(context.scene.numbered_intro, "transition_length")
		
		selected_sequences_count = len(context.selected_sequences) if context.selected_sequences else 0
		layout.row().label("%i %s" % (selected_sequences_count, self.translate("selected strips")))
		
		row = layout.row()
		row.scale_y = 2.0
		
		self.operator_i18n(row, "numbered_intro.create", "Create Numbered Intros")
