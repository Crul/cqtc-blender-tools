import bpy.types

class NumberedIntroPanel(bpy.types.Panel):
	bl_label = "Añadir Tomas Falsas"
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
		layout.row().label("%i tiras seleccionadas" % selected_sequences_count)
		
		row = layout.row()
		row.scale_y = 2.0
		row.operator("numbered_intro.create")
