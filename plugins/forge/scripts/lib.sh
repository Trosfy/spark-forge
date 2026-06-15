# shellcheck shell=bash
# Sourced by forge shell scripts. Resolves config: environment > ~/.config/forge/config > default.

forge_config_path() {
  local user="${XDG_CONFIG_HOME:-$HOME/.config}/forge/config"
  if [ -n "${FORGE_CONFIG:-}" ] && [ -f "$FORGE_CONFIG" ]; then
    echo "$FORGE_CONFIG"
  elif [ -f "$user" ]; then
    echo "$user"
  elif [ -f /etc/forge/config ]; then
    echo /etc/forge/config
  else
    echo "$user"
  fi
}

forge_load_config() {
  local cfg key val
  cfg="$(forge_config_path)"
  if [ -f "$cfg" ]; then
    while IFS='=' read -r key val; do
      case "$key" in '' | \#*) continue ;; esac
      key="${key// /}"
      val="${val%\"}"
      val="${val#\"}"
      if [ -z "${!key+x}" ]; then
        export "$key=$val"
      fi
    done <"$cfg"
  fi
  : "${FORGE_COMFY_URL:=http://localhost:8188}"
  : "${FORGE_COMFY_CONTAINER:=comfyui}"
  : "${FORGE_S3_PREFIX:=forge}"
  : "${FORGE_S3_PUBLIC:=false}"
  export FORGE_COMFY_URL FORGE_COMFY_CONTAINER FORGE_S3_PREFIX FORGE_S3_PUBLIC
}
