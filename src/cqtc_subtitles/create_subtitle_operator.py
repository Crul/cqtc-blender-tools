import bpy
import os
from cqtc_operator import CqtcOperator

scene_prefix = "tx"
global_scale_x = 1920
global_scale_y = global_scale_x * (1080/1920)

camera_position_z = 10
camera_ortho_scale = global_scale_x

light_position_z  = 10
bgr_position_z = -0.1

class CreateSubtitleOperator(CqtcOperator):
	bl_idname = "subtitle.create"
	bl_label = "Crear subitulos"
	bl_options = {"REGISTER", "UNDO"}
	
	def execute(self, context):
		error = self.validate_data(context) 
		if error:
			return self.return_error(error)
		
		context.scene.subtitle.scene_name = scene_prefix + context.scene.subtitle.scene_name
		
		text_scene = self.create_subtitle(context)
		self.create_strip(context, text_scene)
		
		context.scene.subtitle.scene_name = ""
		context.scene.subtitle.text = ""
		
		return {"FINISHED"}
	
	
	def validate_data(self, context):
		scene_name = context.scene.subtitle.scene_name
		if ((scene_prefix + scene_name) in bpy.data.scenes):
			return "Ya existe una escena llamada " + (scene_prefix + scene_name)
		
		text = context.scene.subtitle.text
		if (scene_name == "" or text == ""):
			return "Debe indicar el nombre de la escena y el texto del subtítulo."
			
		font_path = context.scene.subtitle.font_path
		if font_path != "" and not os.path.isfile(font_path):
			return "No se ha encontrado el fichero " + font_path
	
	
	def create_subtitle(self, context):	
		current_scene = context.scene
		
		scene_name = context.scene.subtitle.scene_name
		text = context.scene.subtitle.text
		position = context.scene.subtitle.position
		font_path = context.scene.subtitle.font_path
		font_color = context.scene.subtitle.font_color
		font_size = context.scene.subtitle.font_size
		font_spacing = context.scene.subtitle.font_spacing
		create_bgr = context.scene.subtitle.create_bgr
		bgr_color = context.scene.subtitle.bgr_color
		bgr_alpha = context.scene.subtitle.bgr_alpha / 100
		width = context.scene.subtitle.width / 100
		internal_margin = context.scene.subtitle.internal_margin
		external_margin = context.scene.subtitle.external_margin
		
		text_scene = bpy.data.scenes.new(scene_name)
		text_scene.render.alpha_mode = "TRANSPARENT"
		context.screen.scene = text_scene
		
		old_area_type = context.area.type
		context.area.type = "VIEW_3D"
		
		bpy.ops.object.text_add()		
		txt_object = context.object
		
		if font_path != "":
			font = bpy.data.fonts.load(font_path)
			txt_object.data.font = font
		
		txt_object.data.size = font_size
		txt_object.data.space_line = font_spacing
		if ("right" in position):
			txt_object.data.align_x = "RIGHT"
		elif ("left" in position):
			txt_object.data.align_x = "LEFT"
		else:
			txt_object.data.align_x = "CENTER"
		
		txt_object.data.body = text
		
		context.scene.update()
		
		max_text_width = width * global_scale_x
		text_width = min(txt_object.dimensions.x, max_text_width)
		
		if text_width == max_text_width:
			txt_object.data.text_boxes[0].width = text_width
			txt_position_x = -(text_width/2)
		else:
			if ("right" in position):
				txt_position_x = +(text_width/2)
			elif ("left" in position):
				txt_position_x = -(text_width/2)
			else:
				txt_position_x = 0
		
		txt_object.location = txt_position_x, 0, 0
				
		font_material = self.make_material("font_material", font_color, (1,1,1), 1)
		txt_object.data.materials.append(font_material)
		
		context.scene.update()
		
		bgr_dimensions_y = txt_object.dimensions.y + (2 * internal_margin)
		if create_bgr:	
			bpy.ops.mesh.primitive_plane_add(location=(0,0,bgr_position_z))
			bgr_object = context.object
			bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
			
			bgr_dimensions_x = text_width + (2 * internal_margin)
			bgr_dimensions_z = bgr_object.dimensions.z
			bgr_object.dimensions = bgr_dimensions_x, bgr_dimensions_y, bgr_dimensions_z
			
			bgr_material = self.make_material("bgr_material", bgr_color, (1,1,1), bgr_alpha)
			bgr_object.show_transparent = True
			bgr_object.data.materials.append(bgr_material)
		
		delta_x = 0
		delta_y = 0
		if ("top" in position):
			delta_y = (global_scale_y / 2 - (external_margin * 2)) - (bgr_dimensions_y / 2)
		
		if ("bottom" in position):
			delta_y = -((global_scale_y / 2 - (external_margin * 2)) - (bgr_dimensions_y / 2))
		
		if ("right" in position):
			delta_x = (global_scale_x / 2 - (external_margin * 2)) - (bgr_dimensions_x / 2)
		
		if ("left" in position):
			delta_x = -((global_scale_x / 2 - (external_margin * 2)) - (bgr_dimensions_x / 2))
		
		txt_object.location.x += delta_x
		txt_object.location.y += delta_y
		if create_bgr:
			bgr_object.location.x += delta_x
			bgr_object.location.y += delta_y
		
		bpy.ops.object.camera_add()
		context.object.location.z = camera_position_z
		context.object.data.type = "ORTHO"
		context.object.data.ortho_scale = camera_ortho_scale
		
		lamp_data = bpy.data.lamps.new(name="New Lamp", type="SUN")
		lamp_object = bpy.data.objects.new(name="New Lamp", object_data=lamp_data)
		text_scene.objects.link(lamp_object)
		lamp_object.location = (0, 0, light_position_z)
		lamp_object.data.energy = 1
		
		context.scene.update()
		
		error_y = (txt_object.bound_box[0][1] + txt_object.bound_box[2][1]) / 2
		txt_object.location.y -= error_y
		
		context.area.type = old_area_type
		context.screen.scene = current_scene
		
		return text_scene
	
	
	def create_strip(self, context, text_scene):
		if not context.scene.subtitle.create_strip:
			return
		
		scene_name = context.scene.subtitle.scene_name
		strip_channel = context.scene.subtitle.strip_channel
		strip_length = context.scene.subtitle.strip_length
		current_frame = context.screen.scene.frame_current
		
		if context.scene.sequence_editor is None:
			context.scene.sequence_editor_create()
			
		available_channel = self.getAvailableChannel(context, current_frame, current_frame + strip_length)
		text_strip = context.scene.sequence_editor.sequences.new_scene(scene_name, text_scene, available_channel, current_frame)
			
		text_strip.blend_type = "ALPHA_OVER"
		text_strip.frame_final_end = current_frame + strip_length
	
	
	def make_material(self, name, diffuse, specular, alpha):
		mat = bpy.data.materials.new(name)
		mat.diffuse_color = diffuse
		mat.diffuse_shader = "LAMBERT" 
		mat.diffuse_intensity = 1.0 
		mat.specular_color = specular
		mat.specular_shader = "COOKTORR"
		mat.specular_intensity = 0
		mat.alpha = alpha
		mat.ambient = 1
		mat.transparency_method = "Z_TRANSPARENCY"   
		mat.use_transparency = True
		
		return mat
	
	
	def getAvailableChannel(self, context, start_frame, final_frame, start_channel=1):
		if context.scene.sequence_editor is None:
			context.scene.sequence_editor_create()
			
		max_channel = 20
		for channel in range(start_channel, max_channel):
			is_channel_available = True
			for sequence in context.scene.sequence_editor.sequences:
				is_sequence_in_channel_and_interval = (sequence.channel == channel \
					and sequence.frame_final_start < final_frame \
					and sequence.frame_final_end > start_frame)
					
				if is_sequence_in_channel_and_interval:
					is_channel_available = False
					break
					
			if is_channel_available:
				return channel
				
		return max_channel
