import bpy.props
import os
import cqtc_path
import cqtc_pickle
from cqtc_operator import CqtcOperator

template_filename = "plantillas_super_efectos"
template_fullpath = os.path.join(cqtc_path.addons_path, "%s.pickle" % template_filename )
def load_templates():
	return cqtc_pickle.load_pickle(template_fullpath)

class AddSuperEffectTemplateOperator(CqtcOperator):
	bl_idname = "super_effect.add_template"
	bl_label = "Añadir Plantilla"
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		new_template_name = context.scene.super_effect.new_template_name
		if new_template_name == "":
			return self.return_error("Debe indicar el nombre de la plantilla.")
			
		new_template_data = context.scene.super_effect.to_dict()
		new_template_data["name"] = new_template_name
		old_template = [tmpl for tmpl in context.scene.super_effect.template_data if tmpl["name"] == new_template_name]
		if len(old_template) == 0:
			new_template_option = (new_template_name, new_template_name, "Plantilla personalizada")
			context.scene.super_effect.template_options.append(new_template_option)
			context.scene.super_effect.template_data.append(new_template_data)
		else:
			if not context.scene.super_effect.override_template and len(old_template) > 0:
				return self.return_error("Ya existe una plantilla llamada '" + new_template_name + "'")
			
			old_template_index = next(index for (index, tmpl) in enumerate(context.scene.super_effect.template_data) if tmpl["name"] == new_template_name)
			context.scene.super_effect.template_data[old_template_index] = new_template_data
				
		context.scene.super_effect.template = new_template_name
		
		cqtc_pickle.save_pickle(template_fullpath, context.scene.super_effect.template_data)
		
		context.scene.super_effect.new_template_name = ""
		context.scene.super_effect.override_template = False
	
		return {"FINISHED"}

class LoadSuperEffectTemplateOperator(CqtcOperator):
	bl_idname = "super_effect.load_template"
	bl_label = "Cargar Plantilla"
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		template = context.scene.super_effect.template
		if template is None or template == "":
			return self.return_error("Debe seleccionar una plantilla.")
		
		for tmpl in context.scene.super_effect.template_data:
			if tmpl["name"] == template:
				context.scene.super_effect.from_dict(tmpl)
				
		return {"FINISHED"}

class SetSuperEffectTemplateNameOperator(CqtcOperator):
	bl_idname = "super_effect.set_template_name"
	bl_label = "Poner nombre a la nueva plantilla"
	bl_options = {"REGISTER", "UNDO"}
	
	action =  bpy.props.StringProperty()

	def execute(self, context):
		template = context.scene.super_effect.template
		if self.action.upper() == "CLEAR":
			context.scene.super_effect.new_template_name = ""
		elif self.action.upper() == "LOAD":
			context.scene.super_effect.new_template_name = template
				
		return {"FINISHED"}

class RemoveSuperEffectTemplateOperator(CqtcOperator):
	bl_idname = "super_effect.remove_template"
	bl_label = "¿Estás seguro de que quieres borrar la plantilla seleccionada?"
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		template = context.scene.super_effect.template
		for tmpl in context.scene.super_effect.template_options:
			if tmpl[0] == template:
				context.scene.super_effect.template_options.remove(tmpl)
	
		for tmpl in context.scene.super_effect.template_data:
			if tmpl["name"] == template:
				context.scene.super_effect.template_data.remove(tmpl)
		
		cqtc_pickle.save_pickle(template_fullpath, context.scene.super_effect.template_data)
		
		return {"FINISHED"}
	
	def invoke(self, context, event):
		template = context.scene.super_effect.template
		if template is None or template == "":
			return self.return_error("Debe seleccionar una plantilla.")
		
		return context.window_manager.invoke_confirm(self, event)

