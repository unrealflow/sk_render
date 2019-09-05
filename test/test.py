import bpy
import ctypes
import os
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
    ]
    def __init__(self):
        self.baseColor=ToCList_Float([0.8,0.8,0.8,1.0],4)
        self.metallic=0.0
        self.roughness=0.5
    
    def __str__(self):
        return "[{0:.3f},{1:.3f},{2:.3f},{3:.3f}]\t{4:.3f}\t{5:.3f}".format(self.baseColor[0],self.baseColor[1],self.baseColor[2],self.baseColor[3],self.metallic,self.roughness)

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
class CScene(ctypes.Structure):
    _fields_=[
        ("meshes",ctypes.POINTER(CMesh)),
        ("nums",ctypes.c_uint32)
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
        self.scene=[]
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

                if(len(o.data.uv_layers["UVMap"].data)==0):
                    print(o.name+" no UV ")
                    break

                for p in o.data.polygons: 
                    if(len(p.vertices)==4):
                        _mesh.Indices+=[i,i+1,i+2]
                        _mesh.Indices+=[i,i+2,i+3]
                    else:
                        _mesh.Indices+=[i,i+1,i+2]
                    for index in p.vertices:
                        _mesh.Vertices+=list(o.data.vertices[index].co)
                        _mesh.Vertices+=list(o.data.vertices[index].normal)
                        _mesh.Vertices+=list(o.data.uv_layers["UVMap"].data[i].uv)
                        i+=1
                self.scene.append(_mesh)
                print("\n")


_l=Loader()
_l.load(0)

# for m in _l.scene:
#     print("\t-\t-\t-\t-\t-\t-\t-")
#     print(m.Trans)
#     print(m.Mat)
#     print(len(m.Vertices).__str__()+"\t"+len(m.Indices).__str__())
#     print((m.Indices))



print(os.getcwd())
ll = ctypes.cdll.LoadLibrary   

_c_scene_=CScene()
_len=len(_l.scene)
print(_len)
_c_scene_.meshes=(CMesh*_len)()
_c_scene_.nums=_len
for i in range(0,_len):
    _c_scene_.meshes[i]=_l.scene[i].ToCMesh()

def Render():
    lib=ll("E:\\ProgramData\\SkRender\\Bin\\SkRender.dll")
    fun=lib.render
    fun(ctypes.byref(_c_scene_))

Render()
print("OK") 