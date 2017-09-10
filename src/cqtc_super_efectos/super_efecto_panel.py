import bpy.types

class SuperEfectoPanel(bpy.types.Panel):
	bl_label = "Añadir Super Efectos"
	bl_idname = "SCENE_PT_super_efecto"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"

	def draw(self, context):
		layout = self.layout
		scene = context.scene
				
		layout.row().prop(context.scene.super_efecto, "effect_type")
		
		split = layout.split(percentage=0.25)
		split.column().prop(context.scene.super_efecto, "effect_length_type", text="")
		if context.scene.super_efecto.effect_length_type == "FRAMES":
			split.column().prop(context.scene.super_efecto, "effect_length")
		else:
			split.column().prop(context.scene.super_efecto, "effect_length_percentage")
		
		split = layout.row().split()
		split.prop(context.scene.super_efecto, "image_alignment")
		split.prop(context.scene.super_efecto, "image_alignment_margin")
			
		row = layout.row()
		row.scale_y = 1.5
		row.prop(context.scene.super_efecto, "config_expanded",
			icon="TRIA_DOWN" if context.scene.super_efecto.config_expanded else "TRIA_RIGHT",
			icon_only=False
		)
		if context.scene.super_efecto.config_expanded:
			split = layout.row().split()
			split.prop(context.scene.super_efecto, "apply_to_sound")
			if context.scene.super_efecto.apply_to_sound:
				split.prop(context.scene.super_efecto, "overlap_sound")
			
			layout.row().prop(context.scene.super_efecto, "color")
			layout.row().prop(context.scene.super_efecto, "delay_image")
			self.draw_animatable_prop(context, "position_x")
			self.draw_animatable_prop(context, "position_y")
			self.draw_animatable_prop(context, "zoom")
			self.draw_animatable_prop(context, "opacity")			
			self.draw_animatable_prop(context, "offset_x")
			self.draw_animatable_prop(context, "offset_y")
			self.draw_animatable_prop(context, "blur_x")
			self.draw_animatable_prop(context, "blur_y")
			
			layout.row().prop(context.scene.super_efecto, "constant_speed")
			layout.row().prop(context.scene.super_efecto, "reverse_out_effect")
			layout.row().prop(context.scene.super_efecto, "mirror_horizontal_out_effect")
			layout.row().prop(context.scene.super_efecto, "mirror_vertical_out_effect")
			
		row = layout.row()
		split = row.split(percentage=0.66)
		x_col = split.column(align=True)
		col = x_col.row(align=True)
		col.scale_y = 1.5
		
		create_in_operator = col.operator("super_efecto.create", text="< Entrada")
		create_in_operator.operation_type = "IN"
		
		create_out_operator = col.operator("super_efecto.create", text="Salida >")
		create_out_operator.operation_type = "OUT"
		
		row = x_col.row(align=True)
		row.scale_y = 1.5
		create_ind_and_out_operator = row.operator("super_efecto.create", text="< Entrada y Salida >")
		create_ind_and_out_operator.operation_type = "IN_OUT"
		
		col = split.column(align=True)
		col.prop(context.scene.super_efecto, "add_color_to_transition", toggle=True)
		
		row = col.row(align=True)
		row.scale_y = 2.0
		create_out_operator = row.operator("super_efecto.create", text=">< Transición")
		create_out_operator.operation_type = "TRANSITION"
		
		self.draw_template_panel(context)
	

	def draw_template_panel(self, context):
		layout = self.layout
		row = layout.row()
		row.scale_y = 1.5
		row.prop(context.scene.super_efecto, "template_expanded",
			icon="TRIA_DOWN" if context.scene.super_efecto.template_expanded else "TRIA_RIGHT",
			icon_only=False
		)
	
		if not context.scene.super_efecto.template_expanded:
			return
		
		borrar_btn_width = 0.05
		
		split = layout.row().split(percentage=0.80)
		
		split_1 = split.column().split(percentage=borrar_btn_width)			
		split_1.column().operator("super_efecto.remove_template", text="X")
		
		
		split_2 = split_1.split(percentage=0.25)
		split_2.column().label("Plantillas")
		split_2.column().prop(context.scene.super_efecto, "template", text="")
		split.column().operator("super_efecto.load_template", text="Cargar")
					
		split = layout.row().split(percentage=0.80)
		split_3 = split.column().split(percentage=borrar_btn_width)
		split_3.column()
		
		split_4 = split_3.split(percentage=0.25)
		split_4.column().label("Nombre")
		
		split_5 = split_4.split(align=True, percentage=0.90)
		split_5.column(align=True).prop(context.scene.super_efecto, "new_template_name", text="")
		clear_template_name_operator = split_5.column(align=True).operator("super_efecto.set_template_name", text="X")
		clear_template_name_operator.action = 'CLEAR'
		load_template_name_operator = split_5.column(align=True).operator("super_efecto.set_template_name", text="↓")
		load_template_name_operator.action = 'LOAD'
		
		split.column().operator("super_efecto.add_template", text="Guardar")
		
		if len([tmpl for tmpl in context.scene.super_efecto.template_data if tmpl["name"] == context.scene.super_efecto.new_template_name ]) > 0:
			split = layout.row().split(percentage=0.30)
			split.column()
			split.column().prop(context.scene.super_efecto, "override_template")
	
	
	def draw_animatable_prop(self, context, prop_name):
		layout = self.layout
		split = layout.split(percentage=0.475)
		split.column().prop(context.scene.super_efecto, "initial_%s" % prop_name)
		is_animated_prop_name = "%s_animated" % prop_name
		
		if getattr(context.scene.super_efecto, is_animated_prop_name):
			split = split.column().split(percentage=0.047619)
			split.column().prop(context.scene.super_efecto, is_animated_prop_name, text="")
			split.column().prop(context.scene.super_efecto, "final_%s" % prop_name)
		else:
			split.column().prop(context.scene.super_efecto, is_animated_prop_name)
	