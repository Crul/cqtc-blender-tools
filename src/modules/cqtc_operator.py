from abc import ABCMeta
import bpy.types
from bpy.app.translations import pgettext

class CqtcOperator(bpy.types.Operator):
	metaclass__ = ABCMeta

	def return_error(self, error):
		self.report({ "ERROR" }, self.translate(error))
		return {"CANCELLED"}

	def translate(self, text):
		return pgettext(text)
