bl_info = {
    "name": "Houdini Numpad Style Editor",
    "blender": (5, 1, 0),
    "category": "UI",
    "version": (1, 0, 0),
    "author": "DorVeytarn",
    "description": "Middle-click on number fields to get Houdini-style step selector",
}

from . import operators
from . import ui


def register():
    operators.register()
    ui.register()


def unregister():
    ui.unregister()
    operators.unregister()


if __name__ == "__main__":
    register()
