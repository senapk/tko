import os
from pathlib import Path
from tko.config.languages_drafts import readme_draft

class SandboxDrafts:
    sandbox_key_prefix = "user"

    def __init__(self):
        pass

    @staticmethod
    def format_draft_key(draft_id: int) -> str:
        return f"{SandboxDrafts.sandbox_key_prefix}_{draft_id:03d}"
    
    @staticmethod
    def find_max_numbered_key(task_keys_only: list[str]) -> int:
        numbered_keys: list[int] = []
        for key in task_keys_only:
            if key.startswith(SandboxDrafts.sandbox_key_prefix + "_"):
                try:
                    number = int(key[len(SandboxDrafts.sandbox_key_prefix) + 1:])
                    numbered_keys.append(number)
                except ValueError:
                    continue
        return max(numbered_keys) if numbered_keys else 0
    
    @staticmethod
    def create_sandbox_draft(dir: Path, title: str):
        with open (os.path.join(dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n" + readme_draft)
