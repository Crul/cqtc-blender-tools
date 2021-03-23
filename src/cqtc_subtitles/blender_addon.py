import bpy.props
import bpy.types
import bpy.utils
from .create_subtitle_operator import CreateSubtitleOperator
from .subtitles_panel import SubtitlesPanel
from .subtitles_properties import SubtitlesProperties, SubtitlesIconProperty, ModifyIconOperator
from .preferences import CqtcSubtitlesPreferences
from .templates import AddSubtitleTemplateOperator, LoadSubtitleTemplateOperator, SetSubtitleTemplateNameOperator, RemoveSubtitleTemplateOperator


def register():	
	bpy.utils.register_class(CreateSubtitleOperator)
	bpy.utils.register_class(AddSubtitleTemplateOperator)
	bpy.utils.register_class(LoadSubtitleTemplateOperator)
	bpy.utils.register_class(SetSubtitleTemplateNameOperator)
	bpy.utils.register_class(RemoveSubtitleTemplateOperator)
	bpy.utils.register_class(SubtitlesPanel)
	bpy.utils.register_class(ModifyIconOperator)
	bpy.utils.register_class(SubtitlesIconProperty)
	bpy.utils.register_class(SubtitlesProperties)
	bpy.utils.register_class(CqtcSubtitlesPreferences)
	bpy.types.Scene.subtitle = bpy.props.PointerProperty(type=SubtitlesProperties)


def unregister():
	bpy.utils.unregister_class(CreateSubtitleOperator)
	bpy.utils.unregister_class(AddSubtitleTemplateOperator)
	bpy.utils.unregister_class(LoadSubtitleTemplateOperator)
	bpy.utils.unregister_class(SetSubtitleTemplateNameOperator)
	bpy.utils.unregister_class(RemoveSubtitleTemplateOperator)
	bpy.utils.unregister_class(SubtitlesPanel)
	bpy.utils.unregister_class(ModifyIconOperator)
	bpy.utils.unregister_class(SubtitlesIconProperty)
	bpy.utils.unregister_class(SubtitlesProperties)
	bpy.utils.unregister_class(CqtcSubtitlesPreferences)
	del bpy.types.Scene.subtitle


if __name__ == "__main__":
	register()
