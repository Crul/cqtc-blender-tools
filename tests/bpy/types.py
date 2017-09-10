class AnimationDataAction():
	fcurves = {}

class AnimationData():
	action = AnimationDataAction()

class Area:
	type = ""

class Render:
	resolution_x = 1920
	resolution_y = 1080

class Context:
	selected_sequences = []
	
	def __init__(self):
		self.scene = Scene()
		self.area = Area()

class FCurve():
	keyframe_points = {}

class Graph:
	def interpolation_type(self, type):
		pass

class KeyframePoint():
	select_control_point = True

class Operator:
	def report(self, foo1, foo2):
		pass

class Scene:
	super_effect = None
	animation_data = None
	
	def __init__(self):
		self.sequence_editor = SequenceEditor()
		self.render = Render()
	
	def animation_data_create(self):
		self.animation_data = AnimationData()
	
	def update(self):
		pass

class SequenceElement:
	orig_width = 0
	orig_height = 0

class SequenceScene:
	audio_volume = 1
	frame_end = 200

	def keyframe_insert(self, property_name, index=-1, frame=0):
		pass
	
class SequenceEditor():
	def __init__(self):
		self.sequences = Sequences()

class SequenceTransform:
	offset_x = 0
	offset_y = 0
	
	def keyframe_insert(self, property_name, index=-1, frame=0):
		pass

class Sequence:
	select = True
	name = ""
	type = ""
	elements = []
	transform = None
	input_1 = None
	channel = 0
	frame_final_start = 0
	frame_final_end = 0
	frame_final_duration = 0
	frame_offset_start = 0
	frame_offset_end = 0
	
	def __init__(self):
		self.transform = SequenceTransform()

	def keyframe_insert(self, property_name, index=-1, frame=0):
		pass
	
class Sequences():
	def __iter__(self):
		return iter([])

	def new_effect(name, effect_type, channel, frame_start, frame_end, seq1=None, seq2=None):
		pass

class VolumeSequence(Sequence):
	volume = 1
		
class VolumeSceneSequence(Sequence):
	scene = None
	
	def __init__(self):
		super(VolumeSceneSequence, self).__init__()
		self.scene = SequenceScene()
	
Panel = object

PropertyGroup = object
