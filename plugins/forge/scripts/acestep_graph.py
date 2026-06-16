# Builds the ACE-Step 1.5 (AIO checkpoint) text-to-music ComfyUI graph.
# Verified against the official audio_ace_step_1_5_checkpoint template. The 1.5 text encoder
# is autoregressive (generate_audio_codes) with music-theory + LM sampling params; here
# `prompt` is the style "tags", and params carries lyrics/duration and the rest.


def build(prompt, seed, prefix, params):
    duration = float(params.get("duration", 120))
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": params["checkpoint"]}},
        "2": {"class_type": "TextEncodeAceStepAudio1.5", "inputs": {
            "clip": ["1", 1],
            "tags": prompt,
            "lyrics": params.get("lyrics", ""),
            "seed": seed,
            "bpm": params.get("bpm", 120),
            "duration": duration,
            "timesignature": params.get("timesignature", "4"),
            "language": params.get("language", "en"),
            "keyscale": params.get("keyscale", "C major"),
            "generate_audio_codes": params.get("generate_audio_codes", True),
            "cfg_scale": params.get("cfg_scale", 2.0),
            "temperature": params.get("temperature", 0.85),
            "top_p": params.get("top_p", 0.9),
            "top_k": params.get("top_k", 0),
            "min_p": params.get("min_p", 0.0)}},
        "3": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["2", 0]}},
        "4": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["1", 0], "shift": params.get("shift", 3.0)}},
        "5": {"class_type": "EmptyAceStep1.5LatentAudio", "inputs": {"seconds": duration, "batch_size": 1}},
        "6": {"class_type": "KSampler", "inputs": {
            "model": ["4", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["5", 0],
            "seed": seed, "steps": params.get("steps", 8), "cfg": params.get("cfg", 1.0),
            "sampler_name": params.get("sampler", "euler"), "scheduler": params.get("scheduler", "simple"),
            "denoise": 1.0}},
        "7": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
        "8": {"class_type": "SaveAudioMP3", "inputs": {
            "filename_prefix": prefix, "audio": ["7", 0], "quality": params.get("quality", "V0")}},
    }
