# Builds the WAN 2.2 14B first-last-frame / image-to-video ComfyUI graph.
# Verified against the official video_wan2_2_14B_flf2v template. WAN 2.2 14B is a MoE:
# a high-noise expert denoises the early steps and a low-noise expert the late steps, so
# the graph loads both and chains two KSamplerAdvanced passes split at `split_step`.
# prompt = positive text; params carries the two experts, encoder, vae, dims, the WAN
# negative prompt, and the uploaded start/end image filenames (end optional → plain I2V).


def build(prompt, seed, prefix, params):
    steps = params.get("steps", 20)
    split = params.get("split_step", steps // 2)
    cfg = params.get("cfg", 4.0)
    shift = params.get("shift", 8.0)
    sampler = params.get("sampler", "euler")
    scheduler = params.get("scheduler", "simple")
    graph = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": params["high_noise"], "weight_dtype": "default"}},
        "2": {"class_type": "UNETLoader", "inputs": {"unet_name": params["low_noise"], "weight_dtype": "default"}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": params["clip"], "type": "wan", "device": "default"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": params["vae"]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["3", 0]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": params.get("negative", ""), "clip": ["3", 0]}},
        "7": {"class_type": "LoadImage", "inputs": {"image": params.get("start_image", "start.png")}},
        "8": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["1", 0], "shift": shift}},
        "9": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["2", 0], "shift": shift}},
        "10": {"class_type": "WanFirstLastFrameToVideo", "inputs": {
            "positive": ["5", 0], "negative": ["6", 0], "vae": ["4", 0],
            "width": params.get("width", 832), "height": params.get("height", 480),
            "length": params.get("length", 81), "batch_size": 1, "start_image": ["7", 0]}},
        "11": {"class_type": "KSamplerAdvanced", "inputs": {
            "model": ["8", 0], "add_noise": "enable", "noise_seed": seed, "steps": steps, "cfg": cfg,
            "sampler_name": sampler, "scheduler": scheduler,
            "positive": ["10", 0], "negative": ["10", 1], "latent_image": ["10", 2],
            "start_at_step": 0, "end_at_step": split, "return_with_leftover_noise": "enable"}},
        "12": {"class_type": "KSamplerAdvanced", "inputs": {
            "model": ["9", 0], "add_noise": "disable", "noise_seed": seed, "steps": steps, "cfg": cfg,
            "sampler_name": sampler, "scheduler": scheduler,
            "positive": ["10", 0], "negative": ["10", 1], "latent_image": ["11", 0],
            "start_at_step": split, "end_at_step": 10000, "return_with_leftover_noise": "disable"}},
        "13": {"class_type": "VAEDecode", "inputs": {"samples": ["12", 0], "vae": ["4", 0]}},
        "14": {"class_type": "CreateVideo", "inputs": {"images": ["13", 0], "fps": params.get("fps", 16)}},
        "15": {"class_type": "SaveVideo", "inputs": {
            "video": ["14", 0], "filename_prefix": prefix, "format": "auto", "codec": "auto"}},
    }
    end = params.get("end_image")
    if end:
        graph["16"] = {"class_type": "LoadImage", "inputs": {"image": end}}
        graph["10"]["inputs"]["end_image"] = ["16", 0]
    return graph
