# Builds the HunyuanVideo 1.5 image-to-video ComfyUI graph (official 720p i2v template).
# Hunyuan 1.5 uses two text encoders (Qwen2.5-VL + ByT5) via DualCLIPLoader (type
# hunyuan_video_15), a HunyuanVideo15ImageToVideo conditioning node, and a SamplerCustomAdvanced
# chain (CFGGuider + BasicScheduler + KSamplerSelect). prompt = positive text; params carries the
# two encoders, vae, dims, and an optional uploaded start_image filename.


def build(prompt, seed, prefix, params):
    width, height = params.get("width", 1280), params.get("height", 720)
    graph = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": params["unet"], "weight_dtype": "default"}},
        "2": {"class_type": "DualCLIPLoader", "inputs": {
            "clip_name1": params["clip"], "clip_name2": params["clip2"],
            "type": "hunyuan_video_15", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": params["vae"]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": params.get("negative", ""), "clip": ["2", 0]}},
        "6": {"class_type": "HunyuanVideo15ImageToVideo", "inputs": {
            "positive": ["4", 0], "negative": ["5", 0], "vae": ["3", 0],
            "width": width, "height": height, "length": params.get("length", 121), "batch_size": 1}},
        "7": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["1", 0], "shift": params.get("shift", 7.0)}},
        "8": {"class_type": "CFGGuider", "inputs": {
            "model": ["7", 0], "positive": ["6", 0], "negative": ["6", 1], "cfg": params.get("cfg", 6.0)}},
        "9": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": params.get("sampler", "euler")}},
        "10": {"class_type": "BasicScheduler", "inputs": {
            "model": ["7", 0], "scheduler": params.get("scheduler", "simple"),
            "steps": params.get("steps", 20), "denoise": 1.0}},
        "11": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "12": {"class_type": "SamplerCustomAdvanced", "inputs": {
            "noise": ["11", 0], "guider": ["8", 0], "sampler": ["9", 0],
            "sigmas": ["10", 0], "latent_image": ["6", 2]}},
        "13": {"class_type": "VAEDecode", "inputs": {"samples": ["12", 0], "vae": ["3", 0]}},
        "14": {"class_type": "CreateVideo", "inputs": {"images": ["13", 0], "fps": params.get("fps", 24)}},
        "15": {"class_type": "SaveVideo", "inputs": {
            "video": ["14", 0], "filename_prefix": prefix, "format": "auto", "codec": "auto"}},
    }
    start = params.get("start_image")
    if start:
        graph["16"] = {"class_type": "LoadImage", "inputs": {"image": start}}
        graph["6"]["inputs"]["start_image"] = ["16", 0]
    return graph
