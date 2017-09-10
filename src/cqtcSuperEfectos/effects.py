import bpy
from abc import ABCMeta


class SuperEffect:
	metaclass__ = ABCMeta
	name = ""
	effect_key = ""
	effect_name = ""
	description = ""
	reversed_effect = ""
	
	def __init__(self, effect_key, effect_name, name, description, reversed_effect=None):
		self.effect_key = effect_key
		self.effect_name = effect_name
		self.name = name
		self.description = description
		if reversed_effect is None:
			self.reversed_effect = effect_key
		else:
			self.reversed_effect = reversed_effect
	
	
	def getNamePrefix(self, name_prefix):
		if (name_prefix != ""):
			name_prefix += "_"
			
		return name_prefix
	
	
	def createColorStrip(self, context, channel, start_frame, final_frame, name_prefix=""):
		color_strip = context.scene.sequence_editor.sequences \
			.new_effect(self.getNamePrefix(name_prefix) + "Color", \
						"COLOR", \
						channel, \
						start_frame, \
						frame_end=final_frame)
		
		color_strip.select = False
		color_strip.blend_type = 'ALPHA_OVER'
		color_strip.color = context.scene.super_efecto.color
		
		return color_strip
	
	
	def createEffectStrip(self, context, channel, start_frame, final_frame, seq1, seq2, name_prefix=""):
		effect_strip = context.scene.sequence_editor.sequences \
			.new_effect(self.getNamePrefix(name_prefix) + self.name, \
						self.effect_name, 
						channel, \
						start_frame, \
						frame_end=final_frame, \
						seq1=seq1, \
						seq2=seq2)
		
		effect_strip.select = False
		effect_strip.blend_type = 'ALPHA_OVER'
		
		return self.customizeEffectStrip(effect_strip)
	
		
	def customizeEffectStrip(self, effect_strip):
		return effect_strip

class NoEffect(SuperEffect):

	def __init__(self, effect_key):
		super().__init__(effect_key, "", "Sin efecto", "Sin efecto")
	
	def createEffectStrip(self, context, channel, start_frame, final_frame, seq1, seq2, name_prefix=""):
		return (seq1 if seq1 is not None else seq2)
		
	def createColorStrip(self, context, channel, start_frame, final_frame, name_prefix=""):
		return None
		
class FadeEffect(SuperEffect):

	def __init__(self, effect_key):
		super().__init__(effect_key, "CROSS", "Fundido", "Transición de opacidad")
	
class WipeEffect(SuperEffect):
	metaclass__ = ABCMeta
	transition_type = ""
	direction = ""

	def __init__(self, effect_key, transition_type, direction, name, description, reversed_effect):
		super().__init__(effect_key, "WIPE", name, description, reversed_effect)
		self.transition_type = transition_type
		self.direction = direction
	
	def customizeEffectStrip(self, effect_strip):
		effect_strip.transition_type = self.transition_type
		effect_strip.direction = self.direction
	
		return effect_strip
	
class RotatedWipeEffect(WipeEffect):

	def customizeEffectStrip(self, effect_strip):
		effect_strip = super().customizeEffectStrip(effect_strip)
		effect_strip.angle = 1.5708 # radians ?
	
		return effect_strip
	
class IrisInEffect(WipeEffect):

	def __init__(self, effect_key):
		name = "Cortinilla circular grande > pequeña"
		description = "Transición mostrando la imagen mediante una cortinilla circular que se expande desde el centro"
		reversed_effect = "iris_out"
		super().__init__(effect_key, "IRIS", "IN", name, description, reversed_effect)

class IrisOutEffect(WipeEffect):

	def __init__(self, effect_key):
		name = "Cortinilla circular pequeña > grande"
		description = "Transición mostrando la imagen mediante una cortinilla circular que se contrae hacia el centro"
		reversed_effect = "iris_in"
		super().__init__(effect_key, "IRIS", "OUT", name, description, reversed_effect)

class ClockEffect(WipeEffect):

	def __init__(self, effect_key):
		name = "Cortinilla en forma de reloj (sentido horario)"
		description = "Transición mostrando la imagen mediante una cortinilla giratoria"
		reversed_effect = "clock_anti"
		super().__init__(effect_key, "CLOCK", "IN", name, description, reversed_effect)

class ClockAntiEffect(WipeEffect):

	def __init__(self, effect_key):
		name = "Cortinilla en forma de reloj (sentido anti-horario)"
		description = "Transición mostrando la imagen mediante una cortinilla giratoria"
		reversed_effect = "clock"
		super().__init__(effect_key, "CLOCK", "OUT", name, description, reversed_effect)
		
class SlideUpEffect(WipeEffect):

	def __init__(self, effect_key):
		name = "Cortinilla hacia arriba"
		description = "Transición mostrando la imagen mediante una cortinilla de abajo hacia arriba"
		reversed_effect = "slide_down"
		super().__init__(effect_key, "SINGLE", "IN", name, description, reversed_effect)
		
class SlideDownEffect(WipeEffect):

	def __init__(self, effect_key):
		name = "Cortinilla hacia abajo"
		description = "Transición mostrando la imagen mediante una cortinilla de arriba hacia abajo"
		reversed_effect = "slide_up"
		super().__init__(effect_key, "SINGLE", "OUT", name, description, reversed_effect)

class SlideRightEffect(RotatedWipeEffect):

	def __init__(self, effect_key):
		name = "Cortinilla hacia la derecha"
		description = "Transición mostrando la imagen mediante una cortinilla de derecha a izquierda"
		reversed_effect = "slide_left"
		super().__init__(effect_key, "SINGLE", "IN", name, description, reversed_effect)
		
	def customizeEffectStrip(self, effect_strip):
		effect_strip = super().customizeEffectStrip(effect_strip)
		effect_strip.angle = 1.5708 # radians ?
	
		return effect_strip
		
class SlideLeftEffect(RotatedWipeEffect):

	def __init__(self, effect_key):
		name = "Cortinilla hacia la izquierda"
		description = "Transición mostrando la imagen mediante una cortinilla de izquierda a derecha"
		reversed_effect = "slide_right"
		super().__init__(effect_key, "SINGLE", "OUT", name, description, reversed_effect)
		
class DoubleHorizontalSlideOpenEffect(WipeEffect):

	def __init__(self, effect_key):
		name = "Doble cortinilla horizontal abriéndose"
		description = "Transición mostrando la imagen mediante una doble cortinilla horizontal que se expande desde el centro"
		reversed_effect = "double_horizontal_slide_close"
		super().__init__(effect_key, "DOUBLE", "OUT", name, description, reversed_effect)
		
class DoubleHorizontalSlideCloseEffect(WipeEffect):

	def __init__(self, effect_key):
		name = "Doble cortinilla horizontal cerrándose"
		description = "Transición mostrando la imagen mediante una doble cortinilla horizontal que se contrae hacia el centro"
		reversed_effect = "double_horizontal_slide_open"
		super().__init__(effect_key, "DOUBLE", "IN", name, description, reversed_effect)
		
class DoubleVerticalSlideOpenEffect(RotatedWipeEffect):

	def __init__(self, effect_key):
		name = "Doble cortinilla vertical abriéndose"
		description = "Transición mostrando la imagen mediante una doble cortinilla vertical que se expande desde el centro"
		reversed_effect = "double_vertical_slide_close"
		super().__init__(effect_key, "DOUBLE", "OUT", name, description, reversed_effect)
		
class DoubleVerticalSlideCloseEffect(RotatedWipeEffect):

	def __init__(self, effect_key):
		name = "Doble cortinilla vertical cerrándose"
		description = "Transición mostrando la imagen mediante una doble cortinilla vertical que se contrae hacia el centro"
		reversed_effect = "double_vertical_slide_open"
		super().__init__(effect_key, "DOUBLE", "IN", name, description, reversed_effect)

