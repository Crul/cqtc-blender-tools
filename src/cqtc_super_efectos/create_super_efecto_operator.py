import bpy

tmp_channel = 30
global_scale_x = 1920
global_scale_y = int(global_scale_x * (1080/1920))

class CreateSuperEfectoOperator(bpy.types.Operator):
	bl_idname = "super_efecto.create"
	bl_label = "Crear Transición"
	operation_type =  bpy.props.StringProperty()
	
	def execute(self, context):
		result = {"FINISHED"}
		
		is_effect_length_percentage_over_limit = (self.operation_type == "IN_OUT" and context.scene.super_efecto.effect_length_type == "PERCENTAGE" and context.scene.super_efecto.effect_length_percentage > 50)
		if is_effect_length_percentage_over_limit:
			self.report({"ERROR"}, "No se puede crear un efecto de Entrada y Salida con más del 50% de porcentage de duración" )
			return {"CANCELLED"}
		
		for sequence in context.selected_sequences.copy():
			self.unselect_children(sequence)
			self.align_image(context, sequence)
					
		if ("IN" in self.operation_type):
			result = self.create_in_or_out_effect(context, "IN")
		
		if "CANCELLED" in result:
			return result
		
		if ("OUT" in self.operation_type):
			result = self.create_in_or_out_effect(context, "OUT")
		
		if "CANCELLED" in result:
			return result
		
		if (self.operation_type == "TRANSITION"):
			result = self.create_transition(context)
		
		return result
	
	
	def create_in_or_out_effect(self, context, in_or_out):
		is_in = (in_or_out == "IN")
		
		effectable_types = ["COLOR","IMAGE","MOVIE","SCENE","TRANSFORM","CROSS","GAUSSIAN_BLUR"]
		selected_not_sound_sequences = [s for s in context.selected_sequences if s.type in effectable_types]
		if len(selected_not_sound_sequences) == 0:
			self.report({"ERROR"}, "Debes seleccionar al menos una strip que no sea de tipo sonido" )
			return {"CANCELLED"}
		
		effect_length = context.scene.super_efecto.effect_length
		delay_image = context.scene.super_efecto.delay_image
		if context.scene.super_efecto.effect_length_type == "FRAMES":
			min_length = effect_length
			if is_in:
				min_length += delay_image
				
			for sequence in selected_not_sound_sequences:
				if sequence.frame_final_duration < min_length:
					self.report({"ERROR"}, "La strip " + sequence.name + " es más corta de lo necesario para añdir el efecto")
					return {"CANCELLED"}
			
		selected_sound_capable_sequences = [s for s in context.selected_sequences if s.type in ["COLOR","IMAGE","MOVIE","TRANSFORM","CROSS","GAUSSIAN_BLUR"]]
		selected_sound_sequences = [s for s in context.selected_sequences if s.type == "SOUND"]
		if len(selected_sound_sequences) > len(selected_sound_capable_sequences):
			self.report({"ERROR"}, "No puedes seleccionar más strips de sonido que strips de imagen, vídeo o transform" )
			return {"CANCELLED"}

		for selected_sound_sequence in selected_sound_sequences:
			not_sound_sequence_matches = [ nss for nss in selected_sound_capable_sequences \
				if (nss.frame_final_start == selected_sound_sequence.frame_final_start \
					or nss.frame_final_end == selected_sound_sequence.frame_final_end)]
					
			if len(not_sound_sequence_matches) == 0:
				self.report({"ERROR"}, "La strip de sonido " + selected_sound_sequence.name + " no corresponde con ninguna strip de imagen, vídeo o transform" )
				return {"CANCELLED"}
		
		initial_volume = 0 if is_in else 1
		final_volume = 1 if is_in else 0
			
		effect = context.scene.super_efecto.get_effect()
		if (not is_in) and context.scene.super_efecto.reverse_out_effect:
			effect = context.scene.super_efecto.get_reversed_effect(effect)
		
		selected_sequences = context.selected_sequences.copy()			
		for sequence in selected_sequences:
		
			if context.scene.super_efecto.effect_length_type == "PERCENTAGE":
				effect_length = int(context.scene.super_efecto.effect_length_percentage * sequence.frame_final_duration / 100)
			
			if is_in:
				start_frame = sequence.frame_final_start
				final_frame = sequence.frame_final_start + effect_length
					
			else:
				start_frame = sequence.frame_final_end - effect_length
				final_frame = sequence.frame_final_end
			
			if context.scene.super_efecto.apply_to_sound:
				if sequence.type == "SOUND":
					self.animate_volume(sequence, initial_volume, final_volume, start_frame, final_frame)
				elif sequence.type == "SCENE":
					if is_in:
						scene_volume_start_frame = 1
						scene_volume_final_frame = effect_length + 1
					else:
						scene_volume_start_frame = sequence.scene.frame_end - effect_length
						scene_volume_final_frame = sequence.scene.frame_end
						
					self.animate_volume(sequence, initial_volume, final_volume, scene_volume_start_frame, scene_volume_final_frame)
		
			if sequence.type in effectable_types:
				original_sequence = sequence
				sequence = self.add_transform_strip(context, sequence, start_frame, final_frame, is_in)
				sequence = self.add_blur_strip(context, sequence, start_frame, final_frame, is_in)
				
				color_final_frame = final_frame
				if is_in:
					 color_final_frame += delay_image
					 
				channel = self.get_available_channel(context, start_frame, color_final_frame, sequence.channel)
				
				color_strip = effect.create_color_strip(context, channel, start_frame, color_final_frame, original_sequence.name)
				seq1 = color_strip if is_in else sequence
				seq2 = sequence if is_in else color_strip
				if is_in:
					 original_sequence.frame_offset_start += delay_image
					 
				channel = self.get_available_channel(context, start_frame, final_frame, channel)
				effect_strip = effect.create_effect_strip(context, channel, start_frame, final_frame, seq1, seq2, original_sequence.name)
			
				original_sequence.select = False
				sequence.select = True
				
			
		return {"FINISHED"}
	
	
	def create_transition(self, context):
		transitionable_types = ["COLOR","IMAGE","MOVIE","SCENE","TRANSFORM","CROSS","GAUSSIAN_BLUR"]
		selected_not_sound_sequences = [s for s in context.selected_sequences if s.type in transitionable_types]
		if len(selected_not_sound_sequences) != 2:
			self.report({"ERROR"}, "Debes seleccionar dos (y SOLO dos) strips que no sean de sonido" )
			return {"CANCELLED"}
			
		selected_sound_sequences = [s for s in context.selected_sequences if s.type == "SOUND"]
		if len(selected_sound_sequences) > 2:
			self.report({"ERROR"}, "Puedes seleccionar dos strips de sonido como máximo" )
			return {"CANCELLED"}
			
		for selected_sound_sequence in selected_sound_sequences:
			selected_sound_capable_sequences = [s for s in context.selected_sequences if s.type in ["COLOR","IMAGE","MOVIE","TRANSFORM","CROSS","GAUSSIAN_BLUR"]]
			not_sound_sequence_matches = [ nss for nss in selected_sound_capable_sequences \
				if (nss.frame_final_start == selected_sound_sequence.frame_final_start \
					and nss.frame_final_end == selected_sound_sequence.frame_final_end)]
					
			if len(not_sound_sequence_matches) == 0:
				self.report({"ERROR"}, "La strip de sonido " + selected_sound_sequence.name + " no corresponde con ninguna strip de imagen, vídeo" )
				return {"CANCELLED"}
			
		if context.scene.super_efecto.effect_length_type == "PERCENTAGE":
			self.report({"ERROR"}, "No se puede añadir una transición con una duración de tipo porcentaje" )
			return {"CANCELLED"}
		
		strip_tmp_1 = selected_not_sound_sequences[0]
		strip_tmp_2 = selected_not_sound_sequences[1]
		if strip_tmp_1.frame_final_start < strip_tmp_2.frame_final_start:
			seq1 = strip_tmp_1
			seq2 = strip_tmp_2
		else:
			seq1 = strip_tmp_2
			seq2 = strip_tmp_1
			
		if (seq1.frame_final_start == seq2.frame_final_start and seq1.frame_final_end == seq2.frame_final_end):
			self.report({"ERROR"}, "Para añadir una transición las tiras no pueden estar en la misma posición" )
			return {"CANCELLED"}
		
		seq1_sound = None
		seq2_sound = None
		selected_soundable_sequences = [s for s in context.selected_sequences if s.type in ["SOUND", "SCENE"] ]
		for selected_soundable_sequence in selected_soundable_sequences:
			if (selected_soundable_sequence.frame_final_start == seq1.frame_final_start \
				and selected_soundable_sequence.frame_final_end == seq1.frame_final_end):
				seq1_sound = selected_soundable_sequence
			
			if (selected_soundable_sequence.frame_final_start == seq2.frame_final_start \
				and selected_soundable_sequence.frame_final_end == seq2.frame_final_end):
				seq2_sound = selected_soundable_sequence
			
		if context.scene.super_efecto.add_color_to_transition:
			return self.create_transition_with_color(context, seq1, seq2, seq1_sound, seq2_sound)
			
		else:
			return self.create_transition_without_color(context, seq1, seq2, seq1_sound, seq2_sound)
	
	
	def create_transition_without_color(self, context, seq1, seq2, seq1_sound, seq2_sound):
		if seq1.frame_final_end < seq2.frame_final_start:
			self.report({"ERROR"}, "Para añadir una transición sin color intermedio las tiras deben solaparse o ser consecutivas" )
			return {"CANCELLED"}
			
		if seq1.frame_final_end == seq2.frame_final_start:
			overlap_sucess = self.overlap_strips(context, seq1, seq2, seq1_sound, seq2_sound)
			if not overlap_sucess:
				return {"CANCELLED"}
			
		start_frame = seq2.frame_final_start
		final_frame = seq1.frame_final_end
			
		seq1 = self.add_blur_strip(context, seq1, start_frame, final_frame, is_in=False)
		seq1 = self.add_transform_strip(context, seq1, start_frame, final_frame, is_in=False)
		seq2 = self.add_blur_strip(context, seq2, start_frame, final_frame, is_in=True)
		seq2 = self.add_transform_strip(context, seq2, start_frame, final_frame, is_in=True)
		
		effect = context.scene.super_efecto.get_effect()
		
		max_channel = max([s.channel for s in context.selected_sequences])
		channel = self.get_available_channel(context, start_frame, final_frame, max_channel)
		effect_strip = effect.create_effect_strip(context, channel, start_frame, final_frame, seq1, seq2)
						
		if context.scene.super_efecto.apply_to_sound:
		
			if context.scene.super_efecto.overlap_sound:
				effect_length = (final_frame - start_frame)
				if seq1_sound is not None:
					if seq1_sound.type == "SOUND":
						seq1_volume_start_frame = start_frame
						seq1_volume_final_frame = final_frame
					elif seq1_sound.type == "SCENE":
						seq1_volume_start_frame = seq1_sound.scene.frame_end - effect_length
						seq1_volume_final_frame = seq1_sound.scene.frame_end
				
				if seq2_sound is not None:
					if seq2_sound.type == "SOUND":
						seq2_volume_start_frame = start_frame
						seq2_volume_final_frame = final_frame
					elif seq2_sound.type == "SCENE":
						seq2_volume_start_frame = 1
						seq2_volume_final_frame = 1 + effect_length
					
			else:
				effect_length = (final_frame - start_frame)
				half_effect_length = int(effect_length / 2)
				medium_frame = start_frame + half_effect_length
				
				if seq1_sound is not None:
					if seq1_sound.type == "SOUND":
						seq1_volume_start_frame = start_frame
						seq1_volume_final_frame = medium_frame
					elif seq1_sound.type == "SCENE":
						seq1_volume_start_frame = seq1_sound.scene.frame_end - effect_length
						seq1_volume_final_frame = seq1_sound.scene.frame_end - half_effect_length
					
				if seq2_sound is not None:
					if seq2_sound.type == "SOUND":
						seq2_volume_start_frame = medium_frame
						seq2_volume_final_frame = final_frame
					elif seq2_sound.type == "SCENE":
						seq2_volume_start_frame = half_effect_length
						seq2_volume_final_frame = effect_length
					
			
			if seq1_sound is not None:
				self.animate_volume(seq1_sound, 1, 0, seq1_volume_start_frame, seq1_volume_final_frame)
			
			if seq2_sound is not None:
				self.animate_volume(seq2_sound, 0, 1, seq2_volume_start_frame, seq2_volume_final_frame)
		
		return {"FINISHED"}
	
	
	def create_transition_with_color(self, context, seq1, seq2, seq1_sound, seq2_sound):
	
		effect_length = context.scene.super_efecto.effect_length
		half_effect_length = int(effect_length / 2)
		
		if seq1.frame_final_end > seq2.frame_final_start:
			self.report({"ERROR"}, "Para añadir una transición con color intermedio las tiras no pueden solaparse" )
			return {"CANCELLED"}
		
		start_frame = seq1.frame_final_end - half_effect_length
		final_frame = seq2.frame_final_start + half_effect_length
		delay_image = context.scene.super_efecto.delay_image
		effect = context.scene.super_efecto.get_effect()

		seq1 = self.add_blur_strip(context, seq1, start_frame, seq1.frame_final_end, is_in=False)
		seq1 = self.add_transform_strip(context, seq1, start_frame, seq1.frame_final_end, is_in=False)
		seq2 = self.add_blur_strip(context, seq2, seq2.frame_final_start, final_frame, is_in=True)
		seq2 = self.add_transform_strip(context, seq2, seq2.frame_final_start, final_frame, is_in=True)

		color_channel = self.get_available_channel(context, start_frame, final_frame + delay_image, max(seq1.channel, seq2.channel))
		color_strip = effect.create_color_strip(context, color_channel, start_frame, final_frame + delay_image)
		
		channel = self.get_available_channel(context, start_frame, seq1.frame_final_end, color_channel)
		if context.scene.super_efecto.reverse_out_effect:	
			reversed_effect = context.scene.super_efecto.get_reversed_effect(effect)
			effect_strip = reversed_effect.create_effect_strip(context, channel, start_frame, seq1.frame_final_end, seq1, color_strip)
		else:
			effect_strip = effect.create_effect_strip(context, channel, start_frame, seq1.frame_final_end, seq1, color_strip)
		
		channel = self.get_available_channel(context, seq2.frame_final_start, final_frame + delay_image, color_channel)
		effect_strip = effect.create_effect_strip(context, channel, seq2.frame_final_start, final_frame + delay_image, color_strip, seq2)
		
		seq2.frame_offset_start += delay_image
						
		if context.scene.super_efecto.apply_to_sound:
			if seq1_sound is not None:
				if seq1_sound.type == "SOUND":
					self.animate_volume(seq1_sound, 1, 0, start_frame, seq1_sound.frame_final_end)
				elif seq1_sound.type == "SCENE":
					scene_volume_start_frame = seq1_sound.scene.frame_end - half_effect_length
					scene_volume_final_frame = seq1_sound.scene.frame_end
					self.animate_volume(seq1_sound, 1, 0, scene_volume_start_frame, scene_volume_final_frame)
				
			if seq2_sound is not None:
				if seq2_sound.type == "SOUND":
					self.animate_volume(seq2_sound, 0, 1, seq2_sound.frame_final_start, final_frame)
				elif seq2_sound.type == "SCENE":
					scene_volume_start_frame = 1
					scene_volume_final_frame = half_effect_length + 1
					self.animate_volume(seq2_sound, 0, 1, scene_volume_start_frame, scene_volume_final_frame)
				
		return {"FINISHED"}
	
	
	def add_transform_strip(self, context, sequence, start_frame, final_frame, is_in):
		is_transform_required = context.scene.super_efecto.is_transform_required()
		if not is_transform_required:
			return sequence

		selected_keyframes = self.deselect_selected_keyframe_points(context)
		(sequence, sequence_to_return) = self.create_or_get_existing_effect_strip(sequence, context, "TRANSFORM", "_Transform")
		
		sequence.use_uniform_scale = True
		sequence.use_translation = True
		
		original_offset_x = sequence.transform.offset_x
		get_offset_x_fn = lambda value : (original_offset_x + (global_scale_x * value / 100))
		original_offset_y = sequence.transform.offset_y
		get_offset_y_fn = lambda value : (original_offset_y + (global_scale_y * value / 100))
		
		animatable_properties_info = [
			(sequence, "translate_start_x", "position_x", {"is_horizontal_mirrorable"}),
			(sequence, "translate_start_y", "position_y", {"is_vertical_mirrorable"}),
			(sequence, "scale_start_x", "zoom", {}),
			(sequence, "blend_alpha", "opacity", {}),
			(sequence.transform, "offset_x", "offset_x", {"is_horizontal_mirrorable": True, "get_value_fn": get_offset_x_fn }),
			(sequence.transform, "offset_y", "offset_y", {"is_vertical_mirrorable": True, "get_value_fn": get_offset_y_fn })
		]
		self.set_animatable_properties(context, animatable_properties_info, is_in, start_frame, final_frame)
		
		self.set_interpolation_type(context)
		self.reselect_keyframe_points(context, selected_keyframes)
		
		return sequence_to_return
	
	
	def add_blur_strip(self, context, sequence, start_frame, final_frame, is_in):
		is_blur_required = context.scene.super_efecto.is_blur_required()
		if not is_blur_required:
			return sequence
		
		selected_keyframes = self.deselect_selected_keyframe_points(context)
		(sequence, sequence_to_return) = self.create_or_get_existing_effect_strip(sequence, context, "GAUSSIAN_BLUR", "_Blur")

		animatable_properties_info = [ (sequence, "size_x", "blur_x", {}), (sequence, "size_y", "blur_y", {}) ]
		self.set_animatable_properties(context, animatable_properties_info, is_in, start_frame, final_frame)
		
		self.set_interpolation_type(context)
		self.reselect_keyframe_points(context, selected_keyframes)
		
		return sequence_to_return
		
		
	def create_or_get_existing_effect_strip(self, sequence, context, effect_type, effect_name_suffix):
		sequence.blend_type = 'ALPHA_OVER'
		
		is_gaussian_blur = (sequence.type == effect_type)
		if is_gaussian_blur:
			return sequence, sequence
	
		is_child_gaussian_blur = ("input_1" in dir(sequence) and sequence.input_1 is not None and sequence.input_1.type ==effect_type)
		if is_child_gaussian_blur:
			sequence_to_return = sequence
			sequence = sequence.input_1
			
		else:
			original_sequence = sequence
			channel = self.get_available_channel(context, original_sequence.frame_final_start, original_sequence.frame_final_end, original_sequence.channel)
			sequence = context.scene.sequence_editor.sequences.new_effect( \
					original_sequence.name + effect_name_suffix, \
					effect_type, \
					channel, \
					original_sequence.frame_final_start, \
					original_sequence.frame_final_end, \
					original_sequence)
			
			sequence.blend_type = 'ALPHA_OVER'
			
			original_sequence.select = False
			sequence_to_return = sequence
			
		return sequence, sequence_to_return

	
	def set_animatable_properties(self, context, animatable_properties_info, is_in, start_frame, final_frame):
		delay_image = context.scene.super_efecto.delay_image
		if is_in:
			start_frame += delay_image
			final_frame += delay_image
		
		for obj, seq_attr, super_efecto_prop, options in animatable_properties_info:
			is_horizontal_mirrorable = "is_horizontal_mirrorable" in options
			is_vertical_mirrorable = "is_vertical_mirrorable" in options
			get_value_fn = options["get_value_fn"] if "get_value_fn" in options else lambda value : value
			
			self.set_animatable_property(context,
				obj,
				seq_attr,
				super_efecto_prop,
				start_frame,
				final_frame,
				is_in,
				is_horizontal_mirrorable=is_horizontal_mirrorable,
				is_vertical_mirrorable=is_vertical_mirrorable,
				get_value_fn=get_value_fn)
		
		
	def set_animatable_property(self,
		context,
		obj,
		seq_attr,
		super_efecto_prop,
		start_frame,
		end_frame,
		is_in,
		is_vertical_mirrorable=False,
		is_horizontal_mirrorable=False,
		get_value_fn=lambda value : value
	):
		initial_value = get_value_fn(getattr(context.scene.super_efecto, "initial_%s" % super_efecto_prop))
		final_value = get_value_fn(getattr(context.scene.super_efecto, "final_%s" % super_efecto_prop))
		is_animated_value = getattr(context.scene.super_efecto, "%s_animated" % super_efecto_prop)
		
		setattr(obj, seq_attr, initial_value)		
		if not is_animated_value:
			return
	
		is_reversed =  ((not is_in) and context.scene.super_efecto.reverse_out_effect)
		is_horizontal_mirrored = (is_horizontal_mirrorable and (not is_in) and context.scene.super_efecto.mirror_horizontal_out_effect)
		is_vertical_mirrored = (is_vertical_mirrorable and(not is_in) and context.scene.super_efecto.mirror_vertical_out_effect)
		
		if is_reversed:
			setattr(obj, seq_attr, final_value)

		if is_horizontal_mirrored or is_vertical_mirrored:
			setattr(obj, seq_attr, -getattr(obj, seq_attr))
			
		obj.keyframe_insert(seq_attr, index=-1, frame=start_frame)
		
		setattr(obj, seq_attr, final_value if not is_reversed else initial_value)
		
		if is_horizontal_mirrored or is_vertical_mirrored:
			setattr(obj, seq_attr, -getattr(obj, seq_attr))
			
		obj.keyframe_insert(seq_attr, index=-1, frame=end_frame)
	
	
	def overlap_strips(self, context, seq1, seq2, seq1_sound, seq2_sound):
		effect_length = context.scene.super_efecto.effect_length
		
		while(seq1.type in ["TRANSFORM","CROSS","GAUSSIAN_BLUR"]):
			seq1 = seq1.input_1
		
		while(seq2.type in ["TRANSFORM","CROSS","GAUSSIAN_BLUR"]):
			seq2 = seq2.input_1
		
		if seq1.type in ["MOVIE","SCENE"]:
			not_enough_data_after_seq1 = (seq1.frame_offset_end < effect_length)
			if not_enough_data_after_seq1:
				self.report({"ERROR"}, "No hay suficientes datos después del final en la tira " + seq1.name )
				return False
		
		if seq2.type in ["MOVIE","SCENE"]:
			not_enough_data_before_seq2 = (seq2.frame_offset_start < effect_length)
			if not_enough_data_before_seq2:
				self.report({"ERROR"}, "No hay suficientes datos antes del comianzo en la tira " + seq2.name )
				return False
		
		seq1_channel = seq1.channel
		seq1.channel = tmp_channel
		seq1.channel = self.get_available_channel(context, seq1.frame_final_start, seq1.frame_final_end + effect_length, seq1_channel)
		seq1.frame_final_end += effect_length
		
		if seq1_sound is not None:
			seq1_sound_channel = seq1_sound.channel
			seq1_sound.channel = tmp_channel
			seq1_sound.channel = self.get_available_channel(context, seq1.frame_final_start, seq1.frame_final_end + effect_length, seq1_sound_channel)
			seq1_sound.frame_final_end += effect_length

		seq2_channel = seq2.channel
		seq2.channel = tmp_channel
		seq2.channel = self.get_available_channel(context, seq2.frame_final_start - effect_length, seq2.frame_final_end, seq2_channel)
		seq2.frame_final_start -= effect_length
		
		if seq2_sound is not None:
			seq2_sound_channel = seq2_sound.channel
			seq2_sound.channel = tmp_channel
			seq2_sound.channel = self.get_available_channel(context, seq2.frame_final_start - effect_length, seq2.frame_final_end, seq2_sound_channel)
			seq2_sound.frame_final_start -= effect_length
		
		return True
	
	
	def animate_volume(self, seq_sound, initial_volume, final_volume, initial_frame, final_frame):
		if (hasattr(seq_sound, "volume")):
			seq_sound.volume = initial_volume
			seq_sound.keyframe_insert("volume", index=-1, frame=initial_frame)
			
			seq_sound.volume = final_volume
			seq_sound.keyframe_insert("volume", index=-1, frame=final_frame)
		else:
			seq_sound.scene.audio_volume = initial_volume
			seq_sound.scene.keyframe_insert("audio_volume", index=-1, frame=initial_frame)
			
			seq_sound.scene.audio_volume = final_volume
			seq_sound.scene.keyframe_insert("audio_volume", index=-1, frame=final_frame)
		
	
	def unselect_children(self, sequence):
		if 'input_1' not in dir(sequence) or sequence.input_1 is None:
			return
			
		self.unselect_children(sequence.input_1)
		sequence.input_1.select = False
	
	
	def align_image(self, context, sequence):
		if sequence.type != "IMAGE" or len(sequence.elements) == 0:
			return
			
		image_element = sequence.elements[0]
		if image_element.orig_width == context.scene.render.resolution_x and image_element.orig_height == context.scene.render.resolution_y:
			return
	
		image_alignment = context.scene.super_efecto.image_alignment
		image_alignment_margin = context.scene.super_efecto.image_alignment_margin
		
		sequence.use_translation = True
		sequence.blend_type = 'ALPHA_OVER'
		sequence.transform.offset_x = (context.scene.render.resolution_x/2 - image_element.orig_width/2)
		sequence.transform.offset_y = (context.scene.render.resolution_y/2 - image_element.orig_height/2)
			
		if "bottom" in image_alignment:
			sequence.transform.offset_y = image_alignment_margin
			
		if "top" in image_alignment:
			sequence.transform.offset_y = context.scene.render.resolution_y - image_element.orig_height - image_alignment_margin
			
		if "left" in image_alignment:
			sequence.transform.offset_x = image_alignment_margin
			
		if "right" in image_alignment:
			sequence.transform.offset_x = context.scene.render.resolution_x - image_element.orig_width - image_alignment_margin

	
	def get_available_channel(self, context, start_frame, final_frame, start_channel=1):
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
		
		
	def deselect_selected_keyframe_points(self, context):
		if context.scene.animation_data is None:
			context.scene.animation_data_create()
		
		selected_keyframes = []
		if context.scene.animation_data.action is None:
			return selected_keyframes
		
		for i, fcurve in context.scene.animation_data.action.fcurves.items():
			for j, keyframe_point in fcurve.keyframe_points.items():
				if keyframe_point.select_control_point:
					keyframe_point.select_control_point = False
					selected_keyframes.append((i, j))

		return selected_keyframes

		
	def reselect_keyframe_points(self, context, selected_keyframes):
		if context.scene.animation_data.action is None:
			return
			
		for i, fcurve in context.scene.animation_data.action.fcurves.items():
			for j, keyframe_point in fcurve.keyframe_points.items():
				if (i, j) in selected_keyframes:
					keyframe_point.select_control_point = True

		
	def set_interpolation_type(self, context):
		if context.scene.animation_data.action is None:
			return
		
		old_area_type = context.area.type
		context.area.type = 'GRAPH_EDITOR'
		context.scene.update()

		try:
			if context.scene.super_efecto.constant_speed:
				bpy.ops.graph.interpolation_type(type='LINEAR')
			else:
				bpy.ops.graph.interpolation_type(type='BEZIER')
		except: 
			pass
			
		context.area.type = old_area_type
		context.scene.update()
		