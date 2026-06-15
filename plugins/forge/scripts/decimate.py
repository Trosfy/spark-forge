# Decimate a GLB to a target face count and flat-shade it. Runs under Blender:
#   blender -b --python decimate.py -- --glb in.glb --out out.glb --faces 700
import os
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
opts = {}
i = 0
while i < len(argv):
    opts[argv[i].lstrip("-")] = argv[i + 1]
    i += 2
faces = int(opts.get("faces", 700))

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=opts["glb"])
mesh = next(obj for obj in bpy.data.objects if obj.type == "MESH")
bpy.context.view_layer.objects.active = mesh

current = len(mesh.data.polygons)
ratio = max(0.001, min(1.0, faces / max(1, current)))
mod = mesh.modifiers.new("dec", "DECIMATE")
mod.decimate_type = "COLLAPSE"
mod.ratio = ratio
bpy.ops.object.modifier_apply(modifier="dec")
for poly in mesh.data.polygons:
    poly.use_smooth = False

out = opts["out"]
os.makedirs(os.path.dirname(out), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_apply=True)
print(f"DECIMATE_DONE {current}->{len(mesh.data.polygons)} faces -> {out}")
