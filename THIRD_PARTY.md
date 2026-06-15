# Third-party components & model licenses

This repository contains **code only**. It does **not** include or distribute any
model weights. To use it you download models from their upstream sources, and you
must accept their licenses — **several are non-commercial**.

| Component | Source | License | Notes |
|---|---|---|---|
| FLUX.2-dev | black-forest-labs (Hugging Face) | FLUX.2-dev Non-Commercial License | Review current terms before any commercial use. |
| Mistral text encoder (FLUX.2) | Mistral AI | Per upstream | Bundled as the FLUX.2 text encoder. |
| Hunyuan3D-2.1 | Tencent (`Tencent-Hunyuan/Hunyuan3D-2.1`) | Tencent Hunyuan3D Community License | Review usage/territory restrictions. |
| ComfyUI | comfyanonymous | GPL-3.0 | Runs the FLUX.2 graph; not bundled here. |

NVFP4 weights are a Blackwell-specific quantization of the upstream models — the
upstream license still governs them.

You are responsible for complying with each upstream license. This repository's own
code is MIT (see `LICENSE`).
