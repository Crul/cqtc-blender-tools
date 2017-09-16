from bpy_test_base import BpyTestBase
from unittest import mock


class TestCqtcTools(BpyTestBase):
	
	@mock.patch("bpy.props.IntProperty")
	def test_numbered_intro_properties(self, MockIntProperty):
		from cqtc_numbered_intros.numbered_intro_properties import NumberedIntroProperties
		
		
		properties = NumberedIntroProperties()
		
		
		assert properties is not None
		expected_int_property_calls = [
			mock.call(default=1, max=10, min=1, name="Next number", step=1),
			mock.call(default=17, max=1000, min=1, name="Transition length", step=1)
		]
		assert expected_int_property_calls == MockIntProperty.call_args_list
	
	
	def test_numbered_intro_panel(self):
		from cqtc_numbered_intros.numbered_intro_panel import NumberedIntroPanel
		
		
		panel = NumberedIntroPanel()
		
		
		self.assert_panel(panel,
			"SCENE_PT_numbered_intro",
			"Add Numbered Intros",
			"PROPERTIES",
			"WINDOW",
			"render"
		)
	
	
	def test_numbered_intro_panel_draw(self):
		from cqtc_numbered_intros.numbered_intro_panel import NumberedIntroPanel
		panel = NumberedIntroPanel()
		self.mock_panel_layout(panel)
		mock_bpy_context = mock.MagicMock()
		mock_bpy_context.selected_sequences = range(7)
		mock_numbered_intro = {"FOO"}
		mock_bpy_context.scene.numbered_intro = mock_numbered_intro
		
		panel.draw(mock_bpy_context)
		
		assert 3 == panel.layout.row.call_count
		expected_row_prop_calls = [
			mock.call(mock_numbered_intro, "next_number"),
			mock.call(mock_numbered_intro, "transition_length"),
		]
		assert expected_row_prop_calls == panel.layout.prop.call_args_list
		expected_label_calls = [ mock.call(" 7 selected strips", icon="SEQUENCE") ]
		assert expected_label_calls == panel.layout.label.call_args_list
		assert 2.0 == panel.layout.scale_y
		expected_operator_calls = [ mock.call("numbered_intro.create", text="Create Numbered Intros") ]
		assert expected_operator_calls == panel.layout.operator.call_args_list
	
	
	def test_create_numbered_intro_operator(self):
		from cqtc_numbered_intros.create_numbered_intro_operator import CreateNumberedIntroOperator
		
		
		operator = CreateNumberedIntroOperator()
		
		
		self.assert_operator(operator, "numbered_intro.create", "Create Numbered Intros")
	
	
	def test_create_numbered_intro_operator_no_sequences_selected(self):
		from cqtc_numbered_intros.create_numbered_intro_operator import CreateNumberedIntroOperator
		operator = CreateNumberedIntroOperator()
		mock_bpy_context = mock.MagicMock()
		operator.report = mock.MagicMock()
		
		
		result = operator.execute(mock_bpy_context)
		
		
		self.assert_operator_error(operator, result, 'You should select at least one strip')
	
	
	@mock.patch("os.path.isfile")
	def test_create_numbered_intro_operator_(self, mock_isfile):
		import bpy.types
		mock_bpy_context = mock.MagicMock()
		mock_bpy_context.scene.numbered_intro.next_number = 5
		mock_bpy_context.selected_sequences = [ mock.MagicMock() for x in range(3) ]
		for seq in mock_bpy_context.selected_sequences:
			seq.type = "MOVIE"
		mock_isfile.side_effect = [True, True, False]
		import cqtc_numbered_intros.create_numbered_intro_operator
		from cqtc_numbered_intros.create_numbered_intro_operator import CreateNumberedIntroOperator
		cqtc_numbered_intros.create_numbered_intro_operator.numbered_intro_image_path = "FOO"
		operator = CreateNumberedIntroOperator()
		operator.report = mock.MagicMock()
		
		
		result = operator.execute(mock_bpy_context)
		
		
		self.assert_operator_error(operator, result, 'File not found: FOO\\TF 07.jpg')
		expected_isfile_calls = [ mock.call('FOO\\TF 0%s.jpg' % i) for i in range(5,8) ]
		assert expected_isfile_calls == mock_isfile.call_args_list
	
	
	@mock.patch("os.path.isfile")
	def test_create_numbered_intro_operator_(self, mock_isfile):
		import bpy.types
		mock_bpy_context = mock.MagicMock()
		mock_bpy_context.scene.numbered_intro.next_number = 5
		mock_bpy_context.scene.numbered_intro.transition_length = 34
		previous_sequence = bpy.types.Sequence(10, 21)
		previous_sequence.name = "MySequence3"
		previous_sequence.type = "MOVIE"
		previous_sequence.channel = 2
		first_sequence = bpy.types.Sequence(51, 100)
		first_sequence.name = "MySequence1"
		first_sequence.type = "MOVIE"
		first_sequence.channel = 2
		second_sequence = bpy.types.Sequence(200, 300)
		second_sequence.name = "MySequence2"
		second_sequence.type = "MOVIE"
		second_sequence.channel = 2
		mock_bpy_context.selected_sequences = [ second_sequence, first_sequence ]
		mock_bpy_context.sequences = [ previous_sequence ] + mock_bpy_context.selected_sequences
		mock_image_seqs = [ bpy.types.Sequence(0, 0) for x in range(2) ]
		mock_bpy_context.scene.sequence_editor.sequences.new_image.side_effect = mock_image_seqs
		mock_effect_seqs = [ bpy.types.Sequence(0, 0) for x in range(4) ]
		mock_bpy_context.scene.sequence_editor.sequences.new_effect.side_effect = mock_effect_seqs
		mock_isfile.return_value = True
		import cqtc_numbered_intros.create_numbered_intro_operator
		from cqtc_numbered_intros.create_numbered_intro_operator import CreateNumberedIntroOperator
		cqtc_numbered_intros.create_numbered_intro_operator.numbered_intro_image_path = "FOO"
		operator = CreateNumberedIntroOperator()
		operator.report = mock.MagicMock()
		
		
		result = operator.execute(mock_bpy_context)
		
		
		self.assert_operator_success(operator, result)
		expeceted_new_effect_calls = [
			mock.call("TF Negro 5",     "COLOR", 2,  21, frame_end= 22),
			mock.call("TF Transición 5", "WIPE", 2,  21, frame_end= 38, seq1=mock_effect_seqs[0], seq2=mock_image_seqs[0]),
			mock.call("TF Negro 6",     "COLOR", 2, 104, frame_end=105),
			mock.call("TF Transición 6", "WIPE", 2, 104, frame_end=121, seq1=mock_effect_seqs[2], seq2=mock_image_seqs[1])
		]
		assert expeceted_new_effect_calls == mock_bpy_context.scene.sequence_editor.sequences.new_effect.call_args_list
		for i in range(0,4,2):
			assert (0,0,0) == mock_effect_seqs[i].color
			assert "CLOCK" == mock_effect_seqs[i+1].transition_type
			assert "IN" == mock_effect_seqs[i+1].direction
		expected_image_frames = [
			{ "start": 38, "end": 55 },
			{ "start": 121, "end": 138 },
		]
		expected_new_image_calls = [
			mock.call("TF Imagen 5", "FOO\\TF 05.jpg", 2, expected_image_frames[0]["start"]),
			mock.call("TF Imagen 6", "FOO\\TF 06.jpg", 2, expected_image_frames[1]["start"])
		]
		assert expected_new_image_calls == mock_bpy_context.scene.sequence_editor.sequences.new_image.call_args_list
		assert expected_image_frames[0]["end"] == mock_image_seqs[0].frame_final_end
		assert expected_image_frames[1]["end"] == mock_image_seqs[1].frame_final_end
		assert expected_image_frames[0]["end"] == first_sequence.frame_start
		assert expected_image_frames[1]["end"] == second_sequence.frame_start
