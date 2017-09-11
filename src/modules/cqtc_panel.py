from abc import ABCMeta
import bpy.types
from bpy.app.translations import pgettext

class CqtcPanel(bpy.types.Panel):
	metaclass__ = ABCMeta
	
	def operator_i18n(self, layout_obj, operator_name, operator_text):
		return layout_obj.operator(operator_name, text=self.translate(operator_text))

	def translate(self, text):
		return pgettext(text)
		
	@classmethod
	def translate_cls(cls, text):
		return pgettext(text)
