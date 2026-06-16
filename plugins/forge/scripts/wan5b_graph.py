# Builds the WAN 2.2 5B TI2V (single-model image-to-video) ComfyUI graph.
# Verified against the official video_wan2_2_5B_ti2v template. The 5B is one model (no MoE
# high/low split), uses the high-compression wan2.2 VAE, and conditions on a start image via
# Wan22ImageToVideoLatent. prompt = positive text; params carries the model/clip/vae, dims,
# the WAN negative prompt, and an optional uploaded start_image filename (omit → text-to-video).


def build(prompt, seed, prefix, params):
    graph = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": params["unet"], "weight_dtype": "default"}},
        "2": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["1", 0], "shift": params.get("shift", 8.0)}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": params["clip"], "type": "wan", "device": "default"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": params["vae"]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["3", 0]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": params.get("negative", ""), "clip": ["3", 0]}},
        "7": {"class_type": "Wan22ImageToVideoLatent", "inputs": {
            "vae": ["4", 0], "width": params.get("width", 1280), "height": params.get("height", 704),
            "length": params.get("length", 121), "batch_size": 1}},
        "8": {"class_type": "KSampler", "inputs": {
            "model": ["2", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["7", 0],
            "seed": seed, "steps": params.get("steps", 20), "cfg": params.get("cfg", 5.0),
            "sampler_name": params.get("sampler", "uni_pc"), "scheduler": params.get("scheduler", "simple"),
            "denoise": 1.0}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["4", 0]}},
        "10": {"class_type": "CreateVideo", "inputs": {"images": ["9", 0], "fps": params.get("fps", 24)}},
        "11": {"class_type": "SaveVideo", "inputs": {
            "video": ["10", 0], "filename_prefix": prefix, "format": "auto", "codec": "auto"}},
    }
    start = params.get("start_image")
    if start:
        graph["12"] = {"class_type": "LoadImage", "inputs": {"image": start}}
        graph["7"]["inputs"]["start_image"] = ["12", 0]
    return graph
