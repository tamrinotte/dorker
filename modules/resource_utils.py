# -*- coding: utf-8 -*-

# MODULES AND/OR LIBRARIES
import sys
from pathlib import Path

##############################

# LOAD RESOURCE PATH

##############################

def load_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path.cwd()

    return Path(base_path, relative_path)