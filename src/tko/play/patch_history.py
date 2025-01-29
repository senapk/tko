import json

from diff_match_patch import diff_match_patch # type: ignore
import os

class PatchVersion:
    def __init__(self, label: str, content: str):
        self.label: str = label
        self.content: str = content
    
    def __str__(self):
        return "{}:{}".format(self.label, self.content)


class PatchHistory:
    def __init__(self):
        # the last element is the integral last version
        # all the other elements are patches to be applied
        self.patches: list[PatchVersion] = [] 
        self.json_file: str | None = None

    def set_json_file(self, path: str):
        self.json_file = path

    def load_json(self):
        if not self.json_file:
            return
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r') as file:
                    data = json.load(file)
                    for patch in data["patches"]:
                        self.patches.append(PatchVersion(patch["label"], patch["content"]))
            except:
                pass

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
            self.patches.append(PatchVersion(label, new_content))
            return label
        
        dmp = diff_match_patch()
        last = self.patches[-1]
        del self.patches[-1]

        patch = dmp.patch_make(new_content, last.content)
        if not patch: # não houve mudança
            return last.label
        
        patch_text = dmp.patch_toText(patch)
        self.patches.append(PatchVersion(last.label, patch_text))
        self.patches.append(PatchVersion(label, new_content))
        return label

    def restore_all(self) -> list[PatchVersion]:
        output: list[PatchVersion] = []
        if not self.patches:
            return output
        last = self.patches[-1]
        output.append(PatchVersion(last.label, last.content))
        index = len(self.patches) -2
        dmp = diff_match_patch()
        while index >= 0:
            label = self.patches[index].label
            patch = dmp.patch_fromText(self.patches[index].content)
            original = output[-1].content
            new_content = dmp.patch_apply(patch, original)[0]
            output.append(PatchVersion(label, new_content))
            index -= 1
        output.reverse()
        return output

    def to_json(self):
        data: dict = {}
        data["patches"] = []
        for patch in self.patches:
            data["patches"].append({"label": patch.label, "content": patch.content})
        return data
    
    def __str__(self):
        return str(self.to_json())