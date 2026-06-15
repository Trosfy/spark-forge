# Single access point for the local ComfyUI deployment. Image generation uses the
# HTTP API; image-to-3D runs a script inside the same container. Both reach one
# ComfyUI, so its URL and container name resolve from one place.
import json
import subprocess
import time
import urllib.request


class ComfyApi:
    def __init__(self, base_url):
        self.base = base_url.rstrip("/")

    def _post(self, path, payload):
        req = urllib.request.Request(
            self.base + path,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)

    def _get(self, path):
        with urllib.request.urlopen(self.base + path, timeout=30) as resp:
            return json.load(resp)

    def submit(self, graph):
        return self._post("/prompt", {"prompt": graph})["prompt_id"]

    def wait(self, prompt_id, timeout=1800, poll=2.0):
        start = time.time()
        while time.time() - start < timeout:
            entry = self._get(f"/history/{prompt_id}").get(prompt_id)
            if entry:
                status = entry.get("status", {})
                if status.get("status_str") == "error":
                    raise RuntimeError(json.dumps(status)[:2000])
                files = [
                    f"{img['subfolder']}/{img['filename']}" if img.get("subfolder") else img["filename"]
                    for out in entry.get("outputs", {}).values()
                    for img in out.get("images", [])
                ]
                if files:
                    return files, time.time() - start
            time.sleep(poll)
        raise TimeoutError("timed out waiting for ComfyUI")


class ComfyContainer:
    def __init__(self, name):
        self.name = name

    def run(self, *cmd, check=False):
        return subprocess.run(["docker", "exec", self.name, *cmd], check=check)

    def copy_in(self, src, dst):
        subprocess.run(["docker", "cp", src, f"{self.name}:{dst}"], check=True)

    def has(self, path):
        return self.run("test", "-e", path).returncode == 0

    def host_path_for(self, dest):
        try:
            result = subprocess.run(
                ["docker", "inspect", "-f",
                 "{{range .Mounts}}{{.Source}}|{{.Destination}}{{println}}{{end}}", self.name],
                capture_output=True, text=True)
        except FileNotFoundError:
            return None
        if result.returncode != 0:
            return None
        for line in result.stdout.splitlines():
            src, _, dst = line.partition("|")
            if dst == dest:
                return src
        return None

    def health(self):
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Health.Status}}", self.name],
            capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None


class Comfy:
    def __init__(self, cfg):
        self.cfg = cfg
        self.api = ComfyApi(cfg["FORGE_COMFY_URL"])
        self.container = ComfyContainer(cfg["FORGE_COMFY_CONTAINER"])
