#!/usr/bin/env python3
# Build every model x quant graph (no weights, no ComfyUI) and check it is well-formed.
# This is the cheap gate that lets us add models without downloading tens of GB first.
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import model_registry  # noqa: E402


def check(name, quant, graph):
    assert isinstance(graph, dict) and graph, f"{name}/{quant}: empty graph"
    classes = {node["class_type"] for node in graph.values()}
    assert any("Save" in c for c in classes), f"{name}/{quant}: no save node"
    for node in graph.values():
        for val in node["inputs"].values():
            if isinstance(val, list) and len(val) == 2 and isinstance(val[0], str):
                assert val[0] in graph, f"{name}/{quant}: dangling node ref {val}"
    if quant and quant.lower().startswith("gguf"):
        assert any("GGUF" in c for c in classes), f"{name}/{quant}: gguf quant must use a GGUF loader"


def main():
    models = model_registry.available()
    assert models, "no model profiles found"
    built = 0
    for name in models:
        profile = model_registry.load_profile(name)
        for quant in (model_registry.quants_of(profile) or [None]):
            graph = model_registry.build(profile, "a test prompt", 1, "forge/test", {}, quant=quant)
            check(name, quant, graph)
            built += 1
            print(f"ok  {name}/{quant or '-'}  ({len(graph)} nodes)")
    print(f"\nbuilt {built} graph(s) across {len(models)} model(s)")


if __name__ == "__main__":
    main()
