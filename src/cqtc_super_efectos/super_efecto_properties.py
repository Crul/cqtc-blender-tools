import bpy.ops
import bpy.props
import bpy.types
from .effects import *
from . import templates

effect_list = [
	NoEffect("no_effect"),
	FadeEffect("fade"),
	IrisInEffect("iris_in"),
	IrisOutEffect("iris_out"),
	ClockEffect("clock"),
	ClockAntiEffect("clock_anti"),
	SlideDownEffect("slide_down"),
	SlideUpEffect("slide_up"),
	SlideRightEffect("slide_right"),
	SlideLeftEffect("slide_left"),
	DoubleHorizontalSlideOpenEffect("double_horizontal_slide_open"),
	DoubleHorizontalSlideCloseEffect("double_horizontal_slide_close"),
	DoubleVerticalSlideOpenEffect("double_vertical_slide_open"),
	DoubleVerticalSlideCloseEffect("double_vertical_slide_close"),
]

def get_super_efecto_template_options(scene, context):
	return sorted(context.scene.super_efecto.template_options, key=lambda opt: opt[0].lower())
	
def load_template(self, context):
	bpy.ops.super_efecto.load_template()
	
class SuperEfectoProperties(bpy.types.PropertyGroup):
	
	effect_type = bpy.props.EnumProperty(
			name = "Efecto",
			description = "Tipo de efecto de la transición",
			default = effect_list[0].effect_key,
			items = [ (e.effect_key, e.name, e.description) for e in effect_list ]
		)
	
	config_expanded = bpy.props.BoolProperty(name="Configuración", default=True)
	
	effect_length_type = bpy.props.EnumProperty(
			name = "Tipo Duración",
			description = "Tipo de duración de la transición (frames o %)",
			default = "FRAMES",
			items = [
				("FRAMES", "En Frames", "Duración medida en frames"),
				("PERCENTAGE", "En Porcentaje", "Duración medida en porcentaje de la tira")
			]
		)
		
	effect_length = bpy.props.IntProperty(name="Duración del efecto", default=22, min=1, max=10000, step=5)
	effect_length_percentage = bpy.props.FloatProperty(name="Duración del efecto (%)", default=10, min=1, max=100, step=5, subtype="PERCENTAGE")
	
	apply_to_sound = bpy.props.BoolProperty(name="Aplicar al sonido", default=True)
	overlap_sound = bpy.props.BoolProperty(name="Superponer el sonido", default=False)
	
	color = bpy.props.FloatVectorProperty(name="Color", subtype="COLOR", default=(0.0, 0.0, 0.0), min=0.0, max=1.0, description="color picker")
	add_color_to_transition = bpy.props.BoolProperty(name="Con color", default=True)
	
	delay_image = bpy.props.IntProperty(name="Retrasar la imagen (frames)", default=0, min=0, max=500, step=1)
		
	initial_position_x = bpy.props.FloatProperty(name="Posición X Inicial", default=0, min=-1000, max=1000, step=5)
	position_x_animated = bpy.props.BoolProperty(name="Animar Posición X", default=False)
	final_position_x = bpy.props.FloatProperty(name="Posición X Final", default=0, min=-1000, max=1000, step=5)
	
	initial_position_y = bpy.props.FloatProperty(name="Posición Y Inicial", default=0, min=-1000, max=1000, step=5)
	position_y_animated = bpy.props.BoolProperty(name="Animar Posición Y", default=False)
	final_position_y = bpy.props.FloatProperty(name="Posición Y Final", default=0, min=-1000, max=1000, step=5)

	initial_zoom = bpy.props.FloatProperty(name="Zoom Inicial", default=1, min=0, max=100, step=1)
	zoom_animated = bpy.props.BoolProperty(name="Animar Zoom", default=False)
	final_zoom = bpy.props.FloatProperty(name="Zoom Final", default=1, min=0, max=100, step=1)
	
	initial_opacity = bpy.props.FloatProperty(name="Opacidad Inicial", default=1, min=0, max=1, step=0.1, subtype="FACTOR")
	opacity_animated = bpy.props.BoolProperty(name="Animar Opacidad", default=False)
	final_opacity = bpy.props.FloatProperty(name="Opacidad Final", default=1, min=0, max=1, step=0.1, subtype="FACTOR")
	
	initial_offset_x = bpy.props.FloatProperty(name="Offset X Inicial", default=0, min=-1000, max=1000, step=5)
	offset_x_animated = bpy.props.BoolProperty(name="Animar Offset X", default=False)
	final_offset_x = bpy.props.FloatProperty(name="Offset X Final", default=0, min=-1000, max=1000, step=5)
	
	initial_offset_y = bpy.props.FloatProperty(name="Offset Y Inicial", default=0, min=-1000, max=1000, step=5)
	offset_y_animated = bpy.props.BoolProperty(name="Animar Offset Y", default=False)
	final_offset_y = bpy.props.FloatProperty(name="Offset Y Final", default=0, min=-1000, max=1000, step=5)

	initial_blur_x = bpy.props.FloatProperty(name="Desenfoque X Inicial", default=0, min=-1000, max=1000, step=5)
	blur_x_animated = bpy.props.BoolProperty(name="Animar Desenfoque X", default=False)
	final_blur_x = bpy.props.FloatProperty(name="Desenfoque X Final", default=0, min=-1000, max=1000, step=5)
	
	initial_blur_y = bpy.props.FloatProperty(name="Desenfoque Y Inicial", default=0, min=-1000, max=1000, step=5)
	blur_y_animated = bpy.props.BoolProperty(name="Animar Desenfoque Y", default=False)
	final_blur_y = bpy.props.FloatProperty(name="Desenfoque Y Final", default=0, min=-1000, max=1000, step=5)

	constant_speed = bpy.props.BoolProperty(name="Velocidad constante", default=True)
	reverse_out_effect = bpy.props.BoolProperty(name="Invertir Efecto de Salida", default=True)
	mirror_horizontal_out_effect = bpy.props.BoolProperty(name="Voltear Horizontal Efecto de Salida", default=False)
	mirror_vertical_out_effect = bpy.props.BoolProperty(name="Voltear Vertical Efecto de Salida", default=False)
	
	image_alignment = bpy.props.EnumProperty(
			name = "Alinear Imágenes pequeñas",
			description = "Alineación de imágenes menores de 1920x1080",
			items = [
				("center", "Centro", "Imágenes centradas"),
				("bottom", "Abajo", "Imágenes alineadas con el borde inferior"),
				("top", "Arriba", "Imágenes alineadas con el borde superior"),
				("left", "Izquierda", "Imágenes alineadas con el borde izquierdo"),
				("right", "Derecha", "Imágenes alineadas con el borde derecho"),
				("bottom_left", "Abajo Izquierda", "Imágenes alineadas con la esquina inferior izquierda"),
				("bottom_right", "Abajo Derecha", "Imágenes alineadas con la esquina inferior derecha"),
				("top_left", "Arriba Izquierda", "Imágenes alineadas con la esquina superior izquierda"),
				("top_right", "Arriba Derecha", "Imágenes alineadas con la esquina superior derecha"),
			]
		)
	image_alignment_margin = bpy.props.IntProperty(name="Margen para imágenes", default=0, min=-1920, max=1920, step=10)
		
	template_expanded = bpy.props.BoolProperty(name="Plantillas", default=True)
	
	template = bpy.props.EnumProperty(
			name = "Plantillas",
			description = "Plantillas guardadas por el usuario",
			items = get_super_efecto_template_options,
			update = load_template
		)
	
	new_template_name = bpy.props.StringProperty(name="Nombre", description="Nombre para la nueva plantilla")
	override_template = bpy.props.BoolProperty(name="Sobreescribir Plantilla", default=False)
	
	template_data = templates.load_templates()
	template_options = [ (tmpl["name"], tmpl["name"], "Plantilla personalizada") for tmpl in template_data ]
	
	def get_effect(self):
		return [e for e in effect_list if e.effect_key == self.effect_type][0]
	
	def get_reversed_effect(self, effect):
		return [e for e in effect_list if e.effect_key == effect.reversed_effect][0]
	
	def is_transform_required(self):
		return ( \
			self.initial_position_x != 0 or \
			self.final_position_x != 0 or \
			self.position_x_animated or \
			self.initial_position_y != 0 or \
			self.final_position_y != 0 or \
			self.position_y_animated or \
			self.initial_zoom != 1 or \
			self.final_zoom != 1 or \
			self.zoom_animated or \
			self.initial_opacity != 1 or \
			self.final_opacity != 1 or \
			self.opacity_animated or \
			self.initial_offset_x != 0 or \
			self.final_offset_x != 0 or \
			self.offset_x_animated or \
			self.initial_offset_y != 0 or \
			self.final_offset_y != 0 or \
			self.offset_y_animated)
	
	def is_blur_required(self):
		return ( \
			self.initial_blur_x != 0 or \
			self.final_blur_x != 0 or \
			self.blur_x_animated or \
			self.initial_blur_y != 0 or \
			self.final_blur_y != 0 or \
			self.blur_y_animated)
	
	def to_dict(self):
		return {
			"effect_type": self.effect_type,                               
			"effect_length_type": self.effect_length_type,
			"effect_length": self.effect_length,
			"effect_length_percentage": self.effect_length_percentage,
			"apply_to_sound": self.apply_to_sound,
			"overlap_sound": self.overlap_sound,
			"color": (self.color.r, self.color.g, self.color.b),
			"add_color_to_transition": self.add_color_to_transition,
			"delay_image": self.delay_image,
			"initial_position_x": self.initial_position_x,
			"position_x_animated": self.position_x_animated,
			"final_position_x": self.final_position_x,
			"initial_position_y": self.initial_position_y,
			"position_y_animated": self.position_y_animated,
			"final_position_y": self.final_position_y,
			"initial_zoom": self.initial_zoom,
			"zoom_animated": self.zoom_animated,
			"final_zoom": self.final_zoom,
			"initial_opacity": self.initial_opacity,
			"opacity_animated": self.opacity_animated,
			"final_opacity": self.final_opacity,
			"initial_offset_x": self.initial_offset_x,
			"offset_x_animated": self.offset_x_animated,
			"final_offset_x": self.final_offset_x,
			"initial_offset_y": self.initial_offset_y,
			"offset_y_animated": self.offset_y_animated,
			"final_offset_y": self.final_offset_y,
			"initial_blur_x": self.initial_blur_x,
			"blur_x_animated": self.blur_x_animated,
			"final_blur_x": self.final_blur_x,
			"initial_blur_y": self.initial_blur_y,
			"blur_y_animated": self.blur_y_animated,
			"final_offset_y": self.final_offset_y,
			"constant_speed": self.constant_speed,
			"reverse_out_effect": self.reverse_out_effect,
			"mirror_horizontal_out_effect": self.mirror_horizontal_out_effect,
			"mirror_vertical_out_effect": self.mirror_vertical_out_effect,
			"image_alignment": self.image_alignment,
			"image_alignment_margin": self.image_alignment_margin,
		}
		
	def from_dict(self, tmpl):
		self.effect_type = tmpl["effect_type"]
		self.effect_length_type = tmpl["effect_length_type"] if ("effect_length_type" in tmpl) else "FRAMES" # TODO
		self.effect_length = tmpl["effect_length"]
		self.effect_length_percentage = tmpl["effect_length_percentage"] if ("effect_length_percentage" in tmpl) else 10 # TODO
		self.apply_to_sound = tmpl["apply_to_sound"]
		self.overlap_sound = tmpl["overlap_sound"]		
		self.color.r = tmpl["color"][0]
		self.color.g = tmpl["color"][1]
		self.color.b = tmpl["color"][2]
		self.delay_image = tmpl["delay_image"]
		self.add_color_to_transition = tmpl["add_color_to_transition"]
		self.initial_position_x = tmpl["initial_position_x"]
		self.position_x_animated = tmpl["position_x_animated"]
		self.final_position_x = tmpl["final_position_x"]
		self.initial_position_y = tmpl["initial_position_y"]
		self.position_y_animated = tmpl["position_y_animated"]
		self.final_position_y = tmpl["final_position_y"]
		self.initial_zoom = tmpl["initial_zoom"]
		self.zoom_animated = tmpl["zoom_animated"]
		self.final_zoom = tmpl["final_zoom"]
		self.initial_opacity = tmpl["initial_opacity"]
		self.opacity_animated = tmpl["opacity_animated"]
		self.final_opacity = tmpl["final_opacity"]
		self.initial_offset_x = tmpl["initial_offset_x"]
		self.offset_x_animated = tmpl["offset_x_animated"]
		self.final_offset_x = tmpl["final_offset_x"]
		self.initial_offset_y = tmpl["initial_offset_y"]
		self.offset_y_animated = tmpl["offset_y_animated"]
		self.final_offset_y = tmpl["final_offset_y"]
		self.initial_blur_x = tmpl["initial_blur_x"] if ("initial_blur_x" in tmpl) else 0 # TODO
		self.blur_x_animated = tmpl["blur_x_animated"] if ("blur_x_animated" in tmpl) else False # TODO
		self.final_blur_x = tmpl["final_blur_x"] if ("final_blur_x" in tmpl) else 0 # TODO
		self.initial_blur_y = tmpl["initial_blur_y"] if ("initial_blur_y" in tmpl) else 0 # TODO
		self.blur_y_animated = tmpl["blur_y_animated"] if ("blur_y_animated" in tmpl) else 0 # TODO
		self.final_blur_y = tmpl["final_blur_y"] if ("final_blur_y" in tmpl) else 0 # TODO
		self.constant_speed = tmpl["constant_speed"]
		self.reverse_out_effect = tmpl["reverse_out_effect"] if ("reverse_out_effect" in tmpl) else True # TODO
		self.mirror_horizontal_out_effect = tmpl["mirror_horizontal_out_effect"] if ("mirror_horizontal_out_effect" in tmpl) else False # TODO
		self.mirror_vertical_out_effect = tmpl["mirror_vertical_out_effect"] if ("mirror_vertical_out_effect" in tmpl) else False # TODO
		#self.image_alignment = tmpl["image_alignment"] if ("image_alignment" in tmpl) else "center" # TODO
		#self.image_alignment_margin = tmpl["image_alignment_margin"] if ("image_alignment_margin" in tmpl) else 0 # TODO
		
		return self
