from unittest import mock

class TestCqtcSuperEffects():

	@mock.patch("bpy.props.IntProperty")
	@mock.patch("bpy.props.FloatProperty")
	@mock.patch("bpy.props.BoolProperty")
	def test_properties(self, MockBoolProperty, MockFloatProperty, MockIntProperty):
		from cqtc_super_effects.super_effect_properties import SuperEffectProperties
		
		properties = SuperEffectProperties()
		
		assert properties is not None
