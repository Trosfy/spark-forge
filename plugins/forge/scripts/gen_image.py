#!/usr/bin/env python3
# Text-to-image via a model profile (default flux2-dev) on a local ComfyUI instance.
import argparse

import comfy
import forge_config
import model_registry


def main():
    ap = argparse.ArgumentParser(description="Generate an image via a model profile + ComfyUI.")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--model", default=None, help="profile name from models/ (default: FORGE_MODEL)")
    ap.add_argument("--width", type=int, default=None, help="override the profile default")
    ap.add_argument("--height", type=int, default=None)
    ap.add_argument("--steps", type=int, default=None)
    ap.add_argument("--guidance", type=float, default=None)
    ap.add_argument("--lora", default=None, help="lora filename in ComfyUI's loras dir")
    ap.add_argument("--prefix", default="forge/image")
    ap.add_argument("--no-wait", action="store_true")
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()

    cfg = forge_config.load()
    profile = model_registry.load_profile(args.model or cfg["FORGE_MODEL"])
    overrides = {
        "width": args.width, "height": args.height,
        "steps": args.steps, "guidance": args.guidance, "lora": args.lora,
    }
    graph = model_registry.build(profile, args.prompt, args.seed, args.prefix, overrides)

    comfyui = comfy.Comfy(cfg)
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
