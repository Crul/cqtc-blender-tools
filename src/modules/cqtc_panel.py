from abc import ABCMeta
import bpy.types
from bpy.app.translations import pgettext

class CqtcPanel(bpy.types.Panel):
	metaclass__ = ABCMeta
	
	def draw_selected_sequences_info(self, layout_obj, context):
		selected_sequences_count = len(context.selected_sequences) if context.selected_sequences else 0
		layout_obj.row().label("%i %s" % (selected_sequences_count, self.translate("selected strips")))
	
	def operator_i18n(self, layout_obj, operator_name, operator_text):
		return layout_obj.operator(operator_name, text=self.translate(operator_text))

	def translate(self, text):
		return pgettext(text)
		
	@classmethod
	def translate_cls(cls, text):
		return pgettext(text)
