import bpy.types
import os
import cqtc_path
import cqtc_pickle

template_filename = "plantillas_subtitulos"
template_fullpath = os.path.join(cqtc_path.addons_path, "%s.pickle" % template_filename )
def load_templates():
	return cqtc_pickle.load_pickle(template_fullpath)

class AddSubtitleTemplateOperator(bpy.types.Operator):
	bl_idname = "subtitle.add_template"
	bl_label = "Añadir Plantilla"
	bl_options = {"REGISTER", "UNDO"}
	
	def execute(self, context):
		new_template_name = context.scene.subtitle.new_template_name
		if new_template_name == "":
			self.report({"ERROR"}, "Debe indicar el nombre de la plantilla.")
			return {"CANCELLED"}
		
		for tmpl in context.scene.subtitle.template_data:
			if tmpl["name"] == new_template_name:
				self.report({"ERROR"}, "Ya existe una plantilla llamada '" + new_template_name + "'")
				return {"CANCELLED"}
		
		new_template_option = (new_template_name, new_template_name, "Plantilla personalizada")
		context.scene.subtitle.template_options.append(new_template_option)
		
		new_template_data = context.scene.subtitle.to_dict()
		new_template_data["name"] = new_template_name
		context.scene.subtitle.template_data.append(new_template_data)
		
		cqtc_pickle.save_pickle(template_file_path, context.scene.subtitle.template_data)
		
		context.scene.subtitle.new_template_name = ""
		
		return {"FINISHED"}


class LoadSubtitleTemplateOperator(bpy.types.Operator):
	bl_idname = "subtitle.load_template"
	bl_label = "Cargar Plantilla"
	bl_options = {"REGISTER", "UNDO"}
	
	def execute(self, context):
		template = context.scene.subtitle.template
		if template is None or template == "":
			self.report({"ERROR"}, "Debe seleccionar una plantilla.")
			return {"CANCELLED"}
		
		for tmpl in context.scene.subtitle.template_data:
			if tmpl["name"] == template:
				context.scene.subtitle.from_dict(tmpl)
		
		return {"FINISHED"}


class RemoveSubtitleTemplateOperator(bpy.types.Operator):
	bl_idname = "subtitle.remove_template"
	bl_label = "¿Estás seguro de que quieres borrar la plantilla seleccionada?"
	bl_options = {"REGISTER", "UNDO"}
	
	def execute(self, context):
		template = context.scene.subtitle.template
		for tmpl in context.scene.subtitle.template_options:
			if tmpl[0] == template:
				context.scene.subtitle.template_options.remove(tmpl)
		
		for tmpl in context.scene.subtitle.template_data:
			if tmpl["name"] == template:
				context.scene.subtitle.template_data.remove(tmpl)
		
		cqtc_pickle.save_pickle(template_file_path, context.scene.subtitle.template_data)
		
		return {"FINISHED"}
	
	def invoke(self, context, event):
		template = context.scene.subtitle.template
		if template is None or template == "":
			self.report({"ERROR"}, "Debe seleccionar una plantilla.")
			return {"CANCELLED"}
		
		return context.window_manager.invoke_confirm(self, event)
