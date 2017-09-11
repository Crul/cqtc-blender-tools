import cqtc_bpy

global_scale_x = 1920
global_scale_y = int(global_scale_x * (1080/1920))		
effectable_strip_types = ["COLOR","IMAGE","MOVIE","SCENE","TRANSFORM","CROSS","GAUSSIAN_BLUR"]
transitionable_strip_types = ["COLOR","IMAGE","MOVIE","SCENE","TRANSFORM","CROSS","GAUSSIAN_BLUR"]
sound_capable_strip_types = ["COLOR","IMAGE","MOVIE","TRANSFORM","CROSS","GAUSSIAN_BLUR"]

class SuperEffectCreator():
	
	def create(self, context, operation_type):
		error = self.__validate_global(context, operation_type)
		if error:
			return error
		
		for sequence in context.selected_sequences.copy():
			cqtc_bpy.unselect_children(sequence)
			cqtc_bpy.align_image(context, sequence)
		
		for in_or_out in ["IN", "OUT"]:
			if (in_or_out in operation_type):
				error = self.__create_in_or_out_effect(context, in_or_out)
				if error:
					return error
		
		if (operation_type == "TRANSITION"):
			error = self.__create_transition(context)
			if error:
				return error
	
	
	def __validate_global(self, context, operation_type):
		is_effect_length_percentage_over_limit = (operation_type == "IN_OUT" 
			and context.scene.super_effect.effect_length_type == "PERCENTAGE"
			and context.scene.super_effect.effect_length_percentage > 50)
		
		if is_effect_length_percentage_over_limit:
			return "No se puede crear un efecto de Entrada y Salida con más del 50% de porcentage de duración"
	
	
	def __validate_in_or_out_effect(self, context, is_in):

		selected_not_sound_sequences = [s for s in context.selected_sequences if s.type in effectable_strip_types]
		if len(selected_not_sound_sequences) == 0:
			return "Debes seleccionar al menos una strip que no sea de tipo sonido"
		
		effect_length = context.scene.super_effect.effect_length
		delay_image = context.scene.super_effect.delay_image
		if context.scene.super_effect.effect_length_type == "FRAMES":
			min_length = effect_length
			if is_in:
				min_length += delay_image
				
			for sequence in selected_not_sound_sequences:
				if sequence.frame_final_duration < min_length:
					return "La strip " + sequence.name + " es más corta de lo necesario para añdir el efecto"
			
		selected_sound_capable_sequences = [s for s in context.selected_sequences if s.type in sound_capable_strip_types]
		selected_sound_sequences = [s for s in context.selected_sequences if s.type == "SOUND"]
		if len(selected_sound_sequences) > len(selected_sound_capable_sequences):
			return "No puedes seleccionar más strips de sonido que strips de imagen, vídeo o transform"

		for selected_sound_sequence in selected_sound_sequences:
			not_sound_sequence_matches = [ nss for nss in selected_sound_capable_sequences \
				if (nss.frame_final_start == selected_sound_sequence.frame_final_start \
					or nss.frame_final_end == selected_sound_sequence.frame_final_end)]
					
			if len(not_sound_sequence_matches) == 0:
				return "La strip de sonido " + selected_sound_sequence.name + " no corresponde con ninguna strip de imagen, vídeo o transform"
	
	
	def __validate_transition(self, context):
		selected_not_sound_sequences = [s for s in context.selected_sequences if s.type in transitionable_strip_types]
		if len(selected_not_sound_sequences) != 2:
			return "Debes seleccionar dos (y SOLO dos) strips que no sean de sonido"
			
		selected_sound_sequences = [s for s in context.selected_sequences if s.type == "SOUND"]
		if len(selected_sound_sequences) > 2:
			return "Puedes seleccionar dos strips de sonido como máximo"
			
		for selected_sound_sequence in selected_sound_sequences:
			selected_sound_capable_sequences = [s for s in context.selected_sequences if s.type in sound_capable_strip_types]
			not_sound_sequence_matches = [ nss for nss in selected_sound_capable_sequences \
				if (nss.frame_final_start == selected_sound_sequence.frame_final_start \
					and nss.frame_final_end == selected_sound_sequence.frame_final_end)]
					
			if len(not_sound_sequence_matches) == 0:
				return "La strip de sonido " + selected_sound_sequence.name + " no corresponde con ninguna strip de imagen, vídeo"
			
		if context.scene.super_effect.effect_length_type == "PERCENTAGE":
			return "No se puede añadir una transición con una duración de tipo porcentaje"
		
		strip_tmp_1 = selected_not_sound_sequences[0]
		strip_tmp_2 = selected_not_sound_sequences[1]
		if (strip_tmp_1.frame_final_start == strip_tmp_2.frame_final_start and strip_tmp_1.frame_final_end == strip_tmp_2.frame_final_end):
			return "Para añadir una transición las tiras no pueden estar en la misma posición"
	
	
	def __validate_transition_without_color(self, context, seq1, seq2, seq1_sound, seq2_sound):
		if seq1.frame_final_end < seq2.frame_final_start:
			return "Para añadir una transición sin color intermedio las tiras deben solaparse o ser consecutivas"
			
		if seq1.frame_final_end == seq2.frame_final_start:
			return cqtc_bpy.overlap_strips(context, seq1, seq2, seq1_sound, seq2_sound)
	
	
	def __validate_transition_with_color(self, seq1, seq2):
		if seq1.frame_final_end > seq2.frame_final_start:
			return "Para añadir una transición con color intermedio las tiras no pueden solaparse"
	
	
	def __create_in_or_out_effect(self, context, in_or_out):
		is_in = (in_or_out == "IN")
		error = self.__validate_in_or_out_effect(context, is_in)
		if error:
			return error

		effect = context.scene.super_effect.get_effect()
		if (not is_in) and context.scene.super_effect.reverse_out_effect:
			effect = context.scene.super_effect.get_reversed_effect(effect)
		
		selected_sequences = context.selected_sequences.copy()			
		for sequence in selected_sequences:
			self.__create_in_or_out_strip_effect(context, effect, is_in, sequence)
	
	
	def __create_in_or_out_strip_effect(self, context, effect, is_in, sequence):

		delay_image = context.scene.super_effect.delay_image
		effect_length = context.scene.super_effect.effect_length \
			if context.scene.super_effect.effect_length_type == "FRAMES" \
			else int(context.scene.super_effect.effect_length_percentage * sequence.frame_final_duration / 100)
		
		if is_in:
			start_frame = sequence.frame_final_start
			final_frame = sequence.frame_final_start + effect_length
				
		else:
			start_frame = sequence.frame_final_end - effect_length
			final_frame = sequence.frame_final_end
		
		if context.scene.super_effect.apply_to_sound:
			self.__apply_effect_sound_transition(sequence, start_frame, final_frame, effect_length, is_in)
	
		if sequence.type in effectable_strip_types:
			original_sequence = sequence
			sequence = self.__add_transform_strip(context, sequence, start_frame, final_frame, is_in)
			sequence = self.__add_blur_strip(context, sequence, start_frame, final_frame, is_in)
			
			color_final_frame = final_frame
			if is_in:
				 color_final_frame += delay_image
				 
			channel = cqtc_bpy.get_available_channel_in_position(context, start_frame, color_final_frame, sequence.channel)
			color_strip = effect.create_color_strip(context, channel, start_frame, color_final_frame, original_sequence.name)
			
			seq1 = color_strip if is_in else sequence
			seq2 = sequence if is_in else color_strip
			if is_in:
				 original_sequence.frame_offset_start += delay_image
				 
			channel = cqtc_bpy.get_available_channel_in_position(context, start_frame, final_frame, channel)
			effect_strip = effect.create_effect_strip(context, channel, start_frame, final_frame, seq1, seq2, original_sequence.name)
		
			original_sequence.select = False
			sequence.select = True
	
	
	def __create_transition(self, context):
		error = self.__validate_transition(context)
		if error:
			return error

		selected_not_sound_sequences = [s for s in context.selected_sequences if s.type in transitionable_strip_types]
		strip_tmp_1 = selected_not_sound_sequences[0]
		strip_tmp_2 = selected_not_sound_sequences[1]
		
		is_seq1_before_seq2 = (strip_tmp_1.frame_final_start < strip_tmp_2.frame_final_start)
		seq1 = strip_tmp_1 if is_seq1_before_seq2 else strip_tmp_2
		seq2 = strip_tmp_2 if is_seq1_before_seq2 else strip_tmp_1
		
		(seq1_sound, seq2_sound) = self.__get_transition_sound_sequences(context, seq1, seq2)
			
		if context.scene.super_effect.add_color_to_transition:
			return self.__create_transition_with_color(context, seq1, seq2, seq1_sound, seq2_sound)
			
		else:
			return self.__create_transition_without_color(context, seq1, seq2, seq1_sound, seq2_sound)
	
	
	def __create_transition_without_color(self, context, seq1, seq2, seq1_sound, seq2_sound):
		error = self.__validate_transition_without_color(context, seq1, seq2, seq1_sound, seq2_sound)
		if error:
			return error
			
		start_frame = seq2.frame_final_start
		final_frame = seq1.frame_final_end
			
		seq1 = self.__add_blur_strip(context, seq1, start_frame, final_frame, is_in=False)
		seq1 = self.__add_transform_strip(context, seq1, start_frame, final_frame, is_in=False)
		seq2 = self.__add_blur_strip(context, seq2, start_frame, final_frame, is_in=True)
		seq2 = self.__add_transform_strip(context, seq2, start_frame, final_frame, is_in=True)
		
		effect = context.scene.super_effect.get_effect()
		
		max_channel = max([s.channel for s in context.selected_sequences])
		channel = cqtc_bpy.get_available_channel_in_position(context, start_frame, final_frame, max_channel)
		effect_strip = effect.create_effect_strip(context, channel, start_frame, final_frame, seq1, seq2)
						
		if context.scene.super_effect.apply_to_sound:
			self.__apply_overlapped_sound_transition(context, seq1_sound, seq2_sound, start_frame, final_frame)
	
	
	def __create_transition_with_color(self, context, seq1, seq2, seq1_sound, seq2_sound):
		error = self.__validate_transition_with_color(seq1, seq2)
		if error:
			return error
	
		effect_length = context.scene.super_effect.effect_length
		half_effect_length = int(effect_length / 2)
		
		start_frame = seq1.frame_final_end - half_effect_length
		final_frame = seq2.frame_final_start + half_effect_length
		delay_image = context.scene.super_effect.delay_image
		effect = context.scene.super_effect.get_effect()

		seq1 = self.__add_blur_strip(context, seq1, start_frame, seq1.frame_final_end, is_in=False)
		seq1 = self.__add_transform_strip(context, seq1, start_frame, seq1.frame_final_end, is_in=False)
		seq2 = self.__add_blur_strip(context, seq2, seq2.frame_final_start, final_frame, is_in=True)
		seq2 = self.__add_transform_strip(context, seq2, seq2.frame_final_start, final_frame, is_in=True)

		color_channel = cqtc_bpy.get_available_channel_in_position(context, start_frame, final_frame + delay_image, max(seq1.channel, seq2.channel))
		color_strip = effect.create_color_strip(context, color_channel, start_frame, final_frame + delay_image)
		
		seq1_effect = effect if not context.scene.super_effect.reverse_out_effect \
			else context.scene.super_effect.get_reversed_effect(effect)
		
		channel = cqtc_bpy.get_available_channel_in_position(context, start_frame, seq1.frame_final_end, color_channel)
		effect_strip = seq1_effect.create_effect_strip(context, channel, start_frame, seq1.frame_final_end, seq1, color_strip)
		
		channel = cqtc_bpy.get_available_channel_in_position(context, seq2.frame_final_start, final_frame + delay_image, color_channel)
		effect_strip = effect.create_effect_strip(context, channel, seq2.frame_final_start, final_frame + delay_image, color_strip, seq2)
		
		seq2.frame_offset_start += delay_image
		
		if context.scene.super_effect.apply_to_sound:
			self.__apply_consecutive_sound_transition(seq1_sound, seq2_sound, start_frame, final_frame, half_effect_length)
	
	
	def __add_transform_strip(self, context, sequence, start_frame, final_frame, is_in):
		is_transform_required = context.scene.super_effect.is_transform_required()
		if not is_transform_required:
			return sequence

		selected_keyframes = cqtc_bpy.deselect_selected_keyframe_points(context)
		(sequence, sequence_to_return) = self.__create_or_get_existing_effect_strip(sequence, context, "TRANSFORM", "_Transform")
		
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
		self.__set_animatable_properties(context, animatable_properties_info, is_in, start_frame, final_frame)
		
		cqtc_bpy.set_interpolation_type(context)
		cqtc_bpy.select_keyframe_points(context, selected_keyframes)
		
		return sequence_to_return
	
	
	def __add_blur_strip(self, context, sequence, start_frame, final_frame, is_in):
		is_blur_required = context.scene.super_effect.is_blur_required()
		if not is_blur_required:
			return sequence
		
		selected_keyframes = cqtc_bpy.deselect_selected_keyframe_points(context)
		(sequence, sequence_to_return) = self.__create_or_get_existing_effect_strip(sequence, context, "GAUSSIAN_BLUR", "_Blur")

		animatable_properties_info = [ (sequence, "size_x", "blur_x", {}), (sequence, "size_y", "blur_y", {}) ]
		self.__set_animatable_properties(context, animatable_properties_info, is_in, start_frame, final_frame)
		
		cqtc_bpy.set_interpolation_type(context)
		cqtc_bpy.select_keyframe_points(context, selected_keyframes)
		
		return sequence_to_return
	
	
	def __apply_effect_sound_transition(self, seq_sound, start_frame, final_frame, effect_length, is_in):
		initial_volume = 0 if is_in else 1
		final_volume = 1 if is_in else 0
			
		if seq_sound.type == "SOUND":
			volume_start_frame = start_frame
			volume_final_frame = final_frame

			cqtc_bpy.animate_volume(seq_sound, initial_volume, final_volume, volume_start_frame, volume_final_frame)

		elif seq_sound.type == "SCENE":
			if is_in:
				volume_start_frame = 1
				volume_final_frame = effect_length + 1
			else:
				volume_start_frame = seq_sound.scene.frame_end - effect_length
				volume_final_frame = seq_sound.scene.frame_end
			
			cqtc_bpy.animate_volume(seq_sound, initial_volume, final_volume, volume_start_frame, volume_final_frame)
	
	
	def __apply_consecutive_sound_transition(self, seq1_sound, seq2_sound, start_frame, final_frame, half_effect_length):
		if seq1_sound is not None:
			if seq1_sound.type == "SOUND":
				seq1_volume_start_frame = start_frame
				seq1_volume_final_frame = seq1_sound.frame_final_end
			elif seq1_sound.type == "SCENE":
				seq1_volume_start_frame = seq1_sound.scene.frame_end - half_effect_length
				seq1_volume_final_frame = seq1_sound.scene.frame_end
			
			cqtc_bpy.animate_volume(seq1_sound, 1, 0, seq1_volume_start_frame, seq1_volume_final_frame)
				
		if seq2_sound is not None:
			if seq2_sound.type == "SOUND":
				seq2_volume_start_frame = seq2_sound.frame_final_start
				seq2_volume_final_frame = final_frame
			elif seq2_sound.type == "SCENE":
				seq2_volume_start_frame = 1
				seq2_volume_final_frame = half_effect_length + 1
			
			cqtc_bpy.animate_volume(seq2_sound, 0, 1, seq2_volume_start_frame, seq2_volume_final_frame)
	
	
	def __apply_overlapped_sound_transition(self, context, seq1_sound, seq2_sound, start_frame, final_frame):
		if context.scene.super_effect.overlap_sound:
		
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
			cqtc_bpy.animate_volume(seq1_sound, 1, 0, seq1_volume_start_frame, seq1_volume_final_frame)
		
		if seq2_sound is not None:
			cqtc_bpy.animate_volume(seq2_sound, 0, 1, seq2_volume_start_frame, seq2_volume_final_frame)
	
	
	def __create_or_get_existing_effect_strip(self, sequence, context, effect_type, effect_name_suffix):
		sequence.blend_type = "ALPHA_OVER"
		
		is_effect_strip = (sequence.type == effect_type)
		if is_effect_strip:
			return sequence, sequence
		
		is_effect_strip_child = (("input_1" in dir(sequence))
			and (sequence.input_1 is not None and sequence.input_1.type == effect_type))
		
		if is_effect_strip_child:
			sequence_to_return = sequence
			sequence = sequence.input_1
			
		else:
			original_sequence = sequence
			channel = cqtc_bpy.get_available_channel_in_position(context, original_sequence.frame_final_start, original_sequence.frame_final_end, original_sequence.channel)
			sequence = context.scene.sequence_editor.sequences.new_effect(
					original_sequence.name + effect_name_suffix,
					effect_type,
					channel,
					original_sequence.frame_final_start,
					original_sequence.frame_final_end,
					original_sequence)
			
			sequence.blend_type = "ALPHA_OVER"
			
			original_sequence.select = False
			sequence_to_return = sequence
			
		return sequence, sequence_to_return
	
	
	def __get_transition_sound_sequences(self, context, seq1, seq2):
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

		return (seq1_sound, seq2_sound)
	
	
	def __set_animatable_properties(self, context, animatable_properties_info, is_in, start_frame, final_frame):
		delay_image = context.scene.super_effect.delay_image
		if is_in:
			start_frame += delay_image
			final_frame += delay_image
		
		for obj, seq_attr, super_effect_prop, options in animatable_properties_info:
			is_horizontal_mirrorable = "is_horizontal_mirrorable" in options
			is_vertical_mirrorable = "is_vertical_mirrorable" in options
			get_value_fn = options["get_value_fn"] if "get_value_fn" in options else lambda value : value
			
			self.__set_animatable_property(context,
				obj,
				seq_attr,
				super_effect_prop,
				start_frame,
				final_frame,
				is_in,
				is_horizontal_mirrorable=is_horizontal_mirrorable,
				is_vertical_mirrorable=is_vertical_mirrorable,
				get_value_fn=get_value_fn)
	
	
	def __set_animatable_property(self,
		context,
		obj,
		seq_attr,
		super_effect_prop,
		start_frame,
		end_frame,
		is_in,
		is_vertical_mirrorable=False,
		is_horizontal_mirrorable=False,
		get_value_fn=lambda value : value
	):
		initial_value = get_value_fn(getattr(context.scene.super_effect, "initial_%s" % super_effect_prop))
		final_value = get_value_fn(getattr(context.scene.super_effect, "final_%s" % super_effect_prop))
		is_animated_value = getattr(context.scene.super_effect, "%s_animated" % super_effect_prop)
		
		setattr(obj, seq_attr, initial_value)		
		if not is_animated_value:
			return
	
		is_reversed =  ((not is_in) and context.scene.super_effect.reverse_out_effect)
		is_horizontal_mirrored = (is_horizontal_mirrorable and (not is_in) and context.scene.super_effect.mirror_horizontal_out_effect)
		is_vertical_mirrored = (is_vertical_mirrorable and(not is_in) and context.scene.super_effect.mirror_vertical_out_effect)
		
		if is_reversed:
			setattr(obj, seq_attr, final_value)

		if is_horizontal_mirrored or is_vertical_mirrored:
			setattr(obj, seq_attr, -getattr(obj, seq_attr))
			
		obj.keyframe_insert(seq_attr, index=-1, frame=start_frame)
		
		setattr(obj, seq_attr, final_value if not is_reversed else initial_value)
		
		if is_horizontal_mirrored or is_vertical_mirrored:
			setattr(obj, seq_attr, -getattr(obj, seq_attr))
			
		obj.keyframe_insert(seq_attr, index=-1, frame=end_frame)