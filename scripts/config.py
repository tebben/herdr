"""Sync only repository-owned Herdr files, never app state or shipped files."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
HOME = Path(os.environ.get("HERDR_APP_HOME", "~/.config/herdr-app")).expanduser()
UPSTREAM_MODS = {"herdr-nvim", "herdr-nvim-header"}


def owned(path, installed):
    parts = path.parts
    if path.is_absolute() or not parts or any(p.startswith(".") for p in parts):
        raise ValueError(f"Not an owned config path: {path}")
    if path.name == "jsconfig.json" or path.name.endswith((".d.ts", ".error")):
        raise ValueError(f"Generated file: {path}")
    if len(parts) == 1 and parts[0] in {"keys.json", "settings.json", "programs.json"}:
        return
    if len(parts) == 2 and parts[0] in {"layouts", "themes"} and path.suffix == ".json":
        if parts[0] == "layouts" and (
            path.stem in {"main", "terminals", "win98"} or f"layout:{path.stem}" in installed
        ):
            raise ValueError(f"Shipped layout: {path}")
        return
    if len(parts) >= 3 and parts[0] == "mods":
        if parts[1] in installed or parts[1] in UPSTREAM_MODS:
            raise ValueError(f"Installed upstream mod: {path}")
        return
    raise ValueError(f"Not an owned config path: {path}")


def inventory(config=CONFIG, home=HOME, paths=None):
    installed_file = home / "installed.json"
    installed = json.loads(installed_file.read_text()) if installed_file.exists() else {}
    paths = [Path(p) for p in paths] if paths else [
        p.relative_to(config) for p in sorted(config.rglob("*")) if p.is_file() or p.is_symlink()
    ]
    for path in paths:
        owned(path, installed)
        for base in (config, home):
            candidate = base / path
            if candidate.resolve() != base.resolve() / path:
                raise ValueError(f"Symlink in managed path: {candidate}")
    return paths


def contents(base, paths):
    result = {}
    for path in paths:
        data = (base / path).read_bytes()
        if path.suffix == ".json":
            json.loads(data)
        result[path] = data
    return result


def backup(home=HOME, root=ROOT, managed=()):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    dest = root / ".backups" / stamp
    paths = [Path(name) for name in ("keys.json", "settings.json", "programs.json")
             if (home / name).is_file()]
    paths += [p.relative_to(home) for p in (home / "layouts").glob("*.json")]
    paths += [p for p in managed if (home / p).is_file()]
    for path in sorted(set(paths)):
        (dest / path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(home / path, dest / path)
    print(f"Backup: {dest}")
    return dest


def sync(action, config=CONFIG, home=HOME, root=ROOT, paths=None):
    paths = inventory(config, home, paths)
    if not paths:
        raise ValueError("No managed files under config/")
    source, target = (config, home) if action == "apply" else (home, config)
    data = contents(source, paths)
    if action == "apply":
        backup(home, root, paths)
    for path, value in data.items():
        dest = target / path
        if dest.exists() and dest.read_bytes() == value:
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=dest.parent, prefix=f".{dest.name}.", delete=False) as file:
            temporary = Path(file.name)
            file.write(value)
        try:
            shutil.copymode(dest if dest.exists() else source / path, temporary)
            temporary.replace(dest)
        finally:
            temporary.unlink(missing_ok=True)
        print(f"{action}: {path}")


def check():
    paths = inventory()
    if not paths:
        raise ValueError("No managed files under config/")
    data = contents(CONFIG, paths)
    live = contents(HOME, paths)
    for path in paths:
        if data[path] != live[path]:
            raise ValueError(f"Live file differs from config/{path}; capture or apply first")
    mods = UPSTREAM_MODS | {p.parts[1] for p in paths if p.parts[0] == "mods"}
    for mod in sorted(mods):
        subprocess.run(["herdr-app", "check", str(HOME / "mods" / mod)], check=True)
    status = json.loads(subprocess.check_output(["herdr-app", "status"], text=True))
    if status.get("errors"):
        raise ValueError(f"Herdr errors: {status['errors']}")
    print("Owned config matches live files; mod checks passed; no app errors.")


if __name__ == "__main__":
    try:
        action = sys.argv[1]
        if action in {"apply", "capture"}:
            sync(action, paths=sys.argv[2:] or None)
        elif action == "backup":
            backup()
        elif action == "check":
            check()
        else:
            raise ValueError(f"Unknown command: {action}")
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
