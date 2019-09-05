# -*- coding: utf-8 -*-
bl_info = {
    "name": "SkRender",
    "author": "sk",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Render > SkRender",
    "description": "SkRender",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Render",
    }
# import bpy
# from . import core
import os
if "bpy" in locals():
    if bpy.app.version < (2, 71, 0):
        import imp as importlib
    else:
        import importlib
    importlib.reload(core)

else:
    import bpy
    import logging
    from . import core


class SkRender(bpy.types.Operator):
    """Object Cursor Array"""
    bl_idname = "render.sk_render"
    bl_label = "SkRender"
    bl_options = {'REGISTER','UNDO'}

    total: bpy.props.IntProperty(name="Steps", default=2, min=1, max=100)

    def __init__(self):
        self.loader=core.data.Loader()
    def execute(self, context):
        self.loader.load(context)
        for m in self.loader.scene:
            print("\t-\t-\t-\t-\t-\t-\t-")
            print(m.Trans)
            print(m.Mat)
            print(len(m.Vertices).__str__()+"\t"+len(m.Indices).__str__())
            print((m.Indices))
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(SkRender.bl_idname)

# store keymaps here to access after registration
addon_keymaps = []

def register():
    bpy.utils.register_class(SkRender)
    bpy.types.TOPBAR_MT_render.append(menu_func)
     # handle the keymap
    wm = bpy.context.window_manager
    # Note that in background mode (no GUI available), keyconfigs are not available either,
    # so we have to check this to avoid nasty errors in background case.
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(SkRender.bl_idname, 'T', 'PRESS', ctrl=True, shift=True)
        kmi.properties.total = 4
        addon_keymaps.append((km, kmi))


def unregister():
    # Note: when unregistering, it's usually good practice to do it in reverse order you registered.
    # Can avoid strange issues like keymap still referring to operators already unregistered...
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    bpy.utils.unregister_class(SkRender)
    bpy.types.TOPBAR_MT_render.remove(menu_func)


if __name__ == "__main__":
    register()