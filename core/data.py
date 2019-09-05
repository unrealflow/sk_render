import bpy
import ctypes
def ToCList(src,len):
    dst=(ctypes.c_float*len)()
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
        self.baseColor=ToCList([0.8,0.8,0.8,1.0],4)
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
        self.Position=ToCList([0.0,0.0,0.0],3)
        self.Rotation=ToCList([0.0,0.0,0.0],3)
        self.Scale=ToCList([1.0,1.0,1.0],3)
    def __str__(self):
        return C3ToStr(self.Position)+C3ToStr(self.Rotation)+C3ToStr(self.Scale)

class Mesh(ctypes.Structure): 
   
    def __init__(self):
        self.Vertices=[]
        self.Indices=[]
        self.Trans=Transform()
        self.Mat=Material()

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
                _mesh.Trans.Position=ToCList(o.location,3)
                _mesh.Trans.Rotation=ToCList(o.rotation_euler,3)
                _mesh.Trans.Scale=ToCList(o.scale,3)
                _tmp_mat_= o.data.materials[0].node_tree.nodes["Principled BSDF"]
                _mesh.Mat.baseColor=ToCList(_tmp_mat_.inputs[0].default_value,4)
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

