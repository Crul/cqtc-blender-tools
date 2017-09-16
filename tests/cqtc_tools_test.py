from bpy_test_base import BpyTestBase
from unittest import mock

class TestCqtcTools(BpyTestBase):

	def test_tools_panel(self):
		from cqtc_tools.cqtc_tools_panel import CqtcToolsPanel
		
		
		panel = CqtcToolsPanel()
		
		
		self.assert_panel(panel,
			"SCENE_PT_cqtc_tools",
			"Herramientas",
			"PROPERTIES",
			"WINDOW",
			"render"
		)
	
	
	def test_tools_panel_draw(self):
		from cqtc_tools.cqtc_tools_panel import CqtcToolsPanel
		panel = CqtcToolsPanel()
		self.mock_panel_layout(panel)
		mock_bpy_context = mock.MagicMock()
		mock_bpy_context.selected_sequences = range(7)
		mock_operator_up = mock.MagicMock()
		mock_operator_down = mock.MagicMock()
		panel.layout.operator.side_effect = [
			mock_operator_up,
			mock_operator_down
		]
		
		panel.draw(mock_bpy_context)
		
		expected_label_calls = [ mock.call(" 7 selected strips", icon="SEQUENCE") ]
		assert expected_label_calls == panel.layout.label.call_args_list
		expected_operator_calls = [
			mock.call("cqtc_tools.change_channel", text="Subir strips"),
			mock.call("cqtc_tools.change_channel", text="Bajar strips")
		]
		assert expected_operator_calls == panel.layout.operator.call_args_list
		assert mock_operator_up.up_or_down
		assert not mock_operator_down.up_or_down
	
	
	def test_change_strips_channel_operator(self):
		from cqtc_tools.change_strips_channel_operator import ChangeStripsChannelOperator
		
		
		operator = ChangeStripsChannelOperator()
		
		
		assert operator is not None
	
	
	def test_change_strips_channel_operator_no_selected_sequences(self):
		from cqtc_tools.change_strips_channel_operator import ChangeStripsChannelOperator
		mock_bpy_context = mock.MagicMock()
		mock_bpy_context.selected_sequences = []
		operator = ChangeStripsChannelOperator()
		operator.report = mock.MagicMock()
		
		result = operator.execute(mock_bpy_context)
		
		
		self.assert_operator_error(operator, result, "No hay strips seleccionadas")
	
	
	@mock.patch("cqtc_bpy.get_available_channel_for_strip")
	def test_change_strips_channel_operator_move_up(self, mock_get_available_channel_for_strip):
		import bpy.types
		from cqtc_tools.change_strips_channel_operator import ChangeStripsChannelOperator
		mock_bpy_context = mock.MagicMock()
		mock_bpy_context.selected_sequences = [ bpy.types.Sequence(0, 100),  bpy.types.Sequence(101, 200) ]
		for i, seq in enumerate(mock_bpy_context.selected_sequences):
			seq.channel = i + 1
		operator = ChangeStripsChannelOperator()
		operator.up_or_down = True
		operator.report = mock.MagicMock()
		mock_get_available_channel_for_strip.side_effect = [ 7, 9 ]
		
		result = operator.execute(mock_bpy_context)
		
		
		self.assert_operator_success(operator, result)
		assert 9 == mock_bpy_context.selected_sequences[0].channel
		assert 7 == mock_bpy_context.selected_sequences[1].channel
	
	
	@mock.patch("cqtc_bpy.get_available_channel_for_strip")
	def test_change_strips_channel_operator_move_down(self, mock_get_available_channel_for_strip):
		import bpy.types
		from cqtc_tools.change_strips_channel_operator import ChangeStripsChannelOperator
		mock_bpy_context = mock.MagicMock()
		mock_bpy_context.selected_sequences = [ bpy.types.Sequence(0, 100),  bpy.types.Sequence(101, 200) ]
		for i, seq in enumerate(mock_bpy_context.selected_sequences):
			seq.channel = i + 3
		operator = ChangeStripsChannelOperator()
		operator.up_or_down = False
		operator.report = mock.MagicMock()
		mock_get_available_channel_for_strip.side_effect = [ 7, 9 ]
		
		
		result = operator.execute(mock_bpy_context)
		
		
		self.assert_operator_success(operator, result)
		assert 7 == mock_bpy_context.selected_sequences[0].channel
		assert 9 == mock_bpy_context.selected_sequences[1].channel
