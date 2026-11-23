set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

default:
    @just --list

# Install only the pinned upstream prebuilt Neovim integration.
install-nvim:
    python3 scripts/config.py backup
    bash scripts/install-nvim.sh

# Deploy owned config; live files are backed up before replacement.
apply: install-nvim
    python3 scripts/config.py apply
    herdr-app do layout.switch '{"name":"teebs"}'
    just check

# Save app-side edits to files already owned by this repository.
capture:
    python3 scripts/config.py capture

# Verify deployment without writing configuration.
check:
    python3 -m unittest discover -s tests
    python3 scripts/config.py check
