#!/usr/bin/env python3
# Image-to-video / first-last-frame video via a WAN profile on a local ComfyUI instance.
import argparse
import json
import os

import comfy
import forge_config
import model_registry


def list_models():
    for name in model_registry.available():
        profile = model_registry.load_profile(name)
        if model_registry.modality_of(profile) != "video":
            continue
        default = profile.get("default_quant")
        quants = ", ".join((q + " (default)" if q == default else q) for q in model_registry.quants_of(profile))
        print(f"{name}  [{profile['family']}]  quants: {quants or 'single'}")


def main():
    ap = argparse.ArgumentParser(description="Generate video via a WAN profile + ComfyUI.")
    ap.add_argument("--prompt", help="positive prompt describing the motion/scene")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--start-image", help="host path to the first frame")
    ap.add_argument("--end-image", default=None, help="host path to the last frame (enables first-last-frame)")
    ap.add_argument("--model", default=None, help="video profile from models/ (default: FORGE_VIDEO_MODEL)")
    ap.add_argument("--quant", default=None, help="quantization name (default: FORGE_QUANT or the profile default)")
    ap.add_argument("--width", type=int, default=None)
    ap.add_argument("--height", type=int, default=None)
    ap.add_argument("--length", type=int, default=None, help="frame count (default: profile)")
    ap.add_argument("--fps", type=int, default=None)
    ap.add_argument("--negative", default=None, help="override the profile's negative prompt")
    ap.add_argument("--prefix", default="forge/video")
    ap.add_argument("--list-models", action="store_true", help="list available video models + quants and exit")
    ap.add_argument("--print-graph", action="store_true", help="build and print the graph JSON; do not run ComfyUI")
    ap.add_argument("--no-wait", action="store_true")
    ap.add_argument("--timeout", type=int, default=3600)
    args = ap.parse_args()

    if args.list_models:
        list_models()
        return
    if args.prompt is None or args.seed is None or args.start_image is None:
        ap.error("--prompt, --seed and --start-image are required")

    cfg = forge_config.load()
    profile = model_registry.load_profile(args.model or cfg["FORGE_VIDEO_MODEL"])
    mod = model_registry.modality_of(profile)
    if mod != "video":
        raise SystemExit(f"'{args.model}' is a {mod} model — use gen_{mod}.py")
    quant = args.quant or cfg["FORGE_QUANT"] or None

    comfyui = comfy.Comfy(cfg)
    overrides = {"width": args.width, "height": args.height, "length": args.length,
                 "fps": args.fps, "negative": args.negative}
    # LoadImage reads from ComfyUI's input dir, so upload the frames there first.
    for key, path in (("start_image", args.start_image), ("end_image", args.end_image)):
        if path:
            name = os.path.basename(path)
            if not args.print_graph:
                comfyui.container.copy_in(path, f"{cfg['FORGE_COMFY_INPUT']}/{name}")
            overrides[key] = name

    graph = model_registry.build(profile, args.prompt, args.seed, args.prefix, overrides, quant=quant)

    if args.print_graph:
        print(json.dumps(graph, indent=2))
        return

    prompt_id = comfyui.api.submit(graph)
    print(f"prompt_id={prompt_id}", flush=True)
    if args.no_wait:
        return

    files, elapsed = comfyui.api.wait(prompt_id, timeout=args.timeout)
    print(f"elapsed={elapsed:.1f}s")
    out_dir = cfg["FORGE_OUTPUT_DIR"] or comfyui.container.host_path_for(cfg["FORGE_COMFY_OUTPUT"]) or ""
    for rel in files:
        print("output:", f"{out_dir}/{rel}" if out_dir else rel)


if __name__ == "__main__":
    main()
