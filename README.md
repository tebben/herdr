# Herdr setup

Portable customizations for the stock **Herdr app**. `config/` owns our keys,
settings, personal layouts, and custom mod sources; generated app state stays
out of Git. Agents must read the live Herdr manual referenced by `AGENTS.md`
and verify supported APIs first. No custom Herdr builds.

Requires a running `herdr-app`, `hc`, Neovim 0.10+, `just`, Python 3, Bash,
curl, tar, and `sha256sum` or `shasum` (Linux/macOS).

```sh
just                 # list commands
just apply           # install pinned mod, back up, deploy config, select main-copy
just capture         # save live changes to already-managed config files
just check           # tests, JSON validation, installed mod checks, app errors
```

Edit files in `config/`, then `just apply`. If you changed settings in the app,
run `just capture` first and review `git diff`. Apply replaces whole managed
files, including keys; local backups are in `.backups/`. Restore a backed-up
file to the app home, then capture it. `HERDR_APP_HOME` overrides the default
`~/.config/herdr-app`. New custom files must be added under `config/` explicitly.

First mod: [ChmaraX/herdr-nvim](https://github.com/ChmaraX/herdr-nvim/tree/main/herdr-app).
Its verified prebuilt release is pinned in `herdr-nvim.version`; binaries and
upstream mods stay outside Git. **Files** opens the tree and Neovim; clicking a
file opens it there. Linux: **Alt+E** toggles both, **Alt+Shift+E** focuses the
tree, **Alt+O** opens the agent-file picker. macOS uses Cmd instead of Alt.
The integration also includes upstream preview/comment features. Installation
downloads from GitHub; the mod runs Neovim, `hc`, and git and can read project
files and agent session logs.

Use **Ctrl+H/J/K/L** or **Alt+H/J/K/L** to focus adjacent panes and focusable
panels. **Ctrl+Shift+H/J/K/L** moves the nearest pane border left/down/up/right
by 40 pixels. These Ctrl bindings intercept keys in terminals, including
Neovim; they no longer perform their usual terminal or editor actions.

The cloned Spaces and Agents panels use `j`/`k` to select a row, `Enter` to
open it, and `h`/`l` to move focus horizontally. They do not receive upstream
panel updates automatically.

To update the mod, edit `herdr-nvim.version`, run `just install-nvim`, review
live changes, then `just capture` and `just check`. Herdr updates normally;
our cloned layout and keys need manual review for new upstream defaults.