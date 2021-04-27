#EXECUTE

bl_info = {
    "name" : "KasMas",
    "author" : "Kursad Karatas",
    "description" : "componenets",
    "blender" : (2, 80, 0),
    "version": (0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}



import bpy, bmesh
import blf
from bpy.props import IntProperty, FloatProperty, BoolProperty,FloatVectorProperty, StringProperty
from mathutils import Vector,Matrix

from bpy_extras import view3d_utils



print("TEST")


def defineObjectProps():

    try:
        bool(bpy.types.Object.ezlattice_flag)

    except:
        bpy.types.Object.kasmas_isprofile = BoolProperty(name="IsMuscleProfile", default=False, update=update_kasmasfunc)
        bpy.types.Object.kasmas_profile = StringProperty(name="MuscleProfile", default="")



def update_kasmasfunc(self, context):
    
    if context.object.kasmas_isprofile:
        cr=context.object
        cr_name=cr.name
        profile_name=".profilemuscle"+"_"+cr_name
        
        scale=cr.data.bevel_depth
        
        c=[o for o in context.scene.objects if o.type=="CURVE" and o.name==profile_name]
        print(c)
        if len(c)<1:
            bpy.ops.curve.primitive_bezier_circle_add(enter_editmode=False, location=(0, 0, 0))
            profile=context.object
            profile.name=profile_name
            profile.scale=Vector((scale,scale,scale))
#             profile.parent=cr
#             cr.kasmas_profile=""
        
        else:
            profile=[o for o in context.scene.objects if o.type=="CURVE" and o.name==profile_name][0]
        
        cr=[o for o in context.scene.objects if o.type=="CURVE" and o.name==cr_name]
        
        if len(cr)>0:
        
            setSelectActiveObject(context, cr[0])
#             context.object.data.bevel_object = bpy.data.objects[".profilemuscle"]
            context.object.data.bevel_object = profile
            context.object.data.use_fill_caps = True

            context.object.kasmas_profile=profile_name
            
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
    
    # get the context arguments
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    coord = event.mouse_region_x, event.mouse_region_y

#     obj=context.object
    obj=obj
    matrix=obj.matrix_world
    
    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

    ray_target = ray_origin + view_vector

    def visible_objects_and_duplis():
        """Loop over (object, matrix) pairs (mesh only)"""

        depsgraph = context.evaluated_depsgraph_get()
        for dup in depsgraph.object_instances:
            if dup.is_instance:  # Real dupli instance
                obj = dup.instance_object
                yield (obj, dup.matrix_world.copy())
            else:  # Usual object
                obj = dup.object
                yield (obj, obj.matrix_world.copy())

    def obj_ray_cast(obj, matrix):
        """Wrapper for ray casting that moves the ray into object space"""

        # get the ray relative to the object
        matrix_inv = matrix.inverted()
        ray_origin_obj = matrix_inv @ ray_origin
        ray_target_obj = matrix_inv @ ray_target
        ray_direction_obj = ray_target_obj - ray_origin_obj

        # cast the ray
        success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)

        if success:
            return location, normal, face_index
        else:
            return None, None, None

    # cast rays and find the closest object
    best_length_squared = -1.0
    best_obj = None

    #for obj, matrix in visible_objects_and_duplis():
    #    if obj.type == 'MESH':
    hit, normal, face_index = obj_ray_cast(obj, matrix)
    if hit is not None:
        hit_world = matrix @ hit
        scene.cursor.location = hit_world
        length_squared = (hit_world - ray_origin).length_squared
        if best_obj is None or length_squared < best_length_squared:
            best_length_squared = length_squared
            best_obj = obj

    # now we have the object under the mouse cursor,
    # we could do lots of stuff but for the example just select.
    if best_obj is not None:
        # for selection etc. we need the original object,
        # evaluated objects are not in viewlayer
        best_original = best_obj.original
        best_original.select_set(True)
        context.view_layer.objects.active = best_original
        


def getCurvePointLocation(crv,i):
    data=crv.data
    

    #data.splines[0].points[0].co=c1
    loc=data.splines[0].bezier_points[i].co.copy()
        
    return loc

def makeProfileCurve(loc=Vector((1,1,0)) ) :

    bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=True, 
                                            location=loc)

    curve=bpy.context.object
    curve.name=".curveprofile"
    
    
    bpy.ops.curve.normals_make_consistent()
    bpy.ops.curve.subdivide()
    data=curve.data
    
    i0= getCurvePointLocation(curve,0)
    i1= getCurvePointLocation(curve,1)
    i2= getCurvePointLocation(curve,2)
    
    #data.splines[0].points[0].co=c1
    data.splines[0].bezier_points[0].co=i0+Vector((0,0.1/2,0))
    data.splines[0].bezier_points[1].co=Vector((0,1,0))
    data.splines[0].bezier_points[2].co=i2+Vector((0,0.1/2,0))
    
    #data.splines[0].bezier_points[1].co=Vector((0,1,0))
    #data.splines[0].points[1].co=(c2+c1)/2


def setCurvePoint(co=[]):
    
    cr=bpy.data.objects["BezierCurve"]
    cr.location=Vector((0,0,0))
    #data=bpy.data.objects["BezierCurve"].data
    
    #p1=data.splines[0].bezier_points[0].co.copy()
    #p2=data.splines[0].bezier_points[1].co.copy()
    c1=Vector((co[0].x,co[0].y,co[0].z))
    c2=Vector((co[1].x,co[1].y,co[1].z  ))
        
    #data.splines[0].points[0].co=c1
    #data.splines[0].points[2].co=c2
    #data.splines[0].points[1].co=(c2+c1)/2
    
    data.splines[0].bezier_points[0].co=c1
    data.splines[0].bezier_points[2].co=c2
    data.splines[0].bezier_points[1].co=(c2+c1)/2


def makeMuscle(co=[]):
    ob=bpy.context.object
    
    bpy.ops.object.select_all(action='DESELECT')

    bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=True)
    cr=bpy.context.object
    bpy.ops.curve.handle_type_set(type='VECTOR')
    

    bpy.ops.curve.subdivide()
    bpy.ops.curve.handle_type_set(type='AUTOMATIC')


    #cr=bpy.data.objects["BezierCurve"]
    cr.location=Vector((0,0,0))
    data=bpy.data.objects["BezierCurve"].data
    data=cr.data
    
    #p1=data.splines[0].bezier_points[0].co.copy()
    #p2=data.splines[0].bezier_points[1].co.copy()
    c1=Vector((co[0].x,co[0].y,co[0].z))
    c2=Vector((co[1].x,co[1].y,co[1].z  ))
        
    #data.splines[0].points[0].co=c1
    #data.splines[0].points[2].co=c2
    #data.splines[0].points[1].co=(c2+c1)/2
    
    data.splines[0].bezier_points[0].co=c1
    data.splines[0].bezier_points[2].co=c2
    data.splines[0].bezier_points[1].co=(c2+c1)/2

    #Curve Depth
    cr.data.bevel_depth = 0.1

    #Thickness
    data.splines[0].bezier_points[1].radius=(c2-c1).length
    data.splines[0].bezier_points[0].radius=(c2-c1).length/3
    data.splines[0].bezier_points[2].radius=(c2-c1).length/3

    #Texture
    cr.data.use_uv_as_generated = True
    cr.data.materials.append(bpy.data.materials['MUSCLE_A'])
    
    cr.data.splines[0].tilt_interpolation = 'EASE'
    cr.data.splines[0].radius_interpolation = 'EASE'


    bpy.ops.object.modifier_add(type='SHRINKWRAP')
#     bpy.ops.object.modifier_add(type='SHRINKWRAP')
    bpy.context.object.modifiers["Shrinkwrap"].target = bpy.data.objects[ob.name]
    bpy.context.object.modifiers["Shrinkwrap"].use_apply_on_spline = True

    
    bpy.ops.object.modifier_add(type='MIRROR')
    #bpy.context.object.modifiers["Mirror"].mirror_object = bpy.data.objects["HEAD"]
    bpy.context.object.modifiers["Mirror"].mirror_object = bpy.data.objects[ob.name]


    return cr

def getVertSel():

    obj=bpy.context.edit_object
    obj.update_from_editmode()

    m=obj.matrix_world
    me = obj.data

    #get bmesh (Object needs to be in Edit mode)
    bm=bmesh.from_edit_mesh(me)
    #bm=bmesh.geometry(me)


    #print active vert:

    mode=bm.select_mode

    #     act=bm.select_history.active
    print(mode)

    co=Vector((0.0, 0.0, 0.0))
    vv=[]
    if bm.select_mode=={'VERT'}:
        #co=bm.select_history.active.co.copy()
        for v in bm.select_history:
            co=m@v.co
        #print("VERT MODE >>>", co)
            vv.append(co)
    
    return vv

 
# if not bool([o for o in bpy.context.scene.objects if ".curveprofile"==o.name]):
#     makeProfileCurve()   
#     


#CODE REFACTOR
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
#         if context.scene.quick_pipe_fill_caps is True:
#             blf.draw(font_id, "ON")
#         else:
#             blf.draw(font_id, "OFF")



def returnCurveData(self):
    
    crv=[o for o in bpy.data.objects if o.name==self.curve_name]
    if len(crv)>0:
        return crv[0].data
    
    else:
        return None



class OBJECT_PT_KASMAS(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "KasMas Tools"
    bl_idname = "KasMas_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene


        crv=[o for o in context.scene.objects if o.type=="CURVE" and o.select_get()]
        #data=crv[0].data
        
        if len(crv)>0:
            cr=crv[0]
            crv=crv[0].data
            #print(crv)
            
            p0=crv.splines[0].bezier_points[0]
            p1=crv.splines[0].bezier_points[1]
            p2=crv.splines[0].bezier_points[2]
            

            # Create a simple row.
            layout.label(text=" Muscle Props")
            
            row = layout.row()
            row.prop(cr, "kasmas_isprofile", text="use profile")
            
            if cr.kasmas_isprofile:
                prf=[o for o in context.scene.objects if o.name==cr.kasmas_profile]
#                 print(prf, "  ", cr.kasmas_profile )
                if len(prf)>0:
                    
                    row = layout.row()
                    row.prop(prf[0], "scale", text="Profile")
                    
 
            row = layout.row()
            row.prop(crv, "offset", text="depth")
            
            row = layout.row()
            row.prop(crv, "extrude", text="flatness")
            
            row = layout.row()
            row.prop(crv, "bevel_depth", text="thickness")

            #row.prop(scene, "frame_end")
        
            # Create an row where the buttons are aligned to each other.
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



            # Create two columns, by using a split layout.
            split = layout.split()

            # First column
            #col = split.column()
            #col.label(text="Column One:")
            #col.prop(scene, "frame_end")
            #col.prop(scene, "frame_start")

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
    
    first_loc:FloatVectorProperty(name="FirstLocation", description="", default=(0.0, 0.0, 0.0) )
    mid_loc:FloatVectorProperty(name="FirstLocation", description="", default=(0.0, 0.0, 0.0) )
    last_loc:FloatVectorProperty(name="FirstLocation", description="", default=(0.0, 0.0, 0.0) )

    curve_name:StringProperty()
   
    flag_depth:BoolProperty(default=False)
    flag_radius:BoolProperty(default=False)
    
    
    
    depth_initial:FloatProperty(name="DepthInitial", description="", default=0.0 )
    
    def resetFlags(self):
        
        self.flag_depth=False
        self.flag_radius=False
        
    
    def modal(self, context, event):
        # if event.type == 'MOUSEMOVE':
        #     delta = self.first_mouse_x - event.mouse_x
        #     context.object.location.x = self.first_value + delta * 0.01

        scene = context.scene
        region = context.region
        rv3d = context.region_data
        coord = event.mouse_region_x, event.mouse_region_y

        # get the ray from the viewport and mouse
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        ray_target = ray_origin + (view_vector * 1000)
        ray_target.normalized() 

        obj=context.object
        m=obj.matrix_world
        
        points=[]
        
#         if event.type in {
#                 'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE',
#                 'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4', 'NUMPAD_6',
#                 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9', 'NUMPAD_5','TAB'}:

        
#         if event.type in {
#                 'MIDDLEMOUSE',
#                 'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4', 'NUMPAD_6',
#                 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9', 'NUMPAD_5','TAB'}:
# 
# 
#             print("PASS")
# 
#             return {'PASS_THROUGH'}

        
#         try:
#             value_offset
#         except NameError:
#             print("value_offset does not exists")
#             value_offset=0
#         else:
#             print("Try value_offset > {}".format(value_offset))    
       
     
        if event.type == 'MIDDLEMOUSE':
#             bpy.ops.view3d.rotate()
            return {'PASS_THROUGH'}
  
        if event.type == 'MIDDLEMOUSE' and event.value == "PRESS":
#             bpy.ops.view3d.move()
            return {'PASS_THROUGH'}


        if event.type == 'LEFTMOUSE':
            
            
#             if self.click_timer>0:
                
            self.resetFlags()
            
            self.first_click=True
                
            
            
            if context.object.mode=='EDIT':
                
#                 bpy.context.view_layer.update()
#                 obj.update_from_editmode()
                ##bpy.ops.view3d.select('INVOKE_DEFAULT', extend=False, deselect=False, enumerate=False, toggle=False)


                vv=[v for v in obj.data.vertices if v.select]
#                 print(vv)
                loc=Vector((0,0,0))
                if len(vv)==1:
                    bpy.context.scene.cursor.location=m@vv[-1].co
                if len(vv)>1:
                    for v in vv:
                        loc+=m@v.co

                    bpy.context.scene.cursor.location=loc/len(vv)
                    
                bpy.context.view_layer.update()
                obj.update_from_editmode()

            if self.first_click and self.click_timer==0  and event.value == "RELEASE":
                print("First Click")
#                 self.first_click=True
                
                self.click_timer+=1
                ##objectMode()
                ##bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
                ##start=context.object
                
                ##start.name="first"
                
                ##active=context.object
                ##active.location=bpy.context.scene.cursor.location
                ##print(active.location)
                ##setSelectActiveObject(context, obj)
                
                ##editMode()
                
                
                self.first_click=False
#                 self.click_timer=0

                relocateCursor(context, event, obj)
                
                self.first_loc=context.scene.cursor.location.copy()    
#             bpy.ops.view3d.snap_cursor_to_selected()

            if self.first_click and self.click_timer>0 and event.value=="RELEASE":
                
                print("Second Click")
                relocateCursor(context, event, obj)
                self.last_loc=context.scene.cursor.location.copy()    

                self.click_timer+=1
                self.second_click=True
                
#                 co=getVertSel()
                points.append(Vector(self.first_loc))
                points.append(Vector(self.last_loc))
                #setCurvePoint(co)
                self.curve_name=makeMuscle(points).name
                print(self.curve_name)
                
                objectMode()
                setSelectActiveObject(context, obj)

                self.first_click=False
            
            
                    
                
#             return {'PASS_THROUGH'}

            return {'RUNNING_MODAL'}
        
#         if event.type == 'MOUSEMOVE':
#             delta = self.first_mouse_x - event.mouse_x
# #                 delta = self.last_loc - event.mouse_x
#             
# #             if self.first_click and self.click_timer>1 and self.second_click and event.value=="WHEELUPMOUSE" and  event.type == 'SHIFT':
        
        elif event.type == "WHEELUPMOUSE" or event.type=="UP_ARROW":
#                 delta = self.first_mouse_x - event.mouse_x
#             delta=0.1
#             delta = abs(self.first_mouse_x - event.mouse_x)
            delta=abs(( Vector(self.first_loc) - Vector(self.last_loc) ).length)/100
            crv=[o for o in bpy.data.objects if o.name==self.curve_name]
            data=crv[0].data
# #                     context.object.location.x = self.first_value + delta * 0.01
            data.splines[0].bezier_points[1].radius+=delta
#                 

        elif event.type == "WHEELDOWNMOUSE" or event.type=="DOWN_ARROW":
#                 delta = self.first_mouse_x - event.mouse_x
#             delta=0.1
#             delta = abs(self.first_mouse_x - event.mouse_x)
            delta=abs(( Vector(self.first_loc) - Vector(self.last_loc) ).length)/100
            crv=[o for o in bpy.data.objects if o.name==self.curve_name]
            data=crv[0].data
# #                     context.object.location.x = self.first_value + delta * 0.01
            data.splines[0].bezier_points[1].radius-=delta
#                 
        
        elif event.type=="LEFT_ARROW":
            delta=abs(( Vector(self.first_loc) - Vector(self.last_loc) ).length)/400
            crv=[o for o in bpy.data.objects if o.name==self.curve_name]
            data=crv[0].data
# #                     context.object.location.x = self.first_value + delta * 0.01
            data.offset-=delta
        
        elif event.type=="RIGHT_ARROW":
            delta=abs(( Vector(self.first_loc) - Vector(self.last_loc) ).length)/400
            crv=[o for o in bpy.data.objects if o.name==self.curve_name]
            data=crv[0].data
# #                     context.object.location.x = self.first_value + delta * 0.01
            data.offset+=delta
        
#         if event.type=="D" and event.value=="PRESS":
# #             self.resetFlags()
#             self.first_mouse_x = event.mouse_x
#             if not self.flag_depth:
#                 self.flag_depth=True
#         
#             else:
#                 self.flag_depth=False
        
        if event.type=="R" and event.value=="PRESS":
#             self.resetFlags()
            
            self.first_mouse_x = event.mouse_x
            
            if not self.flag_radius:
                self.flag_radius=True
            else:
                self.flag_radius=False
#         if event.type=="CLICK_DRAG":

        if event.type=="MOUSEMOVE":

#             if self.flag_depth:
            
            
            if self.d:
                
#                 delta=abs(( Vector(self.first_loc) - Vector(self.last_loc) ).length)/200
                delta = (self.first_mouse_x - event.mouse_x)/1000
                data=returnCurveData(self)
               
#                 data.offset-=delta
#                 data.offset=value_offset+delta
#                 if delta>self.depth_initial:
#                     data.offset=self.depth_initial+delta
#                 data.offset=self.depth_initial+self.depth_initial/10
                
#                 if not delta==0.0 and abs(delta)>self.depth_initial:
#                     delta=self.depth_initial/2
#                     print("Depth in Drag {} ".format(self.depth_initial))
                    
#                 data.offset+=self.depth_initial/10
                data.offset+=delta
                
            if self.flag_radius:
                
                crv=[o for o in bpy.data.objects if o.name==self.curve_name]
            
                if len(crv)>0:
                    data=crv[0].data
#                 delta=abs(( Vector(self.first_loc) - Vector(self.last_loc) ).length)/200
                    radius= data.splines[0].bezier_points[1].radius
                    
                    delta = (self.first_mouse_x - event.mouse_x)/1000+radius
                     
                    crv=[o for o in bpy.data.objects if o.name==self.curve_name]
                    data=crv[0].data
    #                 data.offset-=delta
                    data.splines[0].bezier_points[1].radius=delta
                
        
        
        if event.type=="D":
            self.first_mouse_x = event.mouse_x
            self.d=event.value=="PRESS"
            
            if not self.d:
                
                self.first_mouse_x = event.mouse_x
                
                crv=[o for o in bpy.data.objects if o.name==self.curve_name]
                if len(crv)>0:
                    data=crv[0].data
#                     value_offset=data.offset
                    self.depth_initial=data.offset
                    #print("Setting Depth {} ".format(value_offset))
           
    
        if self.click_timer>1 and event.type=="RET":
            
            self.first_click=False
            self.second_click=False
            self.click_timer=0
            
            print("DONE")
        
        
            return {'RUNNING_MODAL'}
        
        

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            
            context.object.location.x = self.first_value
            print("CANCELED")
            print(self.click_timer, " - ",Vector(  self.first_loc)," <[(@)]> ", Vector(self.last_loc))

            context.area.header_text_set(None)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            
            return {'CANCELLED'}


        
#         if event.type == "RET":
#             print("Enter")
#             bpy.ops.object.mode_set(mode="OBJECT")
# #                 return {'CANCELLED'}
#             return {'FINISHED'}


#         return {'PASS_THROUGH'}

        #if context.object.type == 'CURVE':
            #CODE REFACTOR
        crv=[o for o in bpy.data.objects if o.name==self.curve_name]
        if len(crv)>0:
            data=crv[0].data
            segments = data.bevel_resolution
            
            radius =  data.splines[0].bezier_points[1].radius
            
            depth = data.offset
            
            context.area.header_text_set(
                "Radius: (" + ("%.3f" % radius) + "), Depth (" + ("%.3f" % depth)  +
                "), RMB/Exit: confirm - [D] Left/Right:Depth - [R] Up/Down:Radius"
                
            )

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        
        #CODE REFACTOR
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_pipe_options, args, 'WINDOW', 'POST_PIXEL')
        
        
        self.lmb=False
        self.d=False
        
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

    # test call
    bpy.ops.object.modal_component('INVOKE_DEFAULT')
