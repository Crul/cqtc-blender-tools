import cqtc_templates
import cqtc_panel

class SuperEffectPanel(cqtc_panel.CqtcPanel):
	bl_label = "Añadir Super Efectos"
	bl_idname = "SCENE_PT_super_effect"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"

	def draw(self, context):
		layout = self.layout
		scene = context.scene
				
		layout.row().prop(context.scene.super_effect, "effect_type")
		
		split = layout.split(percentage=0.25)
		split.column().prop(context.scene.super_effect, "effect_length_type", text="")
		if context.scene.super_effect.effect_length_type == "FRAMES":
			split.column().prop(context.scene.super_effect, "effect_length")
		else:
			split.column().prop(context.scene.super_effect, "effect_length_percentage")
		
		split = layout.row().split()
		split.prop(context.scene.super_effect, "image_alignment")
		split.prop(context.scene.super_effect, "image_alignment_margin")
			
		row = layout.row()
		row.scale_y = 1.5
		row.prop(context.scene.super_effect, "config_expanded",
			icon="TRIA_DOWN" if context.scene.super_effect.config_expanded else "TRIA_RIGHT",
			icon_only=False
		)
		if context.scene.super_effect.config_expanded:
			split = layout.row().split()
			split.prop(context.scene.super_effect, "apply_to_sound")
			if context.scene.super_effect.apply_to_sound:
				split.prop(context.scene.super_effect, "overlap_sound")
			
			layout.row().prop(context.scene.super_effect, "color")
			layout.row().prop(context.scene.super_effect, "delay_image")
			layout.row().prop(context.scene.super_effect, "speed_factor")
			self.draw_animatable_prop(context, "position_x")
			self.draw_animatable_prop(context, "position_y")
			self.draw_animatable_prop(context, "zoom")
			self.draw_animatable_prop(context, "opacity")			
			self.draw_animatable_prop(context, "offset_x")
			self.draw_animatable_prop(context, "offset_y")
			self.draw_animatable_prop(context, "blur_x")
			self.draw_animatable_prop(context, "blur_y")
			
			layout.row().prop(context.scene.super_effect, "constant_speed")
			layout.row().prop(context.scene.super_effect, "reverse_out_effect")
			layout.row().prop(context.scene.super_effect, "mirror_horizontal_out_effect")
			layout.row().prop(context.scene.super_effect, "mirror_vertical_out_effect")
			
		
		self.draw_selected_sequences_info(layout, context)
		
		row = layout.row()
		split = row.split(percentage=0.66)
		x_col = split.column(align=True)
		col = x_col.row(align=True)
		col.scale_y = 1.5
		
		create_in_operator = col.operator("super_effect.create", text="< Entrada")
		create_in_operator.operation_type = "IN"
		
		create_out_operator = col.operator("super_effect.create", text="Salida >")
		create_out_operator.operation_type = "OUT"
		
		row = x_col.row(align=True)
		row.scale_y = 1.5
		create_ind_and_out_operator = row.operator("super_effect.create", text="< Entrada y Salida >")
		create_ind_and_out_operator.operation_type = "IN_OUT"
		
		col = split.column(align=True)
		col.prop(context.scene.super_effect, "add_color_to_transition", toggle=True)
		
		row = col.row(align=True)
		row.scale_y = 2.0
		create_out_operator = row.operator("super_effect.create", text=">< Transición")
		create_out_operator.operation_type = "TRANSITION"
		
		cqtc_templates.draw_template_panel(self, context.scene.super_effect, "super_effect")
	
	
	def draw_animatable_prop(self, context, prop_name):
		layout = self.layout
		split = layout.split(percentage=0.475)
		split.column().prop(context.scene.super_effect, "initial_%s" % prop_name)
		is_animated_prop_name = "%s_animated" % prop_name
		
		if getattr(context.scene.super_effect, is_animated_prop_name):
			split = split.column().split(percentage=0.047619)
			split.column().prop(context.scene.super_effect, is_animated_prop_name, text="")
			split.column().prop(context.scene.super_effect, "final_%s" % prop_name)
		else:
			split.column().prop(context.scene.super_effect, is_animated_prop_name)
	