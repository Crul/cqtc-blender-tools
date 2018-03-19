import cqtc_panel

class AnimatedSequencePanel(cqtc_panel.CqtcPanel):
	bl_label = cqtc_panel.CqtcPanel.translate_cls("Add Animated Sequence")
	bl_idname = "SCENE_PT_animated_sequence"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"

	def draw_header(self, context):
		self.layout.label(" ", icon="FILE_IMAGE")
	
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		
		layout.row().prop(context.scene.animated_sequence, "sequence_path")
		layout.row().prop(context.scene.animated_sequence, "base_name")
		row = layout.row()
		row.prop(context.scene.animated_sequence, "from_image")
		row.prop(context.scene.animated_sequence, "to_image")
		
		layout.row().prop(context.scene.animated_sequence, "add_last_image_if_marker_exists")
		layout.row().prop(context.scene.animated_sequence, "remove_markers")
		layout.row().prop(context.scene.animated_sequence, "strip_channel")
		
		row = layout.row()
		row.scale_y = 2.0
		
		self.operator_i18n(row, "animated_sequence.create", "Create Animated Sequence")
