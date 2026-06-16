# Builds the Z-Image (Turbo) ComfyUI graph (official template).
# Z-Image uses a Lumina2-type Qwen3 text encoder, an AuraFlow model-sampling shift, and a
# res_multistep KSampler at cfg 1 over an SD3-style latent; the negative is a zeroed positive.
import graph_util


def build(prompt, seed, prefix, params):
    return {
        "1": graph_util.unet_loader(params["unet"]),
        "2": {"class_type": "ModelSamplingAuraFlow", "inputs": {
            "model": ["1", 0], "shift": params.get("shift", 3.0)}},
        "3": {"class_type": "CLIPLoader", "inputs": {
            "clip_name": params["clip"], "type": params.get("clip_type", "lumina2"), "device": "default"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": params["vae"]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["3", 0]}},
        "6": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["5", 0]}},
        "7": {"class_type": "EmptySD3LatentImage", "inputs": {
            "width": params["width"], "height": params["height"], "batch_size": 1}},
        "8": {"class_type": "KSampler", "inputs": {
            "model": ["2", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["7", 0],
            "seed": seed, "steps": params["steps"], "cfg": params.get("cfg", 1.0),
            "sampler_name": params.get("sampler", "res_multistep"),
            "scheduler": params.get("scheduler", "simple"), "denoise": 1.0}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["4", 0]}},
        "10": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["9", 0]}},
    }
