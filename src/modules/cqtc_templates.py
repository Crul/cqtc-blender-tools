from abc import ABCMeta, abstractproperty, abstractmethod
import bpy.props
import os
import cqtc_path
import cqtc_pickle
from cqtc_operator import CqtcOperator


def template_fullpath(template_filename):
	return os.path.join(cqtc_path.addons_path, "%s.pickle" % template_filename)


def load_templates(template_filename):
	return cqtc_pickle.load_pickle(template_fullpath(template_filename))


def draw_template_panel(addon_panel, addon_properties, addon_properties_name):
	layout = addon_panel.layout
	row = layout.row()
	row.prop(addon_properties, "template_expanded",
		icon="TRIA_DOWN" if addon_properties.template_expanded else "TRIA_RIGHT",
		icon_only=False
	)

	if not addon_properties.template_expanded:
		return
	
	borrar_btn_width = 0.1
	
	split = layout.row().split(percentage=0.80)
	
	split_1 = split.column().split(percentage=borrar_btn_width)			
	split_1.column().operator(addon_properties_name + ".remove_template", text="", icon="X")
	
	split_2 = split_1.split(percentage=0.25)
	split_2.column().label("Plantillas")
	split_2.column().prop(addon_properties, "template", text="")
	split.column().operator(addon_properties_name + ".load_template", text="Cargar", icon="FILE_REFRESH")
				
	split = layout.row().split(percentage=0.80)
	split_3 = split.column().split(percentage=borrar_btn_width)
	split_3.column()
	
	split_4 = split_3.split(percentage=0.25)
	split_4.column().label("Nombre")
	
	split_5 = split_4.split(align=True, percentage=0.90)
	split_5.column(align=True).prop(addon_properties, "new_template_name", text="")
	clear_template_name_operator = split_5.column(align=True).operator(addon_properties_name + ".set_template_name", text="", icon="X")
	clear_template_name_operator.action = "CLEAR"
	load_template_name_operator = split_5.column(align=True).operator(addon_properties_name + ".set_template_name", text="", icon="NLA_PUSHDOWN")
	load_template_name_operator.action = "LOAD"
	
	split.column().operator(addon_properties_name + ".add_template", text="Guardar", icon="SAVE_COPY")
	
	if len([tmpl for tmpl in addon_properties.template_data if tmpl["name"] == addon_properties.new_template_name ]) > 0:
		split = layout.row().split(percentage=0.30)
		split.column()
		split.column().prop(addon_properties, "override_template")


class CqtcTemplateOperator(CqtcOperator):
	metaclass__ = ABCMeta

	@abstractmethod
	def get_addon_properties(self, context):
		pass

	@abstractproperty
	def template_filename(self):
		pass

	@property
	def template_fullpath(self):
		return template_fullpath(self.template_filename)


class AddCqtcTemplateOperator(CqtcTemplateOperator):
	metaclass__ = ABCMeta

	def execute(self, context):
		addon_properties = self.get_addon_properties(context)
		
		new_template_name = addon_properties.new_template_name
		if new_template_name == "":
			return self.return_error("Debe indicar el nombre de la plantilla.")
		
		new_template_data = addon_properties.to_dict()
		new_template_data["name"] = new_template_name
		old_template = [tmpl for tmpl in addon_properties.template_data if tmpl["name"] == new_template_name]
		if len(old_template) == 0:
			new_template_option = (new_template_name, new_template_name, "Plantilla personalizada")
			addon_properties.template_options.append(new_template_option)
			addon_properties.template_data.append(new_template_data)
		else:
			if not addon_properties.override_template and len(old_template) > 0:
				return self.return_error("Ya existe una plantilla llamada '" + new_template_name + "'")
			
			old_template_index = next(index for (index, tmpl) in enumerate(addon_properties.template_data) if tmpl["name"] == new_template_name)
			addon_properties.template_data[old_template_index] = new_template_data
				
		addon_properties.template = new_template_name
		
		cqtc_pickle.save_pickle(self.template_fullpath, addon_properties.template_data)
		
		addon_properties.new_template_name = ""
		addon_properties.override_template = False
	
		return {"FINISHED"}


class LoadCqtcTemplateOperator(CqtcTemplateOperator):
	metaclass__ = ABCMeta
	
	def execute(self, context):
		addon_properties = self.get_addon_properties(context)
		
		template = addon_properties.template
		if template is None or template == "":
			return self.return_error("Debe seleccionar una plantilla.")
		
		for tmpl in addon_properties.template_data:
			if tmpl["name"] == template:
				addon_properties.from_dict(tmpl)
				
		return {"FINISHED"}


class SetCqtcTemplateNameOperator(CqtcTemplateOperator):
	metaclass__ = ABCMeta
	
	@abstractproperty
	def action_parameter(self):
		pass
	
	def execute(self, context):
		addon_properties = self.get_addon_properties(context)
		
		template = addon_properties.template
		if self.action_parameter.upper() == "CLEAR":
			addon_properties.new_template_name = ""
		elif self.action_parameter.upper() == "LOAD":
			addon_properties.new_template_name = template
				
		return {"FINISHED"}


class RemoveCqtcTemplateOperator(CqtcTemplateOperator):
	metaclass__ = ABCMeta

	def execute(self, context):
		addon_properties = self.get_addon_properties(context)
		
		template = addon_properties.template
		for tmpl in addon_properties.template_options:
			if tmpl[0] == template:
				addon_properties.template_options.remove(tmpl)
	
		for tmpl in addon_properties.template_data:
			if tmpl["name"] == template:
				addon_properties.template_data.remove(tmpl)
		
		cqtc_pickle.save_pickle(self.template_fullpath, addon_properties.template_data)
		
		return {"FINISHED"}
	
	def invoke(self, context, event):
		addon_properties = self.get_addon_properties(context)
		
		template = addon_properties.template
		if template is None or template == "":
			return self.return_error("Debe seleccionar una plantilla.")
		
		return context.window_manager.invoke_confirm(self, event)

