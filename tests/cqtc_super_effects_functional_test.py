from unittest import mock
import json
import os.path
import pytest
import warnings

import bpy
from cqtc_super_effects.super_effect_properties import SuperEffectProperties
from cqtc_super_effects.create_super_effect_operator import CreateSuperEffectOperator

test_definition_path = "./tests/functional_tests"
test_definition_file_pattern = "cqtc_super_effects.%s.json"
test_definitions = [
	"unselect_children",
	"align_image",
	"in_validation",
	"in",
	"out_validation",
	"out",
	"transition_validation",
	"transition_without_color",
	"transition_with_color",
	"effects"
]

def load_tests():
	tests_data = {}
	for test_definition in test_definitions:
		test_file_path = os.path.join(test_definition_path, (test_definition_file_pattern % test_definition))
		with open(test_file_path, encoding="utf-8") as file:
			json_data = json.loads(file.read())
			if "TODO" in json_data:
				pending_tests = "\n   - ".join([""] + json_data["TODO"])
				warning_msg = "\n\n > pending %i '%s' tests: %s\n" % (len(json_data["TODO"]), test_definition, pending_tests)
				warnings.warn(warning_msg)
				
			common_data = (json_data["common"] if "common" in json_data else {})
			file_tests_data = dict(get_test_data(tests_data, common_data, test_data) for test_data in json_data["tests"])
			tests_data.update(file_tests_data)
			
	return tests_data

	
def get_test_data(tests_data, common_data, original_test_data):
	test_data = common_data.copy()
	test_data.update(original_test_data)
	
	for key in test_data:
		if type(test_data[key]) is dict and key in original_test_data:
			test_data[key] = common_data[key].copy()
			test_data[key].update(original_test_data[key])
	
	test_name = test_data["name"]
	assert test_name not in tests_data
	
	return (test_name, test_data)
	

class TestCqtcSuperEffectsFunctional:

	cqtc_super_effects_operator = None
	super_effect_properties = None
	mock_selected_sequences_array = []
	keyframe_insert_calls = []
	tests_data = load_tests()
	common_graph_tests_data = {
		"operator": { "operation_type": "IN" },
		"super_effect": {
			"effect_type": "no_effect",
			"initial_zoom": 1,
			"final_zoom": 1,
			"initial_opacity": 1,
			"final_opacity": 1,
			"effect_length": 10
		},
		"sequences": [ { "name": "MySequence", "type": "MOVIE", "frame_final_start": 33, "frame_final_end": 133 } ]
	}
	graph_tests_data = [
		{ "super_effect": { "initial_position_x": 10, "constant_speed": True } },
		{ "super_effect": { "initial_position_x": 10, "constant_speed": False } },
		{ "super_effect": { "initial_blur_x": 10, "constant_speed": True } },
		{ "super_effect": { "initial_blur_x": 10, "constant_speed": False } }
	]
	fake_fcurves = {}
	selected_keyframe_points_on_interpolation_type_call = []
	
	def setup_method(self, method):
		self.cqtc_super_effects_operator = CreateSuperEffectOperator()
		self.cqtc_super_effects_operator.report = mock.MagicMock()
		self.super_effect_properties = SuperEffectProperties()
		self.mock_selected_sequences_array = [];
		self.keyframe_insert_calls = []
		
	
	@mock.patch("bpy.types.Context.selected_sequences", new_callable=mock.PropertyMock)
	@mock.patch("bpy.types.Sequences.new_effect")
	@pytest.mark.parametrize("test_data_name", tests_data)
	def test_functional(self,
						mock_new_effect,
						mock_selected_sequences,
						test_data_name
	):
		test_data = self.tests_data[test_data_name]
		self.mock_selected_sequences_array = self.create_mock_sequences(test_data)
		mock_selected_sequences.side_effect = self.get_mock_selected_sequences
		mock_new_effect.side_effect = self.create_mock_effect_sequence
		self.set_values(self.super_effect_properties, test_data["super_effect"])
		bpy.context.scene.super_effect = self.super_effect_properties
		self.set_values(self.cqtc_super_effects_operator, test_data["operator"])
		
		
		result = self.cqtc_super_effects_operator.execute(bpy.context)

		
		self.assert_report(test_data)
		assert { test_data["expected_result"] } == result
		final_sequences = self.get_mock_selected_sequences()
		self.assert_sequences(test_data, final_sequences)
		self.assert_calls(mock_new_effect, "new_effect", test_data["expected_calls"]["new_effect"])
		expected_keyframe_insert_call_values = (test_data["expected_calls"]["sequences_keyframe_insert_values"] if "sequences_keyframe_insert_values" in test_data["expected_calls"] else [])
		assert expected_keyframe_insert_call_values == self.keyframe_insert_calls

	
	@mock.patch("bpy.types.Context.selected_sequences", new_callable=mock.PropertyMock)
	@mock.patch("bpy.types.Sequences.new_effect")
	@mock.patch("bpy.types.Scene.animation_data_create")
	@mock.patch("bpy.types.Graph.interpolation_type")
	@pytest.mark.parametrize("graph_test_data", graph_tests_data)
	def test_graph_functional(self,
						mock_interpolation_type,
						mock_animation_data_create,
						mock_new_effect,
						mock_selected_sequences,
						graph_test_data
	):
		test_data = {}
		for key in self.common_graph_tests_data:
			test_data[key] = self.common_graph_tests_data[key].copy()
		
		for key in graph_test_data:
			test_data[key].update(graph_test_data[key].copy())
			
		mock_interpolation_type.side_effect = self.handle_interpolation_type_call
		mock_animation_data_create.side_effect = self.create_animation_data
		mock_new_effect.side_effect = self.create_mock_effect_sequence
		self.mock_selected_sequences_array = self.create_mock_sequences(test_data)
		mock_selected_sequences.side_effect = self.get_mock_selected_sequences
		self.set_values(self.super_effect_properties, test_data["super_effect"])
		bpy.context.scene.super_effect = self.super_effect_properties
		self.set_values(self.cqtc_super_effects_operator, test_data["operator"])
		bpy.context.scene.animation_data = None
		self.create_fake_fcurves()
		
		
		result = self.cqtc_super_effects_operator.execute(bpy.context)

				
		self.cqtc_super_effects_operator.report.assert_not_called()
		mock_animation_data_create.assert_called_once_with()
		assert 1 == mock_interpolation_type.call_count
		call_args, named_call_args = mock_interpolation_type.call_args_list[0]
		expected_interpolation_type = "LINEAR" if test_data["super_effect"]["constant_speed"] else "BEZIER"
		assert { "type": expected_interpolation_type } == named_call_args
		assert () == call_args
		assert [] == self.selected_keyframe_points_on_interpolation_type_call
		for fcurve_key in self.fake_fcurves:
			for kf_point_key in self.fake_fcurves[fcurve_key].keyframe_points:
				kf_point = self.fake_fcurves[fcurve_key].keyframe_points[kf_point_key]
				assert True == kf_point.select_control_point
	
	
	def create_animation_data(self):
		bpy.context.scene.animation_data = bpy.types.AnimationData()
		bpy.context.scene.animation_data.action.fcurves = self.fake_fcurves
	
	
	def create_fake_fcurves(self):
		for i in range(0, 5):
			fcurve_idx = "fcurve_%i" % i
			self.fake_fcurves[fcurve_idx] = bpy.types.FCurve()
			
			for j in range(0, 3):
				kf_point_idx = "kf_point_%i_%i" % (i, j)
				self.fake_fcurves[fcurve_idx].keyframe_points[kf_point_idx] = bpy.types.KeyframePoint()
				self.fake_fcurves[fcurve_idx].keyframe_points[kf_point_idx].select_control_point = True
			
	
	def handle_interpolation_type_call(self, type=None):
		self.selected_keyframe_points_on_interpolation_type_call = []
		for fcurve_key in self.fake_fcurves:
			for kf_point_key in self.fake_fcurves[fcurve_key].keyframe_points:
				kf_point = self.fake_fcurves[fcurve_key].keyframe_points[kf_point_key]
				
				if kf_point.select_control_point:
					self.selected_keyframe_points_on_interpolation_type_call.append(kf_point_key)
	
	
	def get_mock_selected_sequences(self):
		return [ seq for seq in self.mock_selected_sequences_array if seq.select ]
	
	
	def assert_report(self, test_data):
		expected_report = test_data["expected_report"]
		if expected_report is None:
			self.cqtc_super_effects_operator.report.assert_not_called()
		else:
			expected_report_values = ({ expected_report[0] }, expected_report[1] )
			self.cqtc_super_effects_operator.report.assert_has_calls([mock.call(*expected_report_values)])

			
	def assert_sequences(self, test_data, sequences):
		assert len(test_data["expected_sequences"]) == len(sequences)
		self.assert_sequences_values(sequences, test_data["expected_sequences"])
	
	
	def assert_sequences_values(self, object, expected_data_dict):
		if type(expected_data_dict) is list:
			for expected_data_element_index, expected_data_element in enumerate(expected_data_dict):
				self.assert_sequences_values(object[expected_data_element_index], expected_data_element)
		
		else:
			for expected_property, expected_value in expected_data_dict.items():
				current_value = getattr(object, expected_property)
				if type(current_value) in [int,float,str,bool]:
					assert_msg = ("Wrong %s" % (expected_property))
					assert expected_value == current_value, assert_msg
				else:
					self.assert_sequences_values(current_value, expected_value)
	
	
	def assert_calls(self, mock_method, method_name, expected_calls):
		if expected_calls is None or len(expected_calls) == 0:
			mock_method.assert_not_called()
			return
						
		assert len(expected_calls) == mock_method.call_count
		for call_index, call in enumerate(mock_method.call_args_list):
			assert len(expected_calls) > call_index
			call_args, named_call_args = call
			
			for arg_index, arg in enumerate(call_args):
				assert len(expected_calls[call_index]) > arg_index
				expected_arg = expected_calls[call_index][arg_index]
				
				if type(expected_arg) is dict:
					for key in expected_arg:
						assert_msg = ("%s call[%i] arg[%i][%s] value = %s" % (method_name, call_index, arg_index, key, expected_arg[key]))
						assert expected_arg[key] == getattr(arg, key), assert_msg
						
				elif expected_arg != "ANY":
					assert_msg = ("%s call[%i] arg[%i] value = %s" % (method_name, call_index, arg_index, expected_arg))
					assert expected_arg == arg, assert_msg
			
			if named_call_args:
				expected_named_args = expected_calls[call_index][-1]
				for named_call_arg_name in named_call_args:
					expected_call_arg_value = expected_named_args[named_call_arg_name]
					current_call_arg_value = named_call_args[named_call_arg_name]
					assert_msg = ("%s call[%i][%s] named value" % (method_name, call_index, named_call_arg_name))
					if type(expected_call_arg_value) is dict:
						for prop in expected_call_arg_value:
							assert expected_call_arg_value[prop] == getattr(current_call_arg_value, prop), assert_msg
							
					else:
						assert expected_call_arg_value == current_call_arg_value, assert_msg
	
	
	def create_mock_effect_sequence(self, name, effect_type, channel, frame_start, frame_end, seq1=None, seq2=None):
		effect_sequence_data = {
			"name": name,
			"type": effect_type,
			"channel": channel,
			"frame_final_start": frame_start,
			"frame_final_end": frame_end
		}
		if seq1 is not None:
			effect_sequence_data["input_1"] = seq1
			
		effect_sequence = self.create_mock_sequence(self.mock_selected_sequences_array, effect_sequence_data)
		
		self.mock_selected_sequences_array.append(effect_sequence)
		
		return effect_sequence
		
	
	def create_mock_sequences(self, test_data):
		mock_selected_sequences_array = []
		for sequence_data in test_data["sequences"]:
			new_selected_sequence = self.create_mock_sequence(mock_selected_sequences_array, sequence_data)
			if new_selected_sequence not in mock_selected_sequences_array:
				mock_selected_sequences_array.append(new_selected_sequence)
				
		return mock_selected_sequences_array

		
	def create_mock_sequence(self, sequence_array, sequence_data):
		mock_sequence = None
		for sequence in sequence_array:
			mock_sequence = self.search_sequence_by_name(sequence, sequence_data["name"])
			if mock_sequence is not None:
				break
		
		if mock_sequence is None:
			mock_sequence_select = mock.patch("bpy.types.Sequence.select", new_callable=mock.PropertyMock)
			mock_sequence_select.return_value = sequence_data["select"] if "select" in sequence_data else True
			
			frame_final_start = sequence_data["frame_final_start"] if "frame_final_start" in sequence_data else 0
			frame_final_end = sequence_data["frame_final_end"] if "frame_final_end" in sequence_data else 100
			frame_offset_start = sequence_data["frame_offset_start"] if "frame_offset_start" in sequence_data else 0
			frame_offset_end = sequence_data["frame_offset_end"] if "frame_offset_end" in sequence_data else 0
			if "type" in sequence_data and sequence_data["type"] == "SOUND":
				mock_sequence = bpy.types.VolumeSequence(frame_final_start, frame_final_end, frame_offset_start, frame_offset_end)
			elif "type" in sequence_data and sequence_data["type"] == "SCENE":
				mock_sequence = bpy.types.VolumeSceneSequence(frame_final_start, frame_final_end, frame_offset_start, frame_offset_end)
				mock_sequence.scene.keyframe_insert = mock.MagicMock()
				mock_sequence.scene.keyframe_insert.side_effect = self.get_keyframe_insert_fake_fn(mock_sequence, "scene")
			else:
				mock_sequence = bpy.types.Sequence(frame_final_start, frame_final_end, frame_offset_start, frame_offset_end)
				
			self.set_values(mock_sequence, sequence_data)
			mock_sequence.keyframe_insert = mock.MagicMock()
			mock_sequence.keyframe_insert.side_effect = self.get_keyframe_insert_fake_fn(mock_sequence)
				
			mock_sequence.transform.keyframe_insert = mock.MagicMock()
			mock_sequence.transform.keyframe_insert.side_effect = self.get_keyframe_insert_fake_fn(mock_sequence, "transform")
			
			mock_sequence.elements = []
			if "elements" in sequence_data:
				for element_data in sequence_data["elements"]:
					mock_element = bpy.types.SequenceElement()
					self.set_values(mock_element, element_data)
					mock_sequence.elements.append(mock_element)
			
			if "input_1" in sequence_data:
				if type(sequence_data["input_1"]) is bpy.types.Sequence:
					mock_sequence.input_1 = sequence_data["input_1"]
				else:
					mock_sequence.input_1 = self.create_mock_sequence(sequence_array, sequence_data["input_1"])
			
		return mock_sequence
		
		
	def get_keyframe_insert_fake_fn(self, mock_sequence, sequence_property=None):
	
		def keyframe_insert_fake(property_name, index=None, frame=-1):
			property_value = getattr(mock_sequence, property_name) \
				if sequence_property is None else \
					getattr(getattr(mock_sequence, sequence_property), property_name)
				
			sequence_name = mock_sequence.name
			if sequence_property:
				sequence_name += "." + sequence_property
			
			keyframe_insert_call = {
				"sequence": sequence_name,
				"name": property_name,
				"value": property_value,
				"frame": frame
			}
			self.keyframe_insert_calls.append(keyframe_insert_call)
		
		return keyframe_insert_fake
	
	
	def search_sequence_by_name(self, sequence, sequence_name):
		if sequence.name == sequence_name:
			return sequence
			
		if sequence.input_1 is None:
			return None
			
		return self.search_sequence_by_name(sequence.input_1, sequence_name)
	
	
	def set_values(self, object, data_dict):
		for key, value in sorted(data_dict.items()):
			if type(value) is dict:
				obj_prop = getattr(object, key)
				if obj_prop is not None:
					self.set_values(obj_prop, value)
			else:
				if key != "frame_final_duration":
					setattr(object, key, value)
