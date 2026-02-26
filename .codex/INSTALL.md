# Installing Claude Done for Codex

Save and recall session summaries in Codex via native skill discovery.

## Prerequisites

- Git

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Genuifx/claude-done.git ~/.codex/claude-done
   ```

2. **Create the skills symlink:**
   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.codex/claude-done/skills ~/.agents/skills/claude-done
   ```

   **Windows (PowerShell):**
   ```powershell
   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
   cmd /c mklink /J "$env:USERPROFILE\.agents\skills\claude-done" "$env:USERPROFILE\.codex\claude-done\skills"
   ```

3. **Restart Codex** to discover the skills.

## Verify

```bash
ls -la ~/.agents/skills/claude-done
```

You should see a symlink pointing to your claude-done skills directory.

Start a new Codex session and try:
- `/done` — save a session summary
- `/recall` — search past summaries

## Updating

```bash
cd ~/.codex/claude-done && git pull
```

## Uninstalling

```bash
rm ~/.agents/skills/claude-done
# optionally:
rm -rf ~/.codex/claude-done
```
