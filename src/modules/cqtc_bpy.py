import bpy.ops

tmp_channel = 30
max_channel = 20

def align_image(context, sequence, image_alignment, image_alignment_margin):
	if image_alignment == "none" or sequence.type != "IMAGE" or len(sequence.elements) == 0:
		return
		
	image_element = sequence.elements[0]
	if image_element.orig_width == context.scene.render.resolution_x and image_element.orig_height == context.scene.render.resolution_y:
		return

	sequence.use_translation = True
	sequence.blend_type = "ALPHA_OVER"
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


def animate_volume(seq_sound, initial_volume, final_volume, initial_frame, final_frame):
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


def create_material(name, diffuse, specular, alpha):
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


def get_available_channel_for_strip(context, sequence, up_or_down):
	if up_or_down:
		channel_range = range(sequence.channel + 1, max_channel)
	else:
		channel_range = reversed(range(1, sequence.channel))

	start_frame = sequence.frame_final_start
	final_frame = sequence.frame_final_end
	channel = get_available_channel_in_range(context, channel_range, start_frame, final_frame)
	
	return channel if channel is not None else sequence.channel


def get_available_channel_in_position(context, start_frame, final_frame, start_channel=1):
	channel_range = range(start_channel, max_channel)
	channel = get_available_channel_in_range(context, channel_range, start_frame, final_frame)
	
	return channel if channel is not None else max_channel


def get_available_channel_in_range(context, channel_range, start_frame, final_frame):
	for channel in channel_range:
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
			
	return None


def overlap_strips(context, effect_length, seq1, seq2, seq1_sound, seq2_sound):
	
	while(seq1.type in ["TRANSFORM","CROSS","GAUSSIAN_BLUR"]):
		seq1 = seq1.input_1
	
	while(seq2.type in ["TRANSFORM","CROSS","GAUSSIAN_BLUR"]):
		seq2 = seq2.input_1
	
	if seq1.type in ["MOVIE","SCENE"]:
		not_enough_data_after_seq1 = (seq1.frame_offset_end < effect_length)
		if not_enough_data_after_seq1:
			return "No hay suficientes datos después del final en la tira " + seq1.name
	
	if seq2.type in ["MOVIE","SCENE"]:
		not_enough_data_before_seq2 = (seq2.frame_offset_start < effect_length)
		if not_enough_data_before_seq2:
			return "No hay suficientes datos antes del comianzo en la tira " + seq2.name
	
	seq1_channel = seq1.channel
	seq1.channel = tmp_channel
	seq1.channel = get_available_channel_in_position(context, seq1.frame_final_start, seq1.frame_final_end + effect_length, seq1_channel)
	seq1.frame_final_end += effect_length
	
	if seq1_sound is not None:
		seq1_sound_channel = seq1_sound.channel
		seq1_sound.channel = tmp_channel
		seq1_sound.channel = get_available_channel_in_position(context, seq1.frame_final_start, seq1.frame_final_end + effect_length, seq1_sound_channel)
		seq1_sound.frame_final_end += effect_length

	seq2_channel = seq2.channel
	seq2.channel = tmp_channel
	seq2.channel = get_available_channel_in_position(context, seq2.frame_final_start - effect_length, seq2.frame_final_end, seq2_channel)
	seq2.frame_final_start -= effect_length
	
	if seq2_sound is not None:
		seq2_sound_channel = seq2_sound.channel
		seq2_sound.channel = tmp_channel
		seq2_sound.channel = get_available_channel_in_position(context, seq2.frame_final_start - effect_length, seq2.frame_final_end, seq2_sound_channel)
		seq2_sound.frame_final_start -= effect_length


def set_keyframe_interpolation_type(context, sequence, seq_attr, position, interpolation_type):
	if not interpolation_type:
		return
	
	fcurve_data_path = "sequence_editor.sequences_all[\"%s\"].%s" % (sequence.name, seq_attr)
	fcurves = [fcurve for fcurve in context.scene.animation_data.action.fcurves if fcurve.data_path == fcurve_data_path]
	for fcurve in fcurves:
		keyframe_points = [keyframe_point for keyframe_point in fcurve.keyframe_points if keyframe_point.co[0] == position]
		for keyframe_point in keyframe_points:
			keyframe_point.interpolation = interpolation_type


def unselect_children(sequence):
	if "input_1" not in dir(sequence) or sequence.input_1 is None:
		return
		
	unselect_children(sequence.input_1)
	sequence.input_1.select = False


def deselect_selected_keyframe_points(context):
	if context.scene.animation_data is None:
		context.scene.animation_data_create()
	
	selected_keyframes = []
	if context.scene.animation_data.action is None:
		return selected_keyframes
	
	for i, fcurve in context.scene.animation_data.action.fcurves.items():
		for j, keyframe_point in fcurve.keyframe_points.items():
			if keyframe_point.select_control_point:
				keyframe_point.select_control_point = False
				selected_keyframes.append(keyframe_point)

	return selected_keyframes


def select_keyframe_points(context, selected_keyframes):
	if context.scene.animation_data.action is None:
		return
		
	for i, fcurve in context.scene.animation_data.action.fcurves.items():
		for j, keyframe_point in fcurve.keyframe_points.items():
			if keyframe_point in selected_keyframes:
				keyframe_point.select_control_point = True
