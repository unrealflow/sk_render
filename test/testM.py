import sk_render as sk
_l=sk.core.data.Loader()
_l.load(0)
for m in _l.scene:
    print("\t-\t-\t-\t-\t-\t-\t-")
    print(m.Trans)
    print(m.Mat)
    print(len(m.Vertices).__str__()+"\t"+len(m.Indices).__str__())
    print((m.Indices))