#!/usr/bin/env bash
# Install the research kit: symlink skills, agents and the user profile into ~/.claude,
# register the hook.
# Idempotent; refuses to overwrite anything that is not already a symlink into the kit.
set -euo pipefail

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE="$HOME/.claude"
mkdir -p "$CLAUDE/skills" "$CLAUDE/agents"

link() {
    local src="$1" dst="$2"
    if [ -L "$dst" ]; then
        ln -sfn "$src" "$dst"
    elif [ -e "$dst" ]; then
        echo "skip: $dst exists and is not a symlink" >&2
        return
    else
        ln -s "$src" "$dst"
    fi
    echo "linked $dst -> $src"
}

for d in "$KIT"/skills/*/; do
    name="$(basename "$d")"
    link "$KIT/skills/$name" "$CLAUDE/skills/$name"
done
for f in "$KIT"/agents/*.md; do
    link "$f" "$CLAUDE/agents/$(basename "$f")"
done
# the user's profile, read in every session (skipped if a regular file exists there)
link "$KIT/user/CLAUDE.md" "$CLAUDE/CLAUDE.md"

# register the PostToolUse hook in ~/.claude/settings.json, keeping all other keys
python3 - "$CLAUDE/settings.json" "$KIT/hooks/post_edit.py" <<'EOF'
import json, os, sys
path, hook = sys.argv[1], sys.argv[2]
settings = json.load(open(path)) if os.path.exists(path) else {}
command = f"python3 {hook}"
post = settings.setdefault("hooks", {}).setdefault("PostToolUse", [])
present = any(h.get("command") == command for entry in post for h in entry.get("hooks", []))
if not present:
    post.append({"matcher": "Edit|Write|MultiEdit",
                 "hooks": [{"type": "command", "command": command}]})
    with open(path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    print(f"registered hook in {path}")
else:
    print("hook already registered")
EOF
