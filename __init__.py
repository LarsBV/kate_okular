# -*- coding: utf-8 -*-
"""Okular plugin, for previewing stuff, That includes synctex sup."""

from .okular_plugin import *


@kate.init
def init():
  global okular_plugin
  okular_plugin = OkularPlugin()
  
@kate.unload
def unload():
    global okular_plugin
    if okular_plugin:
        del okular_plugin
        okular_plugin = None
