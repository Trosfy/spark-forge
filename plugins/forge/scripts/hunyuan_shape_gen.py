#!/usr/bin/env python3
# Hunyuan3D-2.1 shape-only image-to-3D: pure-PyTorch DiT flow-matching pipeline
# (no texture/PBR, no custom CUDA rasterizer). Exports an untextured GLB.
# Runs inside the ComfyUI container, e.g.:
#   python hunyuan_shape_gen.py --image /opt/ComfyUI/input/subject.png \
#       --out /opt/ComfyUI/output/forge/subject.glb --steps 50 --seed 1234
import argparse
import os
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="tencent/Hunyuan3D-2.1")
    ap.add_argument("--steps", type=int, default=50)
    ap.add_argument("--guidance", type=float, default=5.0)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--octree", type=int, default=256,
                    help="marching-cubes octree resolution (higher = denser)")
    ap.add_argument("--repo", default="/root/work/Hunyuan3D-2.1")
    ap.add_argument("--device", default="cuda", help="cuda or cpu")
    ap.add_argument("--dtype", default="float16", choices=["float16", "float32"])
    args = ap.parse_args()

    sys.path.insert(0, os.path.join(args.repo, "hy3dshape"))

    import torch
    from PIL import Image

    dtype = torch.float16 if args.dtype == "float16" else torch.float32
    print(f"[env] torch={torch.__version__} cuda={torch.cuda.is_available()} "
          f"target_device={args.device} dtype={args.dtype}", flush=True)

    from hy3dshape.pipelines import Hunyuan3DDiTFlowMatchingPipeline
    from hy3dshape.rembg import BackgroundRemover

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    img = Image.open(args.image)
    print(f"[input] {args.image} {img.size} {img.mode}", flush=True)
    if img.mode == "RGB":
        print("[rembg] removing background -> RGBA", flush=True)
        img = BackgroundRemover()(img)
        seg_path = os.path.splitext(args.out)[0] + "_input_rgba.png"
        img.save(seg_path)
        print(f"[rembg] saved segmented input -> {seg_path}", flush=True)

    print(f"[load] {args.model} on {args.device}", flush=True)
    pipe = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
        args.model, device=args.device, dtype=dtype)

    gen = torch.manual_seed(args.seed)
    print(f"[gen] steps={args.steps} guidance={args.guidance} octree={args.octree} "
          f"seed={args.seed}", flush=True)
    start = time.time()
    kwargs = dict(image=img, num_inference_steps=args.steps,
                  guidance_scale=args.guidance, generator=gen)
    try:
        kwargs["octree_resolution"] = args.octree
        mesh = pipe(**kwargs)[0]
    except TypeError as exc:
        print(f"[gen] retry without octree_resolution ({exc})", flush=True)
        kwargs.pop("octree_resolution", None)
        mesh = pipe(**kwargs)[0]
    elapsed = time.time() - start

    try:
        print(f"[mesh] vertices={len(mesh.vertices)} faces={len(mesh.faces)}", flush=True)
    except Exception as exc:
        print(f"[mesh] stats unavailable: {exc}", flush=True)

    mesh.export(args.out)
    print(f"[export] wrote {args.out} ({os.path.getsize(args.out) / 1e6:.2f} MB)", flush=True)
    print(f"[TIMING] generation_seconds={elapsed:.1f}", flush=True)


if __name__ == "__main__":
    main()
