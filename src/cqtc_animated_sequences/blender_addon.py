import bpy.props
import bpy.types
import bpy.utils
from .animated_sequence_panel import AnimatedSequencePanel
from .animated_sequence_properties import AnimatedSequenceProperties
from .create_animated_sequence_operator import CreateAnimatedSequenceOperator
from . import locale


def register(name):
	bpy.utils.register_class(CreateAnimatedSequenceOperator)
	bpy.utils.register_class(AnimatedSequencePanel)
	bpy.utils.register_class(AnimatedSequenceProperties)
	bpy.types.Scene.animated_sequence = bpy.props.PointerProperty(type=AnimatedSequenceProperties)
	bpy.app.translations.register(name, locale.translations)


def unregister(name):
	bpy.utils.unregister_class(CreateAnimatedSequenceOperator)
	bpy.utils.unregister_class(AnimatedSequencePanel)
	bpy.utils.unregister_class(AnimatedSequenceProperties)
	del bpy.types.Scene.animated_sequence
	bpy.app.translations.unregister(name)

if __name__ == "__main__":
	register(__name__)
