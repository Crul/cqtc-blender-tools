from unittest import mock

class TestCqtcSubtitles:

	def test_panel(self):
		from cqtc_subtitles.subtitles_panel import SubtitlesPanel
		
		panel = SubtitlesPanel()
		
		assert panel is not None

	def test_templates(self):
		from cqtc_subtitles import templates
		
		set_template_name_operator = templates.SetSubtitleTemplateNameOperator()
		
		assert set_template_name_operator is not None
		assert "action" in dir(set_template_name_operator)
