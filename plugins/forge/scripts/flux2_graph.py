# Builds the FLUX.2 ComfyUI node graph (official image_flux2 template).
# FLUX.2 is guidance-distilled: no negative-prompt channel.
# params carries: unet, clip, vae, width, height, steps, guidance, optional lora,
# and optional ref_images (filenames already in ComfyUI's input dir). Each reference
# is VAE-encoded and spliced into the conditioning via ReferenceLatent — FLUX.2's
# native multi-reference mechanism (chain one node per image).
import graph_util


def build(prompt, seed, prefix, params):
    lora = params.get("lora")
    refs = params.get("ref_images") or []
    model_src = ["14", 0] if lora else ["1", 0]
    graph = {
        "1": graph_util.unet_loader(params["unet"]),
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": params["clip"], "type": "flux2", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": params["vae"]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "FluxGuidance", "inputs": {"guidance": params["guidance"], "conditioning": ["4", 0]}},
        "6": {"class_type": "BasicGuider", "inputs": {"model": model_src, "conditioning": ["5", 0]}},
        "7": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "8": {"class_type": "Flux2Scheduler", "inputs": {
            "steps": params["steps"], "width": params["width"], "height": params["height"]}},
        "9": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "10": {"class_type": "EmptyFlux2LatentImage", "inputs": {
            "width": params["width"], "height": params["height"], "batch_size": 1}},
        "11": {"class_type": "SamplerCustomAdvanced", "inputs": {
            "noise": ["9", 0], "guider": ["6", 0], "sampler": ["7", 0],
            "sigmas": ["8", 0], "latent_image": ["10", 0]}},
        "12": {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["12", 0]}},
    }
    if lora:
        graph["14"] = {"class_type": "LoraLoaderModelOnly", "inputs": {
            "lora_name": lora, "strength_model": 1.0, "model": ["1", 0]}}
    # Reference images: LoadImage -> scale -> VAEEncode -> ReferenceLatent, chained so
    # each image appends to the conditioning the guider reads (node "6").
    cond = ["5", 0]
    nid = 20
    for fn in refs:
        load, scale, enc, ref = str(nid), str(nid + 1), str(nid + 2), str(nid + 3)
        graph[load] = {"class_type": "LoadImage", "inputs": {"image": fn}}
        graph[scale] = {"class_type": "FluxKontextImageScale", "inputs": {"image": [load, 0]}}
        graph[enc] = {"class_type": "VAEEncode", "inputs": {"pixels": [scale, 0], "vae": ["3", 0]}}
        graph[ref] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": cond, "latent": [enc, 0]}}
        cond = [ref, 0]
        nid += 4
    if refs:
        graph["6"]["inputs"]["conditioning"] = cond
    return graph
