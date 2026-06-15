# Model registry. A profile (models/<name>.json) maps a model+version to a family
# (its graph) plus weights and default params. Add a version = a new profile JSON;
# add an architecture = a new family builder, registered in FAMILIES below.
import json
import os

import flux2_graph

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models")

# family -> graph builder(prompt, seed, prefix, params)
FAMILIES = {"flux2": flux2_graph.build}


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


def build(profile, prompt, seed, prefix, overrides):
    params = dict(profile)
    for key, val in overrides.items():
        if val is not None:
            params[key] = val
    return FAMILIES[profile["family"]](prompt, seed, prefix, params)
