# Quality policy

Default to the higher-quality option when the only cost is wall-clock time:

- Prefer base steps over speed LoRAs (e.g. Turbo) unless the user asks for speed —
  speed LoRAs shift texture character at the same seed.
- Prefer higher precision (fp16 over fp8 over fp4) where memory allows.
- Reuse an explicit seed to reproduce a result; vary it to explore.

Generation here is local: there is no per-image cost, only time.
