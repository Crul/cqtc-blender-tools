from abc import ABCMeta

class Property:
	metaclass__ = ABCMeta
	
	def __new__(self,
		name = None,
		description = None,
		default = None,
		min = None,
		max = None,
		step = None,
		subtype = None,
		items = None,
		update = None,
		precision = None
	):
		return default

class BoolProperty(Property):
	pass

class EnumProperty(Property):
	pass

class FloatProperty(Property):
	pass

class IntProperty(Property):
	pass

class StringProperty(Property):
	pass

class FloatVectorProperty(Property):
	r = 0
	g = 0
	b = 0
