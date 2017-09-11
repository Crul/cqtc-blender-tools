import bpy.props
import bpy.types

class SetProxyConfigProperties(bpy.types.PropertyGroup):
	jpeg_quality = bpy.props.IntProperty(name="Calidad JPEG", default=10, min=1, max=100, step=10)
	rebuild = bpy.props.BoolProperty(name="Rebuild", default=True)
