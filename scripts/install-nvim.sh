#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
version=$(tr -d '\n' < herdr-nvim.version)
[[ "$version" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
    echo "Expected a release tag such as v1.3.1 in herdr-nvim.version" >&2
    exit 1
}

case "$(uname -s)-$(uname -m)" in
    Linux-x86_64) target=x86_64-unknown-linux-gnu ;;
    Linux-aarch64|Linux-arm64) target=aarch64-unknown-linux-gnu ;;
    Darwin-arm64) target=aarch64-apple-darwin ;;
    Darwin-x86_64) target=x86_64-apple-darwin ;;
    *) echo "No supported prebuilt mod for this platform; no source-build fallback." >&2; exit 1 ;;
esac

herdr-app status >/dev/null
command -v hc >/dev/null
command -v nvim >/dev/null

name="herdr-nvim-app-$target"
cache="$PWD/.cache/herdr-nvim/$version"
mkdir -p "$cache"
base="https://github.com/ChmaraX/herdr-nvim/releases/download/$version"
for asset in "$name.tar.gz" "$name.tar.gz.sha256"; do
    if [[ ! -f "$cache/$asset" ]]; then
        curl --fail --location --silent --show-error "$base/$asset" -o "$cache/$asset.part"
        mv "$cache/$asset.part" "$cache/$asset"
    fi
done

expected=$(awk 'NR == 1 {print $1}' "$cache/$name.tar.gz.sha256")
if command -v sha256sum >/dev/null; then
    actual=$(sha256sum "$cache/$name.tar.gz" | awk '{print $1}')
else
    actual=$(shasum -a 256 "$cache/$name.tar.gz" | awk '{print $1}')
fi
[[ "$expected" =~ ^[0-9a-fA-F]{64}$ && "$actual" == "$expected" ]] || {
    echo "Bundle checksum mismatch; nothing installed." >&2
    exit 1
}
tar -xzf "$cache/$name.tar.gz" -C "$cache"
bundle="$cache/$name"
binary="$bundle/bin/herdr-nvim"
"$binary" app-nvim-check

if [[ -x "$bundle/bin/herdr-nvim-launch" ]]; then
    "$binary" app-install --home "${HERDR_APP_HOME:-$HOME/.config/herdr-app}"
else
    # Older releases need their bundled installer; always pass a binary.
    bash "$bundle/herdr-app/install.sh" --binary "$binary" \
        --home "${HERDR_APP_HOME:-$HOME/.config/herdr-app}"
fi
