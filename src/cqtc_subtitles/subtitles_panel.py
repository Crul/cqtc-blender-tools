import cqtc_panel
import cqtc_templates

class SubtitlesPanel(cqtc_panel.CqtcPanel):
	bl_label = "Añadir Subtítulos"
	bl_idname = "SCENE_PT_subtitle"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"

	def draw_header(self, context):
		self.layout.label(" ", icon="SORTALPHA")
	
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		
		layout.row().prop(context.scene.subtitle, "scene_name")
		layout.row().prop(context.scene.subtitle, "text")
		
		split = layout.split(percentage=0.66)
		split.prop(context.scene.subtitle, "position")
		split.prop(context.scene.subtitle, "is_marquee")
		
		row = layout.row()
		row.scale_y = 2.0
		row.operator("subtitle.create")
		
		row = layout.row()
		row.prop(context.scene.subtitle, "config_expanded",
			icon="TRIA_DOWN" if context.scene.subtitle.config_expanded else "TRIA_RIGHT",
			icon_only=False
		)
		
		if context.scene.subtitle.config_expanded:
			layout.row().prop(context.scene.subtitle, "width")
			layout.row().prop(context.scene.subtitle, "internal_margin")
			layout.row().prop(context.scene.subtitle, "external_margin")
			
			row = layout.row()
			row.prop(context.scene.subtitle, "font_expanded",
				icon="TRIA_DOWN" if context.scene.subtitle.font_expanded else "TRIA_RIGHT",
				icon_only=False
			)
			
			if context.scene.subtitle.font_expanded:
				split = layout.row().split(percentage=0.05)
				col = split.column()
				col = split.column()
				
				col.row().prop(context.scene.subtitle, "font_color")
				col.row().prop(context.scene.subtitle, "font_size")
				col.row().prop(context.scene.subtitle, "font_spacing")
				col.row().prop(context.scene.subtitle, "font_path")
			
			
			layout.row().prop(context.scene.subtitle, "create_bgr")
			if context.scene.subtitle.create_bgr:
				split = layout.row().split(percentage=0.05)
				col = split.column()
				col = split.column()
				
				col.row().prop(context.scene.subtitle, "bgr_color")
				col.row().prop(context.scene.subtitle, "bgr_alpha")
			
			layout.row().prop(context.scene.subtitle, "create_strip")
			
			if context.scene.subtitle.create_strip:
				layout.row().prop(context.scene.subtitle, "strip_channel")
				layout.row().prop(context.scene.subtitle, "strip_length")
		
		cqtc_templates.draw_template_panel(self, context.scene.subtitle, "subtitle")
