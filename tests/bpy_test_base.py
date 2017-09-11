from abc import ABCMeta
from unittest import mock

class BpyTestBase():
	metaclass__ = ABCMeta
	
	
	def assert_panel(self, panel, bl_idname, bl_label, bl_space_type, bl_region_type, bl_context):
		assert panel is not None
		assert bl_idname == panel.bl_idname
		assert bl_label == panel.bl_label
		assert bl_space_type == panel.bl_space_type
		assert bl_region_type == panel.bl_region_type
		assert bl_context == panel.bl_context
	
	
	def assert_operator(self, operator, bl_idname, bl_label):
		assert operator is not None
		assert bl_idname == operator.bl_idname
		assert bl_label == operator.bl_label
	
	
	def assert_operator_error(self, operator, result, error_msg):
		assert {"CANCELLED"} == result
		expected_report_calls = [ mock.call({'ERROR'}, error_msg) ]
		assert expected_report_calls == operator.report.call_args_list
	
	
	def assert_operator_success(self, operator, result):
		assert {"FINISHED"} == result
		expected_report_calls = []
		assert expected_report_calls == operator.report.call_args_list
	
	
	def mock_panel_layout(self, panel):
		panel.layout = mock.MagicMock()
		panel.layout.row.return_value = panel.layout
