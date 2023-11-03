import unittest
from copy import deepcopy

from VXTool.app import App
from VXTool.project import CONFIG_DEFAULTS
from VXTool.font import FontBank

class DryLaunchTests(unittest.TestCase):
    def test_empty_init(self):
        app = App()
    
    def test_default_init(self):
        config = deepcopy(CONFIG_DEFAULTS)
        app = App()
        app.init_render_context(FontBank())
        app.apply_config(config)

    def test_render_size_creates_render_texture(self):
        config = deepcopy(CONFIG_DEFAULTS)
        render_size = (320, 160)
        config["render_size"] = render_size
        app = App()
        app.init_render_context(FontBank())
        app.apply_config(config)
        self.assertIsNotNone(app._render_tex)
        self.assertTupleEqual(app._render_tex.get_rect().size, render_size)

    def test_no_render_size_raises_error(self):
        config = deepcopy(CONFIG_DEFAULTS)
        del config["render_size"]
        app = App()
        with self.assertRaises(ValueError) as err:
            app.init_render_context(FontBank())
            app.apply_config(config)

    