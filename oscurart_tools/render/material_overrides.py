# ------------------------------------------------


obDict = []
import bpy
from bpy.app.handlers import persistent


@persistent
def ApplyOverrides(dummy):
    global obDict

    for override in bpy.context.scene.ovlist:

        # set collections clean name
        collClean = override.colloverride
        obClean = override.oboverride



        if collClean != None:
            for ob in collClean.all_objects:
                if ob.type == "MESH": #si es un mesh
                    if not ob.hide_viewport and not ob.hide_render:
                        obDict.append([ob,[mat for mat in ob.data.materials]])
                if ob.type == "EMPTY": #si es un coleccion instance
                    if not ob.instance_collection == None:
                            for iob in ob.instance_collection.all_objects:
                                if iob.type == "MESH":
                                    if not iob.hide_viewport and not iob.hide_render:
                                        obDict.append([iob,[mat for mat in iob.data.materials]])
        else:
            obDict.append([obClean,[mat for mat in obClean.data.materials]])


    for override in bpy.context.scene.ovlist:

        # set collections clean name
        collClean = override.colloverride
        # set material clean name
        matClean = override.matoverride
        # set objeto clean name
        obClean = override.oboverride

        print(matClean)

        if collClean != None:
            for ob in collClean.all_objects:
                if ob.type == "MESH":
                    if not ob.hide_viewport and not ob.hide_render:
                        for i,mat  in enumerate(ob.data.materials):
                            ob.data.materials[i] = matClean
                if ob.type == "EMPTY":
                    if not ob.instance_collection == None:
                            for iob in ob.instance_collection.all_objects:
                                if iob.type == "MESH":
                                    if not iob.hide_viewport and not iob.hide_render:
                                        for i,mat  in enumerate(iob.data.materials):
                                            iob.data.materials[i] = matClean
        else:
            if obClean.type == "MESH":
                if not obClean.hide_viewport and not obClean.hide_render:
                      for i,mat  in enumerate(obClean.data.materials):
                             obClean.data.materials[i] = matClean


@persistent
def RestoreOverrides(dummy):
    global obDict

    for set in obDict:
        for i,mat in enumerate(set[1]):
            set[0].data.materials[i] = mat

    obDict = []


# ---------------------------------------------------



class OscOverridesProp(bpy.types.PropertyGroup):
    colloverride: bpy.props.PointerProperty(
                name="Collection Override",
                type=bpy.types.Collection,
                description="All objects in this collection will be override",
                )
    oboverride: bpy.props.PointerProperty(
                name="Object Override",
                type=bpy.types.Object,
                description="Only this object will be override.",
                )
    matoverride: bpy.props.PointerProperty(
                name="Material Override",
                type=bpy.types.Material,
                description="Material for override objects",
                )

bpy.utils.register_class(OscOverridesProp)
bpy.types.Scene.ovlist = bpy.props.CollectionProperty(type=OscOverridesProp)


class OVERRIDES_PT_OscOverridesGUI(bpy.types.Panel):
    bl_label = "Oscurart Material Overrides"
    bl_idname = "OVERRIDES_PT_layout"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        layout = self.layout
        col = layout.column(align=1)
        colrow = col.row(align=1)
        colrow.operator("render.overrides_add_slot")
        colrow.operator("render.overrides_remove_slot")
        col.operator("render.overrides_transfer")
        for i, m in enumerate(bpy.context.scene.ovlist):
            colrow = col.row(align=1)
            colrow.prop(m, "colloverride", text="")
            colrow.prop(m, "oboverride", text="")
            colrow.prop(m, "matoverride", text="")
            if i != len(bpy.context.scene.ovlist) - 1:
                pa = colrow.operator(
                    "ovlist.move_down",
                    text="",
                    icon="TRIA_DOWN")
                pa.index = i
            if i > 0:
                p = colrow.operator("ovlist.move_up", text="", icon="TRIA_UP")
                p.index = i
            pb = colrow.operator("ovlist.kill", text="", icon="X")
            pb.index = i


class OscTransferOverrides(bpy.types.Operator):
    """Applies the previously configured slots (Groups < Material) to the Scene. """ \
    """This should be transfer once the override groups are set"""
    bl_idname = "render.overrides_transfer"
    bl_label = "Transfer Overrides"

    def execute(self, context):
        # CREO LISTA
        OSCOV = [[OVERRIDE.grooverride, OVERRIDE.matoverride]
                 for OVERRIDE in bpy.context.scene.ovlist[:]
                 if OVERRIDE.matoverride != "" and OVERRIDE.grooverride != ""]

        bpy.context.scene.oscurart.overrides = str(OSCOV)
        return {'FINISHED'}


class OscAddOverridesSlot(bpy.types.Operator):
    """Add override slot"""
    bl_idname = "render.overrides_add_slot"
    bl_label = "Add Override Slot"

    def execute(self, context):
        prop = bpy.context.scene.ovlist.add()
        prop.matoverride = None
        prop.grooverride = None
        return {'FINISHED'}


class OscRemoveOverridesSlot(bpy.types.Operator):
    """Remove override slot"""
    bl_idname = "render.overrides_remove_slot"
    bl_label = "Remove Override Slot"

    def execute(self, context):
        context.scene.ovlist.remove(len(bpy.context.scene.ovlist) - 1)
        return {'FINISHED'}

class OscOverridesUp(bpy.types.Operator):
    """Move override slot up"""
    bl_idname = 'ovlist.move_up'
    bl_label = 'Move Override up'
    bl_options = {'INTERNAL'}

    index: bpy.props.IntProperty(min=0)

    @classmethod
    def poll(self, context):
        return len(context.scene.ovlist)

    def execute(self, context):
        ovlist = context.scene.ovlist
        ovlist.move(self.index, self.index - 1)

        return {'FINISHED'}


class OscOverridesDown(bpy.types.Operator):
    """Move override slot down"""
    bl_idname = 'ovlist.move_down'
    bl_label = 'Move Override down'
    bl_options = {'INTERNAL'}

    index: bpy.props.IntProperty(min=0)

    @classmethod
    def poll(self, context):
        return len(context.scene.ovlist)

    def execute(self, context):
        ovlist = context.scene.ovlist
        ovlist.move(self.index, self.index + 1)
        return {'FINISHED'}


class OscOverridesKill(bpy.types.Operator):
    """Remove override slot"""
    bl_idname = 'ovlist.kill'
    bl_label = 'Kill Override'
    bl_options = {'INTERNAL'}

    index: bpy.props.IntProperty(min=0)

    @classmethod
    def poll(self, context):
        return len(context.scene.ovlist)

    def execute(self, context):
        ovlist = context.scene.ovlist
        ovlist.remove(self.index)
        return {'FINISHED'}
