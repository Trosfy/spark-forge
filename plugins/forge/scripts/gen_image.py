#!/usr/bin/env python3
# Text-to-image via a model profile (default flux2-dev) on a local ComfyUI instance.
import argparse
import json

import comfy
import forge_config
import model_registry


def list_models():
    for name in model_registry.available():
        profile = model_registry.load_profile(name)
        if model_registry.modality_of(profile) != "image":
            continue
        default = profile.get("default_quant")
        quants = ", ".join((q + " (default)" if q == default else q) for q in model_registry.quants_of(profile))
        print(f"{name}  [{profile['family']}]  quants: {quants or 'single'}")


def main():
    ap = argparse.ArgumentParser(description="Generate an image via a model profile + ComfyUI.")
    ap.add_argument("--prompt")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--model", default=None, help="profile name from models/ (default: FORGE_MODEL)")
    ap.add_argument("--quant", default=None, help="quantization name (default: FORGE_QUANT or the profile default)")
    ap.add_argument("--width", type=int, default=None, help="override the profile default")
    ap.add_argument("--height", type=int, default=None)
    ap.add_argument("--steps", type=int, default=None)
    ap.add_argument("--guidance", type=float, default=None)
    ap.add_argument("--lora", default=None, help="lora filename in ComfyUI's loras dir")
    ap.add_argument("--prefix", default="forge/image")
    ap.add_argument("--list-models", action="store_true", help="list available models + quants and exit")
    ap.add_argument("--print-graph", action="store_true", help="build and print the graph JSON; do not run ComfyUI")
    ap.add_argument("--no-wait", action="store_true")
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()

    if args.list_models:
        list_models()
        return
    if args.prompt is None or args.seed is None:
        ap.error("--prompt and --seed are required")

    cfg = forge_config.load()
    profile = model_registry.load_profile(args.model or cfg["FORGE_MODEL"])
    mod = model_registry.modality_of(profile)
    if mod != "image":
        raise SystemExit(f"'{args.model}' is a {mod} model — use gen_{mod}.py")
    quant = args.quant or cfg["FORGE_QUANT"] or None
    overrides = {
        "width": args.width, "height": args.height,
        "steps": args.steps, "guidance": args.guidance, "lora": args.lora,
    }
    graph = model_registry.build(profile, args.prompt, args.seed, args.prefix, overrides, quant=quant)

    if args.print_graph:
        print(json.dumps(graph, indent=2))
        return

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
