import bpy


def register():
    """Register keyboard mapping for the addon"""
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    
    if kc:
        km = kc.keymaps.new(name="Window", space_type='EMPTY', region_type='WINDOW', modal=False)
        kmi = km.keymap_items.new('wm.houdini_numpad_editor', 'MIDDLEMOUSE', 'PRESS', alt=True)


def unregister():
    """Unregister keyboard mapping"""
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    
    if kc:
        for km in kc.keymaps:
            if km.name == "Window":
                for kmi in km.keymap_items:
                    if kmi.idname == 'wm.houdini_numpad_editor':
                        km.keymap_items.remove(kmi)
