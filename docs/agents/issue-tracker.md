# Issue Tracker

This project uses **bd (beads)** for issue tracking — a local CLI tool backed by Dolt.

## Commands

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work atomically
bd close <id>         # Complete work
bd create "Title" --description="..." -t bug|feature|task -p 0-4
```

## Workflow

- Use `bd` for ALL task tracking. Do not use markdown TODOs or external trackers.
- Always use `--json` flag for programmatic output.
- Link discovered work with `--deps discovered-from:<parent-id>`.
- Check `bd ready` before asking what to work on.
- See `AGENTS.md` for full beads integration details.
