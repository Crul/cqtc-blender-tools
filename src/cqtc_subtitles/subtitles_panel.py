import os
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
		
		layout.row().prop(context.scene.subtitle, "template")
		
		layout.row().prop(context.scene.subtitle, "scene_name")
		layout.row().prop(context.scene.subtitle, "text")
		
		prefs = context.user_preferences.addons[__package__].preferences
		if os.path.isdir(prefs.icons_path):
			split = layout.row().split(percentage=0.33)
			split.column()
			icons_col = split.column()
			for item_index, item in enumerate(context.scene.subtitle.icons):
				row = icons_col.row()
				split = row.split(percentage=0.9)
				split.column().prop(item, "icon_index")
				
				remove_icon_operator = split.column().operator("subtitles.modify_icon", text="", icon="X")
				remove_icon_operator.operation = "remove"
				remove_icon_operator.index_to_remove = item_index
			
			if context.scene.subtitle.more_icons_allowed():
				add_icon_operator = icons_col.operator("subtitles.modify_icon", text="Añadir icono", icon="PLUS")
				add_icon_operator.operation = "add"
				
		split = layout.split(percentage=0.33)
		split.prop(context.scene.subtitle, "position")
		split.prop(context.scene.subtitle, "is_marquee")
		if not context.scene.subtitle.is_marquee:
			split.prop(context.scene.subtitle, "fullscreen_width")
		
		row = layout.row()
		row.scale_y = 2.0
		row.operator("subtitle.create")
		
		row = layout.row()
		row.prop(context.scene.subtitle, "config_expanded",
			icon="TRIA_DOWN" if context.scene.subtitle.config_expanded else "TRIA_RIGHT",
			icon_only=False
		)
		
		if context.scene.subtitle.config_expanded:
			split = layout.row().split(percentage=0.02)
			empty_col = split.column()
			config_col = split.column()
				
			config_col.row().prop(context.scene.subtitle, "width")
			
			margin_row = config_col.row().split(percentage=0.5)
			self.draw_margin_props(context, margin_row, "internal")
			self.draw_margin_props(context, margin_row, "external")
			
			row = config_col.row()
			row.prop(context.scene.subtitle, "font_expanded",
				icon="TRIA_DOWN" if context.scene.subtitle.font_expanded else "TRIA_RIGHT",
				icon_only=False
			)
			
			if context.scene.subtitle.font_expanded:
				split = config_col.row().split(percentage=0.02)
				empty_col = split.column()
				box = split.column().box()
				box.row().prop(context.scene.subtitle, "font_color")
				box.row().prop(context.scene.subtitle, "font_size")
				box.row().prop(context.scene.subtitle, "font_bevel_depth")
				box.row().prop(context.scene.subtitle, "font_spacing")
				box.row().prop(context.scene.subtitle, "font_path")
			
				box.row().prop(context.scene.subtitle, "font_has_border")
				if context.scene.subtitle.font_has_border:
					box.row().prop(context.scene.subtitle, "font_border_size")
					box.row().prop(context.scene.subtitle, "font_border_color")
			
			box = config_col.box()
			box.row().prop(context.scene.subtitle, "create_bgr")
			if context.scene.subtitle.create_bgr:
				split = box.row().split(percentage=0.05)
				col = split.column()
				col = split.column()
				
				col.row().prop(context.scene.subtitle, "bgr_color")
				col.row().prop(context.scene.subtitle, "bgr_alpha")
			
			box = config_col.box()
			box.row().prop(context.scene.subtitle, "create_strip")
			if context.scene.subtitle.create_strip:
				split = box.row().split(percentage=0.05)
				col = split.column()
				col = split.column()
				
				col.row().prop(context.scene.subtitle, "strip_channel")
				col.row().prop(context.scene.subtitle, "strip_length")
		
		cqtc_templates.draw_template_panel(self, context.scene.subtitle, "subtitle")
	
	
	def draw_margin_props(self, context, row, margin_type):
		col = row.column().box()
		
		title_row = col.row()
		title_row.alignment = "CENTER"
		title_row.label("Margen " + ("exterior" if margin_type == "external" else "interior"))
		
		row = col.row(align=True).split(percentage=0.2)
		row.column()
		row.column().split(percentage=0.75) \
			.prop(context.scene.subtitle, margin_type + "_margin_top", text="Sup")
		
		row = col.row().split(percentage=0.5, align=True)
		row.prop(context.scene.subtitle, margin_type + "_margin_left", text="Izq")
		row.prop(context.scene.subtitle, margin_type + "_margin_right", text="Dch")
		
		row = col.row(align=True).split(percentage=0.2)
		row.column()
		row.column().split(percentage=0.75) \
			.prop(context.scene.subtitle, margin_type + "_margin_bottom", text="Inf")
