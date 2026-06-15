#!/usr/bin/env python3
# Image-to-3D (GLB) via Hunyuan3D-2.1 running inside the ComfyUI container.
# Files cross the host/container boundary through ComfyUI's bind-mounted dirs.
import argparse
import os
import shutil
import subprocess
import sys

import comfy
import forge_config

CONTAINER_SCRIPT = "/tmp/forge/hunyuan_shape_gen.py"


def main():
    ap = argparse.ArgumentParser(description="Generate a 3D model (GLB) from an image.")
    ap.add_argument("--image", required=True)
    ap.add_argument("--name", default=None, help="output basename (default: from image)")
    ap.add_argument("--steps", type=int, default=50)
    ap.add_argument("--guidance", type=float, default=5.0)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--octree", type=int, default=256)
    ap.add_argument("--decimate", type=int, default=0, help="target face count; 0 = skip")
    args = ap.parse_args()

    cfg = forge_config.load()
    comfyui = comfy.Comfy(cfg)
    here = os.path.dirname(os.path.abspath(__file__))

    image = os.path.abspath(args.image)
    if not os.path.isfile(image):
        sys.exit(f"image not found: {image}")
    name = args.name or os.path.splitext(os.path.basename(image))[0]

    if not comfyui.container.has(cfg["FORGE_HUNYUAN_REPO"]) or not comfyui.container.has(cfg["FORGE_HY3D_CACHE"]):
        sys.exit(f"Hunyuan3D-2.1 is not provisioned in container '{comfyui.container.name}'. "
                 f"See setup/README.md (Hunyuan3D-2.1).")

    input_dir = cfg["FORGE_INPUT_DIR"] or comfyui.container.host_path_for(cfg["FORGE_COMFY_INPUT"])
    output_dir = cfg["FORGE_OUTPUT_DIR"] or comfyui.container.host_path_for(cfg["FORGE_COMFY_OUTPUT"])
    if not input_dir or not output_dir:
        sys.exit("Could not resolve host input/output dirs. Set FORGE_INPUT_DIR and "
                 "FORGE_OUTPUT_DIR, or run ComfyUI in a container with bind-mounted "
                 "input/output (auto-detected from the container's mounts).")
    staged = os.path.join(input_dir, f"forge_{name}.png")
    shutil.copyfile(image, staged)

    container_in = f"{cfg['FORGE_COMFY_INPUT']}/forge_{name}.png"
    container_out = f"{cfg['FORGE_COMFY_OUTPUT']}/forge/{name}.glb"
    host_out = os.path.join(output_dir, "forge", f"{name}.glb")

    # Vendor our copy of the script in, so generation does not depend on any
    # ad-hoc copy living in the container's ephemeral writable layer.
    comfyui.container.run("mkdir", "-p", "/tmp/forge", check=True)
    comfyui.container.copy_in(os.path.join(here, "hunyuan_shape_gen.py"), CONTAINER_SCRIPT)

    comfyui.container.run(
        "python", CONTAINER_SCRIPT,
        "--image", container_in, "--out", container_out,
        "--repo", cfg["FORGE_HUNYUAN_REPO"],
        "--steps", str(args.steps), "--guidance", str(args.guidance),
        "--seed", str(args.seed), "--octree", str(args.octree),
        check=True,
    )

    if not os.path.isfile(host_out):
        sys.exit(f"expected GLB not found on host: {host_out}")
    print("glb:", host_out)

    if args.decimate > 0:
        low = os.path.join(output_dir, "forge", f"{name}_lp{args.decimate}.glb")
        subprocess.run(["blender", "-b", "--python", os.path.join(here, "decimate.py"),
                        "--", "--glb", host_out, "--out", low, "--faces", str(args.decimate)],
                       check=True)
        print("glb_decimated:", low)


if __name__ == "__main__":
    main()
