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
	
	def __init__(self,
		frame_final_start,
		frame_final_end,
		frame_offset_start = 0,
		frame_offset_end = 0
	):
		self.transform = SequenceTransform()
		self.select = True
		self.name = ""
		self.type = ""
		self.elements = []
		self.input_1 = None
		self.channel = 0
		self.frame_final_start = frame_final_start
		self.frame_final_end = frame_final_end
		self._frame_start = frame_final_start - frame_offset_start
		self._frame_offset_start = frame_offset_start
		self._frame_offset_end = frame_offset_end
	
	@property
	def frame_start(self):
		return self._frame_start
		
	@frame_start.setter
	def frame_start(self, value):
		diff = (value - self._frame_start)
		self.frame_final_start += diff
		self.frame_final_end += diff
		self._frame_start = value
		
	@property
	def frame_final_duration(self):
		return self.frame_final_end - self.frame_final_start
	
	@property
	def frame_offset_start(self):
		return self._frame_offset_start
	
	@frame_offset_start.setter
	def frame_offset_start(self, value):
		diff = (value - self._frame_offset_start)
		self.frame_final_start += diff
		self._frame_offset_start = value
	
	@property
	def frame_offset_end(self):
		return self._frame_offset_end
	
	@frame_offset_end.setter
	def frame_offset_end(self, value):
		diff = (value - self._frame_offset_end)
		self.frame_final_end -= diff
		self._frame_offset_end = value
	
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
	
	def __init__(self,
		frame_final_start,
		frame_final_end,
		frame_offset_start = 0,
		frame_offset_end = 0
	):
		super(VolumeSceneSequence, self).__init__(
			frame_final_start,
			frame_final_end,
			frame_offset_start,
			frame_offset_end
		)
		self.scene = SequenceScene()
	
Panel = object

PropertyGroup = object
