# Builds the Qwen-Image (20B MMDiT) ComfyUI graph (official image_qwen_image template).
# Uses the Qwen2.5-VL text encoder via the qwen_image CLIP type and an AuraFlow model-sampling
# shift; cfg > 1 with a (usually empty) negative. prompt = positive text; params carries weights + dims.


def build(prompt, seed, prefix, params):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": params["unet"], "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": params["clip"], "type": "qwen_image", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": params["vae"]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": params.get("negative", ""), "clip": ["2", 0]}},
        "6": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["1", 0], "shift": params.get("shift", 3.1)}},
        "7": {"class_type": "EmptySD3LatentImage", "inputs": {
            "width": params.get("width", 1328), "height": params.get("height", 1328), "batch_size": 1}},
        "8": {"class_type": "KSampler", "inputs": {
            "model": ["6", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["7", 0],
            "seed": seed, "steps": params.get("steps", 20), "cfg": params.get("cfg", 2.5),
            "sampler_name": params.get("sampler", "euler"), "scheduler": params.get("scheduler", "simple"),
            "denoise": 1.0}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["9", 0]}},
    }
