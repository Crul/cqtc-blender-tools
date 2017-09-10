from abc import ABCMeta
import bpy.types

class CqtcOperator(bpy.types.Operator):
	metaclass__ = ABCMeta

	def return_error(self, error):
		self.report({ "ERROR" }, error)
		return {"CANCELLED"}
