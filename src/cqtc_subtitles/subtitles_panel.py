import bpy.types

class SubtitlesPanel(bpy.types.Panel):
	bl_label = "Añadir Subtítulos"
	bl_idname = "SCENE_PT_subtitle"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"
	
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		
		layout.row().prop(context.scene.subtitle, "scene_name")
		layout.row().prop(context.scene.subtitle, "text")
		layout.row().prop(context.scene.subtitle, "position")
		
		row = layout.row()
		row.scale_y = 2.0
		row.operator("subtitle.create")
		
		row = layout.row()
		row.scale_y = 1.5
		row.prop(context.scene.subtitle, "config_expanded",
			icon="TRIA_DOWN" if context.scene.subtitle.config_expanded else "TRIA_RIGHT",
			icon_only=False
		)
		
		if context.scene.subtitle.config_expanded:
			layout.row().prop(context.scene.subtitle, "width")
			layout.row().prop(context.scene.subtitle, "internal_margin")
			layout.row().prop(context.scene.subtitle, "external_margin")
			
			row = layout.row()
			row.scale_y = 1.5
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
		
		row = layout.row()
		row.scale_y = 1.5
		row.prop(context.scene.subtitle, "template_expanded",
			icon="TRIA_DOWN" if context.scene.subtitle.template_expanded else "TRIA_RIGHT",
			icon_only=False
		)
		
		if context.scene.subtitle.template_expanded:
			borrar_btn_width = 0.05
			split = layout.row().split(percentage=0.80)
			sub_split = split.column().split(percentage=borrar_btn_width)
			sub_split.column().operator("subtitle.remove_template", text="X")
			sub_split.column().prop(context.scene.subtitle, "template")
			split.column().operator("subtitle.load_template", text="Cargar")
						
			split = layout.row().split(percentage=0.80)
			sub_split = split.column().split(percentage=borrar_btn_width)
			sub_split.column()
			sub_split.column().prop(context.scene.subtitle, "new_template_name")
			split.column().operator("subtitle.add_template", text="Guardar")
