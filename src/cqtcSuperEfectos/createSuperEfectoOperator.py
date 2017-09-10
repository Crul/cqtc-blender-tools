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
		
		if (self.operation_type == "IN_OUT" and context.scene.super_efecto.effect_length_type == "PERCENTAGE" and context.scene.super_efecto.effect_length_percentage > 50):
			self.report({"ERROR"}, "No se puede crear un efecto de Entrada y Salida con más del 50% de porcentage de duración" )
			return {"CANCELLED"}
		
		for sequence in context.selected_sequences.copy():
			self.unselectChildren(sequence)
			self.alignImage(context, sequence)
					
		if ("IN" in self.operation_type):
			result = self.createInOrOutEffect(context, "IN")
		
		if "CANCELLED" in result:
			return result
		
		if ("OUT" in self.operation_type):
			result = self.createInOrOutEffect(context, "OUT")
		
		if "CANCELLED" in result:
			return result
		
		if (self.operation_type == "TRANSITION"):
			result = self.createTransition(context)
		
		return result
	
	
	def createInOrOutEffect(self, context, in_or_out):
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
			
		effect = context.scene.super_efecto.getEffect()
		if (not is_in) and context.scene.super_efecto.reverse_out_effect:
			effect = context.scene.super_efecto.getReversedEffect(effect)
		
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
					self.animateVolume(sequence, initial_volume, final_volume, start_frame, final_frame)
				elif sequence.type == "SCENE":
					if is_in:
						scene_volume_start_frame = 1
						scene_volume_final_frame = effect_length + 1
					else:
						scene_volume_start_frame = sequence.scene.frame_end - effect_length
						scene_volume_final_frame = sequence.scene.frame_end
						
					self.animateVolume(sequence, initial_volume, final_volume, scene_volume_start_frame, scene_volume_final_frame)
		
			if sequence.type in effectable_types:
				original_sequence = sequence
				sequence = self.addTransformStrip(context, sequence, start_frame, final_frame, is_in)
				sequence = self.addBlurStrip(context, sequence, start_frame, final_frame, is_in)
				
				color_final_frame = final_frame
				if is_in:
					 color_final_frame += delay_image
					 
				channel = self.getAvailableChannel(context, start_frame, color_final_frame, sequence.channel)
				
				color_strip = effect.createColorStrip(context, channel, start_frame, color_final_frame, original_sequence.name)
				seq1 = color_strip if is_in else sequence
				seq2 = sequence if is_in else color_strip
				if is_in:
					 original_sequence.frame_offset_start += delay_image
					 
				channel = self.getAvailableChannel(context, start_frame, final_frame, channel)
				effect_strip = effect.createEffectStrip(context, channel, start_frame, final_frame, seq1, seq2, original_sequence.name)
			
				original_sequence.select = False
				sequence.select = True
				
			
		return {"FINISHED"}
	
	
	def createTransition(self, context):
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
			return self.createTransitionWithColor(context, seq1, seq2, seq1_sound, seq2_sound)
			
		else:
			return self.createTransitionWithoutColor(context, seq1, seq2, seq1_sound, seq2_sound)
	
	
	def createTransitionWithoutColor(self, context, seq1, seq2, seq1_sound, seq2_sound):
		if seq1.frame_final_end < seq2.frame_final_start:
			self.report({"ERROR"}, "Para añadir una transición sin color intermedio las tiras deben solaparse o ser consecutivas" )
			return {"CANCELLED"}
			
		if seq1.frame_final_end == seq2.frame_final_start:
			overlap_sucess = self.overlapStrips(context, seq1, seq2, seq1_sound, seq2_sound)
			if not overlap_sucess:
				return {"CANCELLED"}
			
		start_frame = seq2.frame_final_start
		final_frame = seq1.frame_final_end
			
		seq1 = self.addBlurStrip(context, seq1, start_frame, final_frame, is_in=False)
		seq1 = self.addTransformStrip(context, seq1, start_frame, final_frame, is_in=False)
		seq2 = self.addBlurStrip(context, seq2, start_frame, final_frame, is_in=True)
		seq2 = self.addTransformStrip(context, seq2, start_frame, final_frame, is_in=True)
		
		effect = context.scene.super_efecto.getEffect()
		
		max_channel = max([s.channel for s in context.selected_sequences])
		channel = self.getAvailableChannel(context, start_frame, final_frame, max_channel)
		effect_strip = effect.createEffectStrip(context, channel, start_frame, final_frame, seq1, seq2)
						
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
				self.animateVolume(seq1_sound, 1, 0, seq1_volume_start_frame, seq1_volume_final_frame)
			
			if seq2_sound is not None:
				self.animateVolume(seq2_sound, 0, 1, seq2_volume_start_frame, seq2_volume_final_frame)
		
		return {"FINISHED"}
	
	
	def createTransitionWithColor(self, context, seq1, seq2, seq1_sound, seq2_sound):
	
		effect_length = context.scene.super_efecto.effect_length
		half_effect_length = int(effect_length / 2)
		
		if seq1.frame_final_end > seq2.frame_final_start:
			self.report({"ERROR"}, "Para añadir una transición con color intermedio las tiras no pueden solaparse" )
			return {"CANCELLED"}
		
		start_frame = seq1.frame_final_end - half_effect_length
		final_frame = seq2.frame_final_start + half_effect_length
		delay_image = context.scene.super_efecto.delay_image
		effect = context.scene.super_efecto.getEffect()

		seq1 = self.addBlurStrip(context, seq1, start_frame, seq1.frame_final_end, is_in=False)
		seq1 = self.addTransformStrip(context, seq1, start_frame, seq1.frame_final_end, is_in=False)
		seq2 = self.addBlurStrip(context, seq2, seq2.frame_final_start, final_frame, is_in=True)
		seq2 = self.addTransformStrip(context, seq2, seq2.frame_final_start, final_frame, is_in=True)

		color_channel = self.getAvailableChannel(context, start_frame, final_frame + delay_image, max(seq1.channel, seq2.channel))
		color_strip = effect.createColorStrip(context, color_channel, start_frame, final_frame + delay_image)
		
		channel = self.getAvailableChannel(context, start_frame, seq1.frame_final_end, color_channel)
		if context.scene.super_efecto.reverse_out_effect:	
			reversed_effect = context.scene.super_efecto.getReversedEffect(effect)
			effect_strip = reversed_effect.createEffectStrip(context, channel, start_frame, seq1.frame_final_end, seq1, color_strip)
		else:
			effect_strip = effect.createEffectStrip(context, channel, start_frame, seq1.frame_final_end, seq1, color_strip)
		
		channel = self.getAvailableChannel(context, seq2.frame_final_start, final_frame + delay_image, color_channel)
		effect_strip = effect.createEffectStrip(context, channel, seq2.frame_final_start, final_frame + delay_image, color_strip, seq2)
		
		seq2.frame_offset_start += delay_image
						
		if context.scene.super_efecto.apply_to_sound:
			if seq1_sound is not None:
				if seq1_sound.type == "SOUND":
					self.animateVolume(seq1_sound, 1, 0, start_frame, seq1_sound.frame_final_end)
				elif seq1_sound.type == "SCENE":
					scene_volume_start_frame = seq1_sound.scene.frame_end - half_effect_length
					scene_volume_final_frame = seq1_sound.scene.frame_end
					self.animateVolume(seq1_sound, 1, 0, scene_volume_start_frame, scene_volume_final_frame)
				
			if seq2_sound is not None:
				if seq2_sound.type == "SOUND":
					self.animateVolume(seq2_sound, 0, 1, seq2_sound.frame_final_start, final_frame)
				elif seq2_sound.type == "SCENE":
					scene_volume_start_frame = 1
					scene_volume_final_frame = half_effect_length + 1
					self.animateVolume(seq2_sound, 0, 1, scene_volume_start_frame, scene_volume_final_frame)
				
		return {"FINISHED"}
		
	
	def addTransformStrip(self, context, sequence, start_frame, final_frame, is_in):
		is_transform_required = context.scene.super_efecto.isTransformRequired()
		if not is_transform_required:
			return sequence
		
		if context.scene.animation_data is None:
			context.scene.animation_data_create()
		
		selected_keyframes = []
		if context.scene.animation_data.action is not None:
			for i, fcurve in context.scene.animation_data.action.fcurves.items():
				for j, keyframe_point in fcurve.keyframe_points.items():
					if keyframe_point.select_control_point:
						keyframe_point.select_control_point = False
						selected_keyframes.append(j)
						
		return_original_sequence = False		
		is_transform = (sequence.type == "TRANSFORM")
		if not is_transform:
			is_child_transform = ("input_1" in dir(sequence) and sequence.input_1 is not None and sequence.input_1.type == "TRANSFORM")
			
			if is_child_transform:
				return_original_sequence = True
				original_sequence = sequence
				sequence = sequence.input_1
				
			else:
				original_sequence = sequence
				channel = self.getAvailableChannel(context, original_sequence.frame_final_start, original_sequence.frame_final_end, original_sequence.channel)
				sequence = context.scene.sequence_editor.sequences.new_effect( \
						original_sequence.name + '_Transform', \
						'TRANSFORM', \
						channel, \
						original_sequence.frame_final_start, \
						original_sequence.frame_final_end, \
						original_sequence)
				
				original_sequence.select = False
		
		sequence.blend_type = 'ALPHA_OVER'
				
		delay_image = context.scene.super_efecto.delay_image
		tranform_start_frame = start_frame
		tranform_end_frame = final_frame
		if is_in:
			tranform_start_frame += delay_image
			tranform_end_frame += delay_image
			
		is_reversed =  ((not is_in) and context.scene.super_efecto.reverse_out_effect)
		is_horizontal_mirrored = ((not is_in) and context.scene.super_efecto.mirror_horizontal_out_effect)
		is_vertical_mirrored = ((not is_in) and context.scene.super_efecto.mirror_vertical_out_effect)
		sequence.translate_start_x = context.scene.super_efecto.initial_position_x
		if context.scene.super_efecto.position_x_animated:
			if is_reversed:
				sequence.translate_start_x = context.scene.super_efecto.final_position_x
			
			if is_horizontal_mirrored:
				sequence.translate_start_x *= -1
			
			sequence.keyframe_insert("translate_start_x", index=-1, frame=tranform_start_frame)
			
			sequence.translate_start_x = context.scene.super_efecto.final_position_x \
				if not is_reversed else context.scene.super_efecto.initial_position_x
				
			if is_horizontal_mirrored:
				sequence.translate_start_x *= -1
			
			sequence.keyframe_insert("translate_start_x", index=-1, frame=tranform_end_frame)
		
		sequence.translate_start_y = context.scene.super_efecto.initial_position_y		
		if context.scene.super_efecto.position_y_animated:
			if is_reversed:
				sequence.translate_start_y = context.scene.super_efecto.final_position_y
			
			if is_vertical_mirrored:
				sequence.translate_start_y *= -1
				
			sequence.keyframe_insert("translate_start_y", index=-1, frame=tranform_start_frame)
			
			sequence.translate_start_y = context.scene.super_efecto.final_position_y \
				if not is_reversed else context.scene.super_efecto.initial_position_y
			
			if is_vertical_mirrored:
				sequence.translate_start_y *= -1
			
			sequence.keyframe_insert("translate_start_y", index=-1, frame=tranform_end_frame)
		
		sequence.use_uniform_scale = True
		sequence.scale_start_x = context.scene.super_efecto.initial_zoom			
		if context.scene.super_efecto.zoom_animated:
			if is_reversed:
				sequence.scale_start_x = context.scene.super_efecto.final_zoom
				
			sequence.keyframe_insert("scale_start_x", index=-1, frame=tranform_start_frame)
			sequence.scale_start_x = context.scene.super_efecto.final_zoom \
				if not is_reversed else context.scene.super_efecto.initial_zoom
			sequence.keyframe_insert("scale_start_x", index=-1, frame=tranform_end_frame)
		
		sequence.blend_alpha = context.scene.super_efecto.initial_opacity
		if context.scene.super_efecto.opacity_animated:
			if is_reversed:
				sequence.blend_alpha = context.scene.super_efecto.final_opacity
				
			sequence.keyframe_insert("blend_alpha", index=-1, frame=tranform_start_frame)
			sequence.blend_alpha = context.scene.super_efecto.final_opacity \
				if not is_reversed else context.scene.super_efecto.initial_opacity
			sequence.keyframe_insert("blend_alpha", index=-1, frame=tranform_end_frame)
					
		sequence.use_translation = True
		original_offset_x = sequence.transform.offset_x
		sequence.transform.offset_x = original_offset_x + (global_scale_x * context.scene.super_efecto.initial_offset_x / 100)
		if context.scene.super_efecto.offset_x_animated:
			if is_reversed:
				sequence.transform.offset_x = original_offset_x + (global_scale_x * context.scene.super_efecto.final_offset_x / 100)
			
			if is_horizontal_mirrored:
				sequence.transform.offset_x *= -1

			sequence.transform.keyframe_insert("offset_x", index=-1, frame=tranform_start_frame)
			
			sequence.transform.offset_x = original_offset_x + (global_scale_x * \
				(context.scene.super_efecto.final_offset_x if not is_reversed else context.scene.super_efecto.initial_offset_x) / 100)
				
			if is_horizontal_mirrored:
				sequence.transform.offset_x *= -1
				
			sequence.transform.keyframe_insert("offset_x", index=-1, frame=tranform_end_frame)
		
		original_offset_y = sequence.transform.offset_y
		sequence.transform.offset_y = original_offset_y + (global_scale_y * context.scene.super_efecto.initial_offset_y / 100)
		if context.scene.super_efecto.offset_y_animated:
			if is_reversed:
				sequence.transform.offset_y = original_offset_y + (global_scale_y * context.scene.super_efecto.final_offset_y / 100)
			
			if is_vertical_mirrored:
				sequence.transform.offset_y *= -1
				
			sequence.transform.keyframe_insert("offset_y", index=-1, frame=tranform_start_frame)
			
			sequence.transform.offset_y = original_offset_y + (global_scale_y * \
				(context.scene.super_efecto.final_offset_y if not is_reversed else context.scene.super_efecto.initial_offset_y) / 100)
				
			if is_vertical_mirrored:
				sequence.transform.offset_y *= -1
				
			sequence.transform.keyframe_insert("offset_y", index=-1, frame=tranform_end_frame)
		
		if context.scene.animation_data.action is not None:
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
			
			for i, fcurve in context.scene.animation_data.action.fcurves.items():
				for j, keyframe_point in fcurve.keyframe_points.items():
					if j in selected_keyframes:
						keyframe_point.select_control_point = True
						
		return original_sequence if return_original_sequence else sequence
		
		
	def addBlurStrip(self, context, sequence, start_frame, final_frame, is_in):
		is_blur_required = context.scene.super_efecto.isBlurRequired()
		if not is_blur_required:
			return sequence
		
		if context.scene.animation_data is None:
			context.scene.animation_data_create()
		
		selected_keyframes = []
		if context.scene.animation_data.action is not None:
			for i, fcurve in context.scene.animation_data.action.fcurves.items():
				for j, keyframe_point in fcurve.keyframe_points.items():
					if keyframe_point.select_control_point:
						keyframe_point.select_control_point = False
						selected_keyframes.append(j)
			
		return_original_sequence = False		
		is_gaussian_blur = (sequence.type == "GAUSSIAN_BLUR")
		if not is_gaussian_blur:
			is_child_gaussian_blur = ("input_1" in dir(sequence) and sequence.input_1 is not None and sequence.input_1.type == "GAUSSIAN_BLUR")
			
			if is_child_gaussian_blur:
				return_original_sequence = True
				original_sequence = sequence
				sequence = sequence.input_1
				
			else:
				original_sequence = sequence
				channel = self.getAvailableChannel(context, original_sequence.frame_final_start, original_sequence.frame_final_end, original_sequence.channel)
				sequence = context.scene.sequence_editor.sequences.new_effect( \
						original_sequence.name + '_Blur', \
						'GAUSSIAN_BLUR', \
						channel, \
						original_sequence.frame_final_start, \
						original_sequence.frame_final_end, \
						original_sequence)
						
				original_sequence.select = False
		
		sequence.blend_type = 'ALPHA_OVER'

		delay_image = context.scene.super_efecto.delay_image
		tranform_start_frame = start_frame
		tranform_end_frame = final_frame
		if is_in:
			tranform_start_frame += delay_image
			tranform_end_frame += delay_image
			
		is_reversed =  ((not is_in) and context.scene.super_efecto.reverse_out_effect)
		sequence.size_x = context.scene.super_efecto.initial_blur_x
		if context.scene.super_efecto.blur_x_animated:
			if is_reversed:
				sequence.size_x = context.scene.super_efecto.final_blur_x
			
			sequence.keyframe_insert("size_x", index=-1, frame=tranform_start_frame)
			
			sequence.size_x = context.scene.super_efecto.final_blur_x \
				if not is_reversed else context.scene.super_efecto.initial_blur_x
				
			sequence.keyframe_insert("size_x", index=-1, frame=tranform_end_frame)
		
		sequence.size_y = context.scene.super_efecto.initial_blur_y		
		if context.scene.super_efecto.blur_y_animated:
			if is_reversed:
				sequence.size_y = context.scene.super_efecto.final_blur_y
			
			sequence.keyframe_insert("size_y", index=-1, frame=tranform_start_frame)
			
			sequence.size_y = context.scene.super_efecto.final_blur_y \
				if not is_reversed else context.scene.super_efecto.initial_blur_y
			
			sequence.keyframe_insert("size_y", index=-1, frame=tranform_end_frame)
				
		if context.scene.animation_data.action is not None:
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
			
			for i, fcurve in context.scene.animation_data.action.fcurves.items():
				for j, keyframe_point in fcurve.keyframe_points.items():
					if j in selected_keyframes:
						keyframe_point.select_control_point = True
						
		return original_sequence if return_original_sequence else sequence
		
		
	def overlapStrips(self, context, seq1, seq2, seq1_sound, seq2_sound):
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
		seq1.channel = self.getAvailableChannel(context, seq1.frame_final_start, seq1.frame_final_end + effect_length, seq1_channel)
		seq1.frame_final_end += effect_length
		
		if seq1_sound is not None:
			seq1_sound_channel = seq1_sound.channel
			seq1_sound.channel = tmp_channel
			seq1_sound.channel = self.getAvailableChannel(context, seq1.frame_final_start, seq1.frame_final_end + effect_length, seq1_sound_channel)
			seq1_sound.frame_final_end += effect_length

		seq2_channel = seq2.channel
		seq2.channel = tmp_channel
		seq2.channel = self.getAvailableChannel(context, seq2.frame_final_start - effect_length, seq2.frame_final_end, seq2_channel)
		seq2.frame_final_start -= effect_length
		
		if seq2_sound is not None:
			seq2_sound_channel = seq2_sound.channel
			seq2_sound.channel = tmp_channel
			seq2_sound.channel = self.getAvailableChannel(context, seq2.frame_final_start - effect_length, seq2.frame_final_end, seq2_sound_channel)
			seq2_sound.frame_final_start -= effect_length
		
		return True
	
	
	def animateVolume(self, seq_sound, initial_volume, final_volume, initial_frame, final_frame):
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
		
	
	def unselectChildren(self, sequence):
		if 'input_1' not in dir(sequence) or sequence.input_1 is None:
			return
			
		self.unselectChildren(sequence.input_1)
		sequence.input_1.select = False
	
	
	def alignImage(self, context, sequence):
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

	
	def getAvailableChannel(self, context, start_frame, final_frame, start_channel=1):
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
