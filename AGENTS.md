# Working on this repository

This repository owns portable Herdr app customizations, not Herdr itself.

## Investigate before implementing

- At the start of every Herdr task, read `~/.config/herdr-app/AGENTS.md`.
  If `HERDR_APP_HOME` selects another home, read its `AGENTS.md` instead.
  Read it from disk every time: Herdr rewrites it on startup. Do not vendor,
  edit, or replace it. If it is missing, stop and ask the user to start Herdr.
- Check that home's `herdr.d.ts`, relevant `gpui-kit.d.ts` definitions,
  shipped examples, and `herdr-app commands` as needed.
- Establish whether the requested feature is supported and identify the
  documented extension point before editing. If it is unsupported, explain
  the limitation and stop. Do not work around inaccessible internals.
- Use only supported settings, keys, layouts, mods, commands, and external
  programs through documented APIs. Never build, patch, fork, or replace
  Herdr or herdr-core. Do not modify shipped layouts/mods; clone them first.
- Read third-party recipes and code before installation. Explain network
  access, programs run, and files read. Use verified prebuilt releases,
  never an unreviewed remote-script pipe or a source-build fallback.

## Ownership and workflow

- `config/` contains only owned files, relative to the Herdr app home:
  keys, settings, programs, personal layouts/themes, and custom mod sources.
  The initial personal layout is `teebs`.
- `herdr-nvim.version` pins the upstream Neovim integration. Its downloaded
  mods, launchers, Lua, and binaries are installed artifacts, not our sources.
  Do not copy them into Git or edit them in place.
- Never track runtime state, session logs, generated types/manuals, shipped
  files, secrets, machine-specific launchers, or cache/backup contents.
- Use `just` rather than ad hoc deployment commands. Run `just capture`
  before editing if the user changed managed files in the app; inspect the
  diff. Edit owned files here, then run `just apply` and `just check`.
  `just apply` replaces managed live files, including the whole keys file.
- Add new owned files under `config/`. `just capture` refreshes existing
  owned files only; it does not sweep the app home into Git.
- Keep backups in `.backups/`, preserve unrelated changes, and never replace
  occupied keybindings without permission. Custom keys must not steal
  terminal input silently.
- After updating the pinned mod release, run `just install-nvim`, inspect
  the resulting live config, then `just capture` and `just check`.
  Review new upstream defaults manually: custom layouts and keys do not
  automatically inherit Herdr's changes.
- Check every changed mod with `herdr-app check <folder>` and exercise it
  in the running app. Initial-render checks alone do not prove interactions.
  Inspect `herdr-app status` and relevant `.error` files after changes.
- Keep `README.md` short and update it when workflow or commands change.

## Commits

Agents may commit automatically in this repository after verification.
Use Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`). One commit
must contain all changes belonging to one feature/change, including tests
and documentation; exclude unrelated work. Announce repository, branch,
and files before committing. Do not invent or reuse ticket keys.
Include the required co-author trailer. Never push without explicit approval.
Report separately whether changes are uncommitted, committed locally, or pushed.
