# Shared ComfyUI graph helpers.


def unet_loader(unet, dtype="default"):
    # GGUF weights need ComfyUI-GGUF's UnetLoaderGGUF, not the core UNETLoader, so the
    # loader is chosen by the quantization (file extension), not by the family.
    if unet.lower().endswith(".gguf"):
        return {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": unet}}
    return {"class_type": "UNETLoader", "inputs": {"unet_name": unet, "weight_dtype": dtype}}
