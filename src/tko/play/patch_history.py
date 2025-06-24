import json
from diff_match_patch import diff_match_patch # type: ignore
import os

class PatchInfo:
    def __init__(self, label: str, content: str, lines: int | None = None):
        self.label: str = label
        self.content: str = content
        if lines is not None:
            self.lines: int = lines
        else:
            self.lines: int = len(content.splitlines()) if content else 0
    
    def __str__(self):
        return "{}:{}".format(self.label, self.content)


class PatchHistory:
    def __init__(self):
        # the last element is the integral last version
        # all the other elements are patches to be applied
        self.patches: list[PatchInfo] = [] 
        self.json_file: str | None = None

    def set_json_file(self, path: str):
        self.json_file = path
        return self

    def load_json(self):
        if not self.json_file:
            return self
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r') as file:
                    data = json.load(file)
                    for patch in data["patches"]:
                        if "lines" in patch:
                            lines = int(patch["lines"])
                        else:
                            lines = None
                        self.patches.append(PatchInfo(patch["label"], patch["content"], lines))
            except:
                pass
        return self

    # save patches, label and content to json file
    def save_json(self):
        if not self.json_file:
            return
        with open(self.json_file, 'w') as file:
            json.dump(self.to_json(), file, indent=4)

    # store a new version of the file in json
    # return the label of the last version stored
    def store_version(self, label: str, new_content: str) -> str:
        if not self.patches:
            self.patches.append(PatchInfo(label, new_content))
            return label
        
        dmp = diff_match_patch()
        last = self.patches[-1]
        del self.patches[-1]

        patch = dmp.patch_make(new_content, last.content) # type: ignore
        if not patch: # não houve mudança
            return last.label
        
        patch_text = dmp.patch_toText(patch) # type: ignore
        self.patches.append(PatchInfo(last.label, patch_text, len(last.content.splitlines())))
        self.patches.append(PatchInfo(label, new_content, len(new_content.splitlines())))
        return label

    def restore_all(self) -> list[PatchInfo]:
        output: list[PatchInfo] = []
        if not self.patches:
            return output
        last = self.patches[-1]
        output.append(PatchInfo(last.label, last.content))
        index = len(self.patches) -2
        dmp = diff_match_patch()
        while index >= 0:
            label = self.patches[index].label
            patch = dmp.patch_fromText(self.patches[index].content) # type: ignore
            original = output[-1].content
            new_content = dmp.patch_apply(patch, original)[0] # type: ignore
            output.append(PatchInfo(label, new_content)) # type: ignore
            index -= 1
        output.reverse()
        return output

    def to_json(self):
        data: dict[str, list[dict[str, str]]] = {"patches": []}
        for patch in self.patches:
            data["patches"].append({"label": patch.label, "content": patch.content, "lines": str(patch.lines)})
        return data

    
    def __str__(self):
        return str(self.to_json())