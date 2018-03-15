import bpy.props
import bpy.types

class AnimatedSequenceProperties(bpy.types.PropertyGroup):
	sequence_path = bpy.props.StringProperty(name="Path")
	base_name = bpy.props.StringProperty(name="Base name")
	from_image = bpy.props.IntProperty(name="From image", default=1, min=1, max=10, step=1)
	to_image = bpy.props.IntProperty(name="To image", default=99, min=1, max=99, step=1)
	add_last_image_if_marker_exists = bpy.props.BoolProperty(name="Add last image if third marker exists", default=True)
	remove_markers = bpy.props.BoolProperty(name="Remove markers", default=True)