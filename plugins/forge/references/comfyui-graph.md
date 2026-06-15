# FLUX.2 ComfyUI graph

`flux2_graph.py` builds the official `image_flux2` template as a ComfyUI API graph:

```
UNETLoader ───────────────────────────────────────────────┐
CLIPLoader ─ CLIPTextEncode ─ FluxGuidance ─ BasicGuider ──┤
VAELoader ───────────────────────────────────────────────  SamplerCustomAdvanced ─ VAEDecode ─ SaveImage
Flux2Scheduler(steps,w,h) ─── sigmas ──────────────────────┤
KSamplerSelect(euler) ─────── sampler ─────────────────────┤
RandomNoise(seed) ─────────── noise ───────────────────────┤
EmptyFlux2LatentImage(w,h) ── latent ──────────────────────┘
```

Notes:
- FLUX.2-dev is guidance-distilled — there is **no negative-prompt channel**.
  Phrase exclusions as positive constraints in the prompt.
- Model / text-encoder / VAE filenames come from the model profile (`models/<name>.json`)
  and must exist in ComfyUI's `diffusion_models/`, `text_encoders/`, and `vae/` dirs.
- An optional LoRA inserts a `LoraLoaderModelOnly` ahead of the guider; speed LoRAs
  typically want fewer steps and lower guidance.
