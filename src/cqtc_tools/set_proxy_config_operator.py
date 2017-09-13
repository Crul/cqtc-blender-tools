import bpy.ops
from cqtc_operator import CqtcOperator

class SetProxyConfigOperator(CqtcOperator):
	bl_idname = "cqtc_tools_proxy.set_proxy"
	bl_label = "Aplicar configuración Proxy"
	
	def execute(self, context):
		proxyable_sequences = [seq for seq in context.selected_sequences if "proxy" in dir(seq)]
		error = self.__validate(context, proxyable_sequences)
		if error:
			return self.return_error(error)
		
		for sequence in proxyable_sequences:
			sequence.use_proxy = True
			sequence.proxy.quality = context.scene.cqtc_tools_proxy.jpeg_quality
			sequence.proxy.build_25 = True
		
		sequence_operation = "modificadas"
		if context.scene.cqtc_tools_proxy.rebuild:
			bpy.ops.sequencer.rebuild_proxy()
			sequence_operation  = "reconstruidas"
			
		self.report({"INFO"}, "%i strips %s" % (len(proxyable_sequences), sequence_operation))
		
		return {"FINISHED"}
	
	
	def __validate(self, context, proxyable_sequences):
		if len(context.selected_sequences) == 0:
			return "No hay strips seleccionadas"
		
		if len(proxyable_sequences) == 0:
			return "No se puede aplicar el proxy a ninguna de las strips seleccionadas"
