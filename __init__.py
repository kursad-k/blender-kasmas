

from mathutils import Vector, Matrix
from bpy.props import IntProperty, FloatProperty, BoolProperty, FloatVectorProperty, StringProperty
import bmesh
import bpy
from bpy_extras import view3d_utils
import blf
bl_info = {
    "name": "KasMas",
    "author": "Kursad Karatas",
    "description": "componenets",
    "blender": (2, 80, 0),
    "version": (0, 1),
    "location": "",
    "warning": "",
    "category": "Generic"
}


print("TEST")


def defineObjectProps():

    try:
        bool(bpy.types.Object.ezlattice_flag)

    except:
        bpy.types.Object.kasmas_isprofile = BoolProperty(
            name="IsMuscleProfile", default=False, update=update_kasmasfunc)
        bpy.types.Object.kasmas_profile = StringProperty(
            name="MuscleProfile", default="")


def update_kasmasfunc(self, context):

    if context.object.kasmas_isprofile:
        cr = context.object
        cr_name = cr.name
        profile_name = ".profilemuscle"+"_"+cr_name

        scale = cr.data.bevel_depth

        c = [o for o in context.scene.objects if o.type ==
             "CURVE" and o.name == profile_name]
        print(c)
        if len(c) < 1:
            bpy.ops.curve.primitive_bezier_circle_add(
                enter_editmode=False, location=(0, 0, 0))
            profile = context.object
            profile.name = profile_name
            profile.scale = Vector((scale, scale, scale))

        else:
            profile = [o for o in context.scene.objects if o.type ==
                       "CURVE" and o.name == profile_name][0]

        cr = [o for o in context.scene.objects if o.type ==
              "CURVE" and o.name == cr_name]

        if len(cr) > 0:

            setSelectActiveObject(context, cr[0])

            context.object.data.bevel_object = profile
            context.object.data.use_fill_caps = True

            context.object.kasmas_profile = profile_name

    else:
        context.object.data.bevel_object = None


def isEditMode():
    """Check to see we are in edit  mode
    """
    if bpy.context.object.mode == "EDIT":
        return True

    else:
        return False


def objectMode():

    if isEditMode():
        bpy.ops.object.mode_set(mode="OBJECT")

    else:
        return True

    return


def editMode():

    if not isEditMode():
        bpy.ops.object.mode_set(mode="EDIT")

    else:
        return False


def setActiveObject(obj):
    bpy.context.view_layer.objects.active = obj


def selectObject(obj):
    obj.select_set(True)


def setSelectActiveObject(context, obj):

    if context.mode == 'OBJECT':

        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = obj
        obj.select_set(True)


def relocateCursor(context, event, obj):

    scene = context.scene
    region = context.region
    rv3d = context.region_data
    coord = event.mouse_region_x, event.mouse_region_y

    obj = obj
    matrix = obj.matrix_world

    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

    ray_target = ray_origin + view_vector

    def visible_objects_and_duplis():
        """Loop over (object, matrix) pairs (mesh only)"""

        depsgraph = context.evaluated_depsgraph_get()
        for dup in depsgraph.object_instances:
            if dup.is_instance:
                obj = dup.instance_object
                yield (obj, dup.matrix_world.copy())
            else:
                obj = dup.object
                yield (obj, obj.matrix_world.copy())

    def obj_ray_cast(obj, matrix):
        """Wrapper for ray casting that moves the ray into object space"""

        matrix_inv = matrix.inverted()
        ray_origin_obj = matrix_inv @ ray_origin
        ray_target_obj = matrix_inv @ ray_target
        ray_direction_obj = ray_target_obj - ray_origin_obj

        success, location, normal, face_index = obj.ray_cast(
            ray_origin_obj, ray_direction_obj)

        if success:
            return location, normal, face_index
        else:
            return None, None, None

    best_length_squared = -1.0
    best_obj = None

    hit, normal, face_index = obj_ray_cast(obj, matrix)
    if hit is not None:
        hit_world = matrix @ hit
        scene.cursor.location = hit_world
        length_squared = (hit_world - ray_origin).length_squared
        if best_obj is None or length_squared < best_length_squared:
            best_length_squared = length_squared
            best_obj = obj

    if best_obj is not None:

        best_original = best_obj.original
        best_original.select_set(True)
        context.view_layer.objects.active = best_original


def getCurvePointLocation(crv, i):
    data = crv.data

    loc = data.splines[0].bezier_points[i].co.copy()

    return loc


def makeProfileCurve(loc=Vector((1, 1, 0))):

    bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=True,
                                             location=loc)

    curve = bpy.context.object
    curve.name = ".curveprofile"

    bpy.ops.curve.normals_make_consistent()
    bpy.ops.curve.subdivide()
    data = curve.data

    i0 = getCurvePointLocation(curve, 0)
    i1 = getCurvePointLocation(curve, 1)
    i2 = getCurvePointLocation(curve, 2)

    data.splines[0].bezier_points[0].co = i0+Vector((0, 0.1/2, 0))
    data.splines[0].bezier_points[1].co = Vector((0, 1, 0))
    data.splines[0].bezier_points[2].co = i2+Vector((0, 0.1/2, 0))


def setCurvePoint(co=[]):

    cr = bpy.data.objects["BezierCurve"]
    cr.location = Vector((0, 0, 0))

    c1 = Vector((co[0].x, co[0].y, co[0].z))
    c2 = Vector((co[1].x, co[1].y, co[1].z))

    data.splines[0].bezier_points[0].co = c1
    data.splines[0].bezier_points[2].co = c2
    data.splines[0].bezier_points[1].co = (c2+c1)/2


def makeMuscle(co=[]):
    ob = bpy.context.object

    bpy.ops.object.select_all(action='DESELECT')

    bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=True)
    cr = bpy.context.object
    bpy.ops.curve.handle_type_set(type='VECTOR')

    bpy.ops.curve.subdivide()
    bpy.ops.curve.handle_type_set(type='AUTOMATIC')

    cr.location = Vector((0, 0, 0))
    data = bpy.data.objects["BezierCurve"].data
    data = cr.data

    c1 = Vector((co[0].x, co[0].y, co[0].z))
    c2 = Vector((co[1].x, co[1].y, co[1].z))

    data.splines[0].bezier_points[0].co = c1
    data.splines[0].bezier_points[2].co = c2
    data.splines[0].bezier_points[1].co = (c2+c1)/2

    cr.data.bevel_depth = 0.1

    data.splines[0].bezier_points[1].radius = (c2-c1).length
    data.splines[0].bezier_points[0].radius = (c2-c1).length/3
    data.splines[0].bezier_points[2].radius = (c2-c1).length/3

    cr.data.use_uv_as_generated = True
    cr.data.materials.append(bpy.data.materials['MUSCLE_A'])

    cr.data.splines[0].tilt_interpolation = 'EASE'
    cr.data.splines[0].radius_interpolation = 'EASE'

    bpy.ops.object.modifier_add(type='SHRINKWRAP')

    bpy.context.object.modifiers["Shrinkwrap"].target = bpy.data.objects[ob.name]
    bpy.context.object.modifiers["Shrinkwrap"].use_apply_on_spline = True

    bpy.ops.object.modifier_add(type='MIRROR')

    bpy.context.object.modifiers["Mirror"].mirror_object = bpy.data.objects[ob.name]

    return cr


def getVertSel():

    obj = bpy.context.edit_object
    obj.update_from_editmode()

    m = obj.matrix_world
    me = obj.data

    bm = bmesh.from_edit_mesh(me)

    mode = bm.select_mode

    print(mode)

    co = Vector((0.0, 0.0, 0.0))
    vv = []
    if bm.select_mode == {'VERT'}:

        for v in bm.select_history:
            co = m@v.co

            vv.append(co)

    return vv


def draw_pipe_options(self, context):
    if context.object.type == 'CURVE':
        segments = context.object.data.bevel_resolution
        pipe_width = context.object.data.bevel_depth
        width = context.area.width
        font_id = 0
        blf.color(font_id, 1, 1, 1, 1)
        blf.position(font_id, width / 2 - 100, 140, 0)
        blf.size(font_id, 30, 60)
        blf.draw(font_id, "Segments: ")

        blf.position(font_id, width / 2 - 100, 100, 0)
        blf.draw(font_id, "Width: ")

        blf.position(font_id, width / 2 - 100, 60, 0)
        blf.draw(font_id, "Fill Caps: ")

        blf.color(font_id, 253, 253, 0, 1)
        blf.position(font_id, width / 2 + 35, 140, 0)
        blf.size(font_id, 30, 60)
        blf.draw(font_id, str(4 + segments * 2))

        blf.position(font_id, width / 2 - 14, 100, 0)
        blf.draw(font_id, str("%.3f" % pipe_width))

        blf.position(font_id, width / 2 + 16, 60, 0)


def returnCurveData(self):

    crv = [o for o in bpy.data.objects if o.name == self.curve_name]
    if len(crv) > 0:
        return crv[0].data

    else:
        return None


class OBJECT_PT_KASMAS(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "KasMas Tools"
    bl_idname = "KasMas_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        crv = [o for o in context.scene.objects if o.type ==
               "CURVE" and o.select_get()]

        if len(crv) > 0:
            cr = crv[0]
            crv = crv[0].data

            p0 = crv.splines[0].bezier_points[0]
            p1 = crv.splines[0].bezier_points[1]
            p2 = crv.splines[0].bezier_points[2]

            layout.label(text=" Muscle Props")

            row = layout.row()
            row.prop(cr, "kasmas_isprofile", text="use profile")

            if cr.kasmas_isprofile:
                prf = [o for o in context.scene.objects if o.name ==
                       cr.kasmas_profile]

                if len(prf) > 0:

                    row = layout.row()
                    row.prop(prf[0], "scale", text="Profile")

            row = layout.row()
            row.prop(crv, "offset", text="depth")

            row = layout.row()
            row.prop(crv, "extrude", text="flatness")

            row = layout.row()
            row.prop(crv, "bevel_depth", text="thickness")

            layout.label(text="Detailing")
            layout.label(text="Tilts")
            row = layout.row(align=True)

            row.prop(p0, "tilt", text="tilt start")
            row = layout.row()
            row.prop(p1, "tilt", text="tilt middle")
            row = layout.row()
            row.prop(p2, "tilt", text="tilt end")
            row = layout.row()

            layout.label(text="Sizing")
            row = layout.row(align=True)

            row.prop(p0, "radius", text="size start")
            row = layout.row()
            row.prop(p1, "radius", text="size middle")
            row = layout.row()
            row.prop(p2, "radius", text="size end")
            row = layout.row()

            split = layout.split()

            layout.label(text="Spatial")

            row = layout.row(align=True)
            row.prop(p0, "co", text="start")
            row = layout.row()
            row.prop(p1, "co", text="mid")
            row = layout.row()
            row.prop(p2, "co", text="end")


class OBJECT_OT_KasMas(bpy.types.Operator):
    """Move an object with the mouse, example"""
    bl_idname = "object.kasmas"
    bl_label = "KasMas"

    first_mouse_x: IntProperty()
    first_value: FloatProperty()
    click_timer: IntProperty(default=0)

    first_click: BoolProperty(default=False)
    second_click: BoolProperty(default=False)
    third_click: BoolProperty(default=False)

    first_loc: FloatVectorProperty(
        name="FirstLocation", description="", default=(0.0, 0.0, 0.0))
    mid_loc: FloatVectorProperty(
        name="FirstLocation", description="", default=(0.0, 0.0, 0.0))
    last_loc: FloatVectorProperty(
        name="FirstLocation", description="", default=(0.0, 0.0, 0.0))

    curve_name: StringProperty()

    flag_depth: BoolProperty(default=False)
    flag_radius: BoolProperty(default=False)

    depth_initial: FloatProperty(
        name="DepthInitial", description="", default=0.0)

    def resetFlags(self):

        self.flag_depth = False
        self.flag_radius = False

    def modal(self, context, event):

        scene = context.scene
        region = context.region
        rv3d = context.region_data
        coord = event.mouse_region_x, event.mouse_region_y

        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        ray_target = ray_origin + (view_vector * 1000)
        ray_target.normalized()

        obj = context.object
        m = obj.matrix_world

        points = []

        if event.type == 'MIDDLEMOUSE':

            return {'PASS_THROUGH'}

        if event.type == 'MIDDLEMOUSE' and event.value == "PRESS":

            return {'PASS_THROUGH'}

        if event.type == 'LEFTMOUSE':

            self.resetFlags()

            self.first_click = True

            if context.object.mode == 'EDIT':

                vv = [v for v in obj.data.vertices if v.select]

                loc = Vector((0, 0, 0))
                if len(vv) == 1:
                    bpy.context.scene.cursor.location = m@vv[-1].co
                if len(vv) > 1:
                    for v in vv:
                        loc += m@v.co

                    bpy.context.scene.cursor.location = loc/len(vv)

                bpy.context.view_layer.update()
                obj.update_from_editmode()

            if self.first_click and self.click_timer == 0 and event.value == "RELEASE":
                print("First Click")

                self.click_timer += 1

                self.first_click = False

                relocateCursor(context, event, obj)

                self.first_loc = context.scene.cursor.location.copy()

            if self.first_click and self.click_timer > 0 and event.value == "RELEASE":

                print("Second Click")
                relocateCursor(context, event, obj)
                self.last_loc = context.scene.cursor.location.copy()

                self.click_timer += 1
                self.second_click = True

                points.append(Vector(self.first_loc))
                points.append(Vector(self.last_loc))

                self.curve_name = makeMuscle(points).name
                print(self.curve_name)

                objectMode()
                setSelectActiveObject(context, obj)

                self.first_click = False

            return {'RUNNING_MODAL'}

        elif event.type == "WHEELUPMOUSE" or event.type == "UP_ARROW":

            delta = abs((Vector(self.first_loc) -
                         Vector(self.last_loc)).length)/100
            crv = [o for o in bpy.data.objects if o.name == self.curve_name]
            data = crv[0].data

            data.splines[0].bezier_points[1].radius += delta

        elif event.type == "WHEELDOWNMOUSE" or event.type == "DOWN_ARROW":

            delta = abs((Vector(self.first_loc) -
                         Vector(self.last_loc)).length)/100
            crv = [o for o in bpy.data.objects if o.name == self.curve_name]
            data = crv[0].data

            data.splines[0].bezier_points[1].radius -= delta

        elif event.type == "LEFT_ARROW":
            delta = abs((Vector(self.first_loc) -
                         Vector(self.last_loc)).length)/400
            crv = [o for o in bpy.data.objects if o.name == self.curve_name]
            data = crv[0].data

            data.offset -= delta

        elif event.type == "RIGHT_ARROW":
            delta = abs((Vector(self.first_loc) -
                         Vector(self.last_loc)).length)/400
            crv = [o for o in bpy.data.objects if o.name == self.curve_name]
            data = crv[0].data

            data.offset += delta

        if event.type == "R" and event.value == "PRESS":

            self.first_mouse_x = event.mouse_x

            if not self.flag_radius:
                self.flag_radius = True
            else:
                self.flag_radius = False

        if event.type == "MOUSEMOVE":

            if self.d:

                delta = (self.first_mouse_x - event.mouse_x)/1000
                data = returnCurveData(self)

                data.offset += delta

            if self.flag_radius:

                crv = [o for o in bpy.data.objects if o.name == self.curve_name]

                if len(crv) > 0:
                    data = crv[0].data

                    radius = data.splines[0].bezier_points[1].radius

                    delta = (self.first_mouse_x - event.mouse_x)/1000+radius

                    crv = [o for o in bpy.data.objects if o.name ==
                           self.curve_name]
                    data = crv[0].data

                    data.splines[0].bezier_points[1].radius = delta

        if event.type == "D":
            self.first_mouse_x = event.mouse_x
            self.d = event.value == "PRESS"

            if not self.d:

                self.first_mouse_x = event.mouse_x

                crv = [o for o in bpy.data.objects if o.name == self.curve_name]
                if len(crv) > 0:
                    data = crv[0].data

                    self.depth_initial = data.offset

        if self.click_timer > 1 and event.type == "RET":

            self.first_click = False
            self.second_click = False
            self.click_timer = 0

            print("DONE")

            return {'RUNNING_MODAL'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:

            context.object.location.x = self.first_value
            print("CANCELED")
            print(self.click_timer, " - ", Vector(self.first_loc),
                  " <[(@)]> ", Vector(self.last_loc))

            context.area.header_text_set(None)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

            return {'CANCELLED'}

        crv = [o for o in bpy.data.objects if o.name == self.curve_name]
        if len(crv) > 0:
            data = crv[0].data
            segments = data.bevel_resolution

            radius = data.splines[0].bezier_points[1].radius

            depth = data.offset

            context.area.header_text_set(
                "Radius: (" + ("%.3f" % radius) + "), Depth (" + ("%.3f" % depth) +
                "), RMB/Exit: confirm - [D] Left/Right:Depth - [R] Up/Down:Radius"

            )

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_pipe_options, args, 'WINDOW', 'POST_PIXEL')

        self.lmb = False
        self.d = False

        if context.object:
            self.first_mouse_x = event.mouse_x
            self.first_value = context.object.location.x

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}


def register():
    defineObjectProps()
    bpy.utils.register_class(OBJECT_OT_KasMas)
    bpy.utils.register_class(OBJECT_PT_KASMAS)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_KasMas)
    bpy.utils.unregister_class(OBJECT_PT_KASMAS)


if __name__ == "__main__":
    register()

    bpy.ops.object.modal_component('INVOKE_DEFAULT')
