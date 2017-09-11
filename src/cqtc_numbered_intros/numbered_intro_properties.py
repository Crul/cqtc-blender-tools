import bpy.props
import bpy.types

class NumberedIntroProperties(bpy.types.PropertyGroup):
	next_number = bpy.props.IntProperty(name="Siguiente nº", default=1, min=1, max=10, step=1)
	transition_length = bpy.props.IntProperty(name="Duración transición", default=17, min=1, max=1000, step=1)
