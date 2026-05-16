from pathlib import Path

from tko.util.decoder import Decoder


class TypeScriptMacroPreprocessor:
    tag = 'constinput=()=>""'
    input_cmd = (
        r'const input: () => string = (() => { let lines: string[] | undefined; let index = 0; '
        r'let readlineSync: any; return (): string => { const isTTY = process?.stdin?.isTTY; if (isTTY) { '
        r'readlineSync = readlineSync ?? require("readline-sync"); return readlineSync.question(); } if (!lines) { '
        r'try { const fs = require("fs"); lines = fs.readFileSync(0, "utf-8").split(/\r?\n/); } catch { lines = []; } } '
        r'return lines![index++] ?? ""; }; })();'
    )

    @classmethod
    def copy_and_patch(cls, path_list: list[Path], copy_dir: Path) -> list[Path]:
        copy_dir.mkdir(parents=True, exist_ok=True)
        new_files = [copy_dir / source.name for source in path_list]

        for origin, destiny in zip(path_list, new_files):
            content = Decoder.load(origin)
            lines = content.splitlines(keepends=True)

            inserted = False
            output: list[str] = []
            for line in lines:
                match = False
                if not inserted:
                    filtered = "".join([char for char in line if char != " "])
                    match = filtered.startswith(cls.tag)
                if match:
                    inserted = True
                    output.append(cls.input_cmd)
                else:
                    output.append(line)

            destiny.write_text("".join(output), encoding="utf-8")
        return new_files