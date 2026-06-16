# Builds the FLUX.2 Klein (distilled 4B) ComfyUI graph.
# Verified against the official image_flux2_klein_text_to_image template. Unlike flux2-dev
# (FluxGuidance + BasicGuider, no negative), the distilled klein uses a CFGGuider at low cfg
# with a zeroed-out negative, a Qwen3 text encoder loaded via the flux2 CLIP type, and a
# 4-step Flux2Scheduler. prompt = positive text; params carries weights + dims.


def build(prompt, seed, prefix, params):
    width, height = params.get("width", 1024), params.get("height", 1024)
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": params["unet"], "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": params["clip"], "type": "flux2", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": params["vae"]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["4", 0]}},
        "6": {"class_type": "CFGGuider", "inputs": {
            "model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "cfg": params.get("guidance", 1.0)}},
        "7": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": params.get("sampler", "euler")}},
        "8": {"class_type": "Flux2Scheduler", "inputs": {"steps": params.get("steps", 4), "width": width, "height": height}},
        "9": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "10": {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "11": {"class_type": "SamplerCustomAdvanced", "inputs": {
            "noise": ["9", 0], "guider": ["6", 0], "sampler": ["7", 0], "sigmas": ["8", 0], "latent_image": ["10", 0]}},
        "12": {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["12", 0]}},
    }
