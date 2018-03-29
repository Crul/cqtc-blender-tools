from cqtc_operator import CqtcOperator
import cqtc_bpy
import os.path
import re
import bpy.ops

number_tag_regex = re.compile('\#+')

class CreateAnimatedSequenceOperator(CqtcOperator):
	bl_idname = "animated_sequence.create"
	bl_label = "Create Animated Sequence"
	
	def execute(self, context):
		error = self.validate_data(context)
		if error:
			return self.return_error(error)
		
		error, markers = self.get_markers(context)
		if error:
			return self.return_error(error)
		
		self.add_sequence(context, markers)
		
		context.scene.animated_sequence.from_image = 0
		context.scene.animated_sequence.to_image = 99
		context.scene.animated_sequence.base_name = ""
		
		return {"FINISHED"}
	
	
	def validate_data(self, context):
		from_image = context.scene.animated_sequence.from_image
		to_image = context.scene.animated_sequence.to_image
		
		if from_image > to_image:
			return "Invalid range: 'From image' is greater than 'To image'"

		sequence_path = context.scene.animated_sequence.sequence_path
		base_name = context.scene.animated_sequence.base_name
		template_name = self.get_image_name_template(base_name)
		image_full_path = os.path.join(sequence_path, self.get_image_name(template_name, from_image))
		if not os.path.isfile(image_full_path):
			return "%s: %s" % (self.translate("File not found"), image_full_path)
		
	
	def get_markers(self, context):
		previous_marker = None
		next_marker = None
		current_frame = context.scene.frame_current
		for marker in context.scene.timeline_markers:
			if (marker.frame <= current_frame and (previous_marker is None or previous_marker.frame < marker.frame)):
				previous_marker = marker

			if (marker.frame >= current_frame and (next_marker is None or next_marker.frame > marker.frame)):
				next_marker = marker
		
		if previous_marker == None:
			return "Start marker not found", None

		if next_marker == None:
			return "End marker not found", None

		third_marker = None
		add_last_image_if_marker_exists = context.scene.animated_sequence.add_last_image_if_marker_exists
		if add_last_image_if_marker_exists:
			for marker in context.scene.timeline_markers:
				if (marker.frame > next_marker.frame and (third_marker is None or third_marker.frame > marker.frame)):
					third_marker = marker
		
		return None, [ previous_marker, next_marker, third_marker ]


	def add_sequence(self, context, markers):
		sequence_path = context.scene.animated_sequence.sequence_path
		base_name = context.scene.animated_sequence.base_name
		from_image = context.scene.animated_sequence.from_image
		to_image = context.scene.animated_sequence.to_image
		
		initial_frame = markers[0].frame
		images_final_frame = initial_frame + (5 * (to_image - from_image + 1))
		final_frame = (markers[1].frame if (markers[2] is None) else markers[2].frame)

		template_name = self.get_image_name_template(base_name)
		image_names = [ self.get_image_name(template_name, image_number)
			for image_number in range(from_image, to_image + 1) ]

		image_files = []
		for image_name in image_names:
			if os.path.isfile(os.path.join(sequence_path, image_name)):
				image_files.append({ "name": image_name })
			else:
				break

		strip_channel = context.scene.animated_sequence.strip_channel
		available_channel = cqtc_bpy.get_available_channel_in_position(context, initial_frame, final_frame, strip_channel)
		
		old_area_type = context.area.type
		context.area.type = "SEQUENCE_EDITOR"
		context.scene.update()
		
		bpy.ops.sequencer.image_strip_add(
			directory=sequence_path,
			files=image_files,
			frame_start=initial_frame,
			frame_end=images_final_frame,
			channel=available_channel)
		
		bpy.ops.sequencer.effect_strip_add(frame_start=initial_frame, frame_end=images_final_frame, type="SPEED")

		context.selected_sequences[0].input_1.frame_final_end = markers[1].frame
		
		context.area.type = old_area_type
		context.scene.update()
		
		add_last_image_if_marker_exists = context.scene.animated_sequence.add_last_image_if_marker_exists
		if add_last_image_if_marker_exists and (markers[2] is not None):
			last_image_strip = context.scene.sequence_editor.sequences.new_image(
				"Secuencia Animada Imagen Final",
				os.path.join(sequence_path, image_files[-1]["name"]),
				available_channel,
				markers[1].frame
			)
		
			last_image_strip.frame_final_end = markers[2].frame
		
		remove_markers = context.scene.animated_sequence.remove_markers
		if remove_markers:
			for marker in [m for m in markers if m is not None]:
				context.scene.timeline_markers.remove(marker)


	def get_image_name_template(self, base_name):
		if "#" in base_name:
			return base_name

		return base_name + "##.png"
	
	
	def get_image_name(self, template_name, image_number):
		number_tag_search = number_tag_regex.search(template_name)
		if number_tag_search is None:
			return template_name
		
		number_tag = number_tag_search.group()
		return template_name.replace(number_tag,  str(image_number).zfill(len(number_tag)))
