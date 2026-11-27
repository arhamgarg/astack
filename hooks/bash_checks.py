#!/usr/bin/env python3
import json
import re
import sys

ZSH_MODIFIER = re.compile(r"(?<![\\{])\$[A-Za-z_]\w*:[a-zA-Z]")


def main():
    command = (json.load(sys.stdin).get("tool_input") or {}).get("command") or ""
    if ZSH_MODIFIER.search(command):
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "zsh reads $var:x as a history modifier. Write ${var}:path instead.",
        }}))


if __name__ == "__main__":
    main()
