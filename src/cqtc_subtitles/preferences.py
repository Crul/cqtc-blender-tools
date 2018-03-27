import bpy.props
import bpy.types

class CqtcSubtitlesPreferences(bpy.types.AddonPreferences):
	bl_idname = __package__
	
	icons_path = bpy.props.StringProperty(
		name="Ruta iconos",
		description="Ruta donde se encuentran los emoticonos",
		default=""
	)
	
	def draw(self, context):
		self.layout.prop(self, "icons_path")
	