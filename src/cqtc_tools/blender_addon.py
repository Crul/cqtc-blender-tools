import bpy.props
import bpy.types
import bpy.utils
from .cqtc_tools_panel import CqtcToolsPanel
from .set_proxy_config_properties import SetProxyConfigProperties
from .change_strips_channel_operator import ChangeStripsChannelOperator
from .set_proxy_config_operator import SetProxyConfigOperator


def register():
	bpy.utils.register_class(ChangeStripsChannelOperator)
	bpy.utils.register_class(SetProxyConfigOperator)
	bpy.utils.register_class(CqtcToolsPanel)
	bpy.utils.register_class(SetProxyConfigProperties)
	bpy.types.Scene.cqtc_tools_proxy = bpy.props.PointerProperty(type=SetProxyConfigProperties)


def unregister():
	bpy.utils.unregister_class(ChangeStripsChannelOperator)
	bpy.utils.unregister_class(SetProxyConfigOperator)
	bpy.utils.unregister_class(CqtcToolsPanel)
	bpy.utils.unregister_class(SetProxyConfigProperties)
	del bpy.types.Scene.cqtc_tools_proxy


if __name__ == "__main__":
	register()
