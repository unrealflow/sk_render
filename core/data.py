import bpy
import ctypes
import os
from math import *
def ToCList_Float(src,len):
    dst=(ctypes.c_float*len)()
    for i in range(0,len):
        dst[i]=src[i]
    return dst

def ToCList_Int(src,len):
    dst=(ctypes.c_uint32*len)()
    for i in range(0,len):
        dst[i]=src[i]
    return dst
def C2ToStr(src):
    return "[{0:.3f},{1:.3f}]\t".format(src[0],src[1])

def C3ToStr(src):
    return "[{0:.3f},{1:.3f},{2:.3f}]\t".format(src[0],src[1],src[2])

def C4ToStr(src):
    return "[{0:.3f},{1:.3f},{2:.3f},{3:.3f}]\t".format(src[0],src[1],src[2],src[3])

class Material(ctypes.Structure):
    _fields_=[
        ("baseColor",ctypes.c_float*4),
        ("metallic",ctypes.c_float),
        ("roughness",ctypes.c_float),
        ("transmission",ctypes.c_float),
    ]
    def __init__(self):
        self.baseColor=ToCList_Float([0.8,0.8,0.8,1.0],4)
        self.metallic=0.0
        self.roughness=0.5
        self.transmission=0.0
    
    def __str__(self):
        return "[{0:.3f},{1:.3f},{2:.3f},{3:.3f}]\t{4:.3f}\t{5:.3f}\t{6:.3f}".format(self.baseColor[0],self.baseColor[1],self.baseColor[2],self.baseColor[3],self.metallic,self.roughness,self.transmission)

class Transform(ctypes.Structure):
    _fields_=[
        ("Position",ctypes.c_float*3),
        ("Rotation",ctypes.c_float*3),
        ("Scale",ctypes.c_float*3),
    ]
    def __init__(self):
        self.Position=ToCList_Float([0.0,0.0,0.0],3)
        self.Rotation=ToCList_Float([0.0,0.0,0.0],3)
        self.Scale=ToCList_Float([1.0,1.0,1.0],3)
    def __str__(self):
        return C3ToStr(self.Position)+C3ToStr(self.Rotation)+C3ToStr(self.Scale)

class CMesh(ctypes.Structure):
    _fields_=[
        ("V",ctypes.POINTER(ctypes.c_float)),
        ("Vc",ctypes.c_uint32),
        ("I",ctypes.POINTER(ctypes.c_uint32)),
        ("Ic",ctypes.c_uint32),
        ("T",ctypes.POINTER(Transform)),
        ("M",ctypes.POINTER(Material))
    ]
class CLight(ctypes.Structure):
     _fields_=[
        ("type",ctypes.c_float),
        ("pos",ctypes.c_float*3),
        ("dir",ctypes.c_float*3),
        ("color",ctypes.c_float*3),
        ("radius",ctypes.c_float),
        ("atten",ctypes.c_float)
    ]

class CScene(ctypes.Structure):
    _fields_=[
        ("meshes",ctypes.POINTER(CMesh)),
        ("nums",ctypes.c_uint32),
        ("lights",ctypes.POINTER(CLight)),
        ("lightCount",ctypes.c_uint32)
    ]

class Mesh(ctypes.Structure): 

    def __init__(self):
        self.Vertices=[]
        self.Indices=[]
        self.Trans=Transform()
        self.Mat=Material()
    
    def ToCMesh(self):
        _Cmesh=CMesh()
        v_len=len(self.Vertices)
        i_len=len(self.Indices)
        _Cmesh.V=ToCList_Float(self.Vertices,v_len)
        _Cmesh.Vc=v_len
        _Cmesh.I=ToCList_Int(self.Indices,i_len)
        _Cmesh.Ic=i_len
        _Cmesh.T=ctypes.pointer(self.Trans)
        _Cmesh.M=ctypes.pointer(self.Mat)
        return _Cmesh



class Loader(object):
    def test(self):
        print("test")
    
    def load(self,context):
        self.meshes=[]
        self.lights=[]
        for o in bpy.data.objects:
            if(o.type=='MESH'):
                # for v in o.data.vertices:
                i=0
                _mesh=Mesh()
                _mesh.Trans.Position=ToCList_Float(o.location,3)
                _mesh.Trans.Rotation=ToCList_Float(o.rotation_euler,3)
                _mesh.Trans.Scale=ToCList_Float(o.scale,3)
                _tmp_mat_= o.data.materials[0].node_tree.nodes["Principled BSDF"]
                _mesh.Mat.baseColor=ToCList_Float(_tmp_mat_.inputs[0].default_value,4)
                _mesh.Mat.metallic=_tmp_mat_.inputs[4].default_value
                _mesh.Mat.roughness=_tmp_mat_.inputs[7].default_value
                _mesh.Mat.transmission=_tmp_mat_.inputs[15].default_value
                print("py:"+_mesh.Mat.transmission.__str__())
                if(len(o.data.uv_layers["UVMap"].data)==0):
                    print(o.name+" no UV ")
                    break

                for p in o.data.polygons: 
                    if(len(p.vertices)==4):
                        _mesh.Indices+=[i,i+1,i+2]
                        _mesh.Indices+=[i,i+2,i+3]
                    else:
                        _mesh.Indices+=[i,i+1,i+2]
                    if(p.use_smooth):
                        for index in p.vertices:
                            _mesh.Vertices+=list(o.data.vertices[index].co)
                            _mesh.Vertices+=list(o.data.vertices[index].normal)
                            _mesh.Vertices+=list(o.data.uv_layers["UVMap"].data[i].uv)
                            i+=1
                    else:
                        for index in p.vertices:
                            _mesh.Vertices+=list(o.data.vertices[index].co)
                            _mesh.Vertices+=list(p.normal)
                            _mesh.Vertices+=list(o.data.uv_layers["UVMap"].data[i].uv)
                            i+=1
                self.meshes.append(_mesh)
                print("\n")
            if(o.type=='LIGHT'):
                _light=CLight()
                _light.pos=ToCList_Float(o.location,3)
                _light.color=ToCList_Float(o.data.color*o.data.energy,3)
                if(o.data.type=='POINT'):
                    _light.type=0.0
                    _light.radius=o.data.shadow_soft_size
                    _light.atten=2.0
                elif(o.data.type=='SUN'):
                    _rot=o.rotation_euler
                    _light.type=1.0
                    # (0,0,-1)
                    x0=0.0
                    y0=-1.0*sin(_rot.x)
                    z0=-1.0*cos(_rot.x)

                    x1=x0*cos(_rot.y)+z0*sin(_rot.y)
                    y1=y0
                    z1=z0*cos(_rot.y)-x0*sin(_rot.y)

                    _light.dir[0]=x1*cos(_rot.z)-y1*sin(_rot.z)
                    _light.dir[1]=y1*cos(_rot.z)+x1*sin(_rot.z)
                    _light.dir[2]=z1
                    
                else:
                    _light.type=2.0
                self.lights.append(_light)

    def render(self):
        print(os.getcwd())
        ll = ctypes.cdll.LoadLibrary   

        _c_scene_=CScene()

        _len=len(self.meshes)
        _c_scene_.meshes=(CMesh*_len)()
        _c_scene_.nums=_len
        for i in range(0,_len):
            _c_scene_.meshes[i]=self.meshes[i].ToCMesh()

        _len=len(self.lights)
        print("---------"+_len.__str__())
        _c_scene_.lights=(CLight*_len)()
        _c_scene_.lightCount=_len
        for i in range(0,_len):
            _c_scene_.lights[i]=self.lights[i]

        lib=ll("E:\\ProgramData\\LearnVulkan\\bin\\SkEngine.dll")
        fun=lib.render
        fun(ctypes.byref(_c_scene_))
        print("Render Finished")         
                