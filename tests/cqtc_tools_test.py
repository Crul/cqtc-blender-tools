from unittest import mock

class TestCqtcTools():

	@mock.patch('bpy.props.IntProperty')
	@mock.patch('bpy.props.BoolProperty')
	def test_zoom_properties(self, MockBoolProperty, MockIntProperty):
		from cqtc_tools.set_proxy_config_properties import SetProxyConfigProperties
		
		properties = SetProxyConfigProperties()
		
		assert properties is not None
