class Property:
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

BoolProperty = Property
EnumProperty = Property
FloatProperty = Property
IntProperty = Property
StringProperty = Property

class FloatVectorProperty(Property):
	r = 0
	g = 0
	b = 0
