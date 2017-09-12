from bpy_test_base import BpyTestBase
from unittest import mock

class TestCqtcTools(BpyTestBase):

	@mock.patch("bpy.props.IntProperty")
	@mock.patch("bpy.props.BoolProperty")
	def test_tools_properties(self, MockBoolProperty, MockIntProperty):
		from cqtc_tools.change_strips_channel_operator import ChangeStripsChannelOperator
		from cqtc_tools.set_proxy_config_properties import SetProxyConfigProperties
		
		
		expected_int_property_calls = [ mock.call(name="Calidad JPEG", default=10, min=1, max=100, step=10) ]
		assert expected_int_property_calls == MockIntProperty.call_args_list
		expected_bool_property_calls = [ mock.call(name="Rebuild", default=True), mock.call(default=True) ]
		assert expected_bool_property_calls == MockBoolProperty.call_args_list
	
	
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
		mock_cqtc_tools_proxy = {"FOO"}
		mock_bpy_context.scene.cqtc_tools_proxy = mock_cqtc_tools_proxy
		mock_operator_up = mock.MagicMock()
		mock_operator_down = mock.MagicMock()
		panel.layout.operator.side_effect = [
			None,
			mock_operator_up,
			mock_operator_down
		]
		
		panel.draw(mock_bpy_context)
		
		expected_label_calls = [ mock.call("7 selected strips") ]
		assert expected_label_calls == panel.layout.label.call_args_list
		assert 4 == panel.layout.row.call_count
		expected_prop_calls = [
			mock.call(mock_cqtc_tools_proxy, "jpeg_quality"),
			mock.call(mock_cqtc_tools_proxy, "rebuild"),
		]
		assert expected_prop_calls == panel.layout.prop.call_args_list
		expected_operator_calls = [
			mock.call("cqtc_tools_proxy.set_proxy"),
			mock.call("cqtc_tools_channel.change", text="Subir strips"),
			mock.call("cqtc_tools_channel.change", text="Bajar strips")
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
	
	
	def test_set_proxy_config_operator(self):
		from cqtc_tools.set_proxy_config_operator import SetProxyConfigOperator
		
		
		operator = SetProxyConfigOperator()
		
		
		assert operator is not None
	
	
	def test_set_proxy_config_operator_no_selected_sequences(self):
		from cqtc_tools.set_proxy_config_operator import SetProxyConfigOperator
		mock_bpy_context = mock.MagicMock()
		mock_bpy_context.selected_sequences = []
		operator = SetProxyConfigOperator()
		operator.report = mock.MagicMock()
		
		result = operator.execute(mock_bpy_context)
		
		
		self.assert_operator_error(operator, result, "No hay strips seleccionadas")
	
	
	def test_set_proxy_config_operator_no_proxyable_sequences(self):
		import bpy.types
		from cqtc_tools.set_proxy_config_operator import SetProxyConfigOperator
		mock_bpy_context = mock.MagicMock()
		mock_bpy_context.selected_sequences = [ bpy.types.Sequence(0, 100) ]
		operator = SetProxyConfigOperator()
		operator.report = mock.MagicMock()
		
		
		result = operator.execute(mock_bpy_context)
		
		
		self.assert_operator_error(operator, result, "No se puede aplicar el proxy a ninguna de las strips seleccionadas")
		
	
	def test_set_proxy_config_operator_modify(self):
		import bpy.types
		from cqtc_tools.set_proxy_config_operator import SetProxyConfigOperator
		mock_bpy_context = mock.MagicMock()
		mock_bpy_context.scene.cqtc_tools_proxy.rebuild = False
		mock_bpy_context.scene.cqtc_tools_proxy.jpeg_quality = 17
		mock_bpy_context.selected_sequences = [
			bpy.types.ProxyableSequence(0, 100),
			bpy.types.ProxyableSequence(150, 200)
		]
		bpy.ops.sequencer.rebuild_proxy = mock.MagicMock()
		operator = SetProxyConfigOperator()
		operator.report = mock.MagicMock()
		
		
		result = operator.execute(mock_bpy_context)
		
		
		expected_info_reports = [ "2 strips modificadas" ]
		self.assert_operator_success(operator, result, expected_info_reports)
		for seq in mock_bpy_context.selected_sequences:
			assert seq.use_proxy
			assert seq.proxy.build_25
			assert 17 == seq.proxy.quality
		bpy.ops.sequencer.rebuild_proxy.assert_not_called()
	
	
	def test_set_proxy_config_operator_rebuild(self):
		import bpy.types
		import bpy.ops
		from cqtc_tools.set_proxy_config_operator import SetProxyConfigOperator
		mock_bpy_context = mock.MagicMock()
		mock_bpy_context.scene.cqtc_tools_proxy.rebuild = True
		mock_bpy_context.selected_sequences = [
			bpy.types.ProxyableSequence(0, 100),
			bpy.types.ProxyableSequence(150, 200)
		]
		bpy.ops.sequencer.rebuild_proxy = mock.MagicMock()
		operator = SetProxyConfigOperator()
		operator.report = mock.MagicMock()
		
		
		result = operator.execute(mock_bpy_context)
		
		
		expected_info_reports = [ "2 strips reconstruidas" ]
		self.assert_operator_success(operator, result, expected_info_reports)
		bpy.ops.sequencer.rebuild_proxy.assert_called_once_with()
		
		
		