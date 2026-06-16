# Model registry. A profile (models/<name>.json) maps a model to a family (its graph),
# shared weights/params, and a `quants` map whose entries each override the weights that
# change for one quantization (often just the diffusion file). Add a quant = an entry;
# add a model = a profile JSON; add an architecture = a family builder in FAMILIES below.
import json
import os

import acestep_graph
import flux2_graph
import zimage_graph

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models")

# family -> graph builder(prompt, seed, prefix, params)
FAMILIES = {
    "flux2": flux2_graph.build,
    "z_image": zimage_graph.build,
    "ace_step": acestep_graph.build,
}
# families whose output is audio, not an image (selects which CLI handles them)
AUDIO_FAMILIES = {"ace_step"}


def modality_of(profile):
    return "audio" if profile.get("family") in AUDIO_FAMILIES else "image"


def available():
    try:
        return sorted(f[:-5] for f in os.listdir(_DIR) if f.endswith(".json"))
    except FileNotFoundError:
        return []


def load_profile(name):
    path = os.path.join(_DIR, name + ".json")
    if not os.path.isfile(path):
        raise SystemExit(f"unknown model '{name}'. available: {', '.join(available()) or '(none)'}")
    with open(path) as fh:
        profile = json.load(fh)
    if profile.get("family") not in FAMILIES:
        raise SystemExit(f"model '{name}': unknown family '{profile.get('family')}' (have: {', '.join(FAMILIES)})")
    return profile


def quants_of(profile):
    return sorted(profile.get("quants", {}))


def effective_quant(profile, quant=None):
    quants = profile.get("quants")
    if not quants:
        if quant:
            raise SystemExit("model has no quant variants; drop --quant")
        return None
    name = quant or profile.get("default_quant")
    if not name and len(quants) == 1:
        name = next(iter(quants))
    if not name:
        raise SystemExit(f"model has multiple quants ({', '.join(sorted(quants))}); pass --quant")
    if name not in quants:
        raise SystemExit(f"unknown quant '{name}'. available: {', '.join(sorted(quants))}")
    return name


def resolve_params(profile, quant=None):
    params = {k: v for k, v in profile.items() if k not in ("quants", "default_quant")}
    name = effective_quant(profile, quant)
    if name:
        params.update(profile["quants"][name])
    return params


def build(profile, prompt, seed, prefix, overrides, quant=None):
    params = resolve_params(profile, quant)
    for key, val in overrides.items():
        if val is not None:
            params[key] = val
    return FAMILIES[profile["family"]](prompt, seed, prefix, params)
