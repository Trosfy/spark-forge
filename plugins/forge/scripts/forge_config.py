# Config resolution: built-in defaults < ~/.config/forge/config < environment.
import os

_DEFAULTS = {
    "FORGE_COMFY_URL": "http://localhost:8188",
    "FORGE_COMFY_CONTAINER": "comfyui",
    "FORGE_COMFY_INPUT": "/opt/ComfyUI/input",
    "FORGE_COMFY_OUTPUT": "/opt/ComfyUI/output",
    "FORGE_MODEL": "flux2-dev",
    "FORGE_HUNYUAN_REPO": "/root/work/Hunyuan3D-2.1",
    "FORGE_HY3D_CACHE": "/root/.cache/hy3dgen",
    "FORGE_S3_PREFIX": "forge",
    "FORGE_S3_PUBLIC": "false",
    "FORGE_CDN_DOMAIN": "",
    "FORGE_CDN_KEY_PAIR_ID": "",
    "FORGE_CDN_PRIVATE_KEY": "",
    "FORGE_CDN_TTL": "3600",
    "FORGE_INPUT_DIR": "",
    "FORGE_OUTPUT_DIR": "",
    "FORGE_S3_BUCKET": "",
    "FORGE_S3_REGION": "",
    "FORGE_AWS_PROFILE": "",
}


def _candidates():
    paths = []
    if os.environ.get("FORGE_CONFIG"):
        paths.append(os.environ["FORGE_CONFIG"])
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    paths.append(os.path.join(base, "forge", "config"))
    paths.append("/etc/forge/config")
    return paths


def config_path():
    for path in _candidates():
        if os.path.isfile(path):
            return path
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, "forge", "config")


def _parse(path):
    values = {}
    try:
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                values[key.strip()] = val.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return values


def load():
    values = dict(_DEFAULTS)
    values.update(_parse(config_path()))
    for key in values:
        if key in os.environ:
            values[key] = os.environ[key]
    return values
