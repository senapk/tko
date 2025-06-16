class KV:
    @staticmethod
    def decode_line(line: str, sep: str) -> dict[str, str]:
        args: list[str] = line.split(sep)
        return KV.decode_args(args)

    @staticmethod
    def decode_args(args: list[str]) -> dict[str, str]:
        kv: dict[str, str] = {}
        for value in args:
            parts = value.split(":")
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                kv[key] = value
        return kv
    
    @staticmethod
    def encode_kv(kv: dict[str, str], sep: str = ", ") -> str:
        items: list[str] = []
        for k, v in kv.items():
            items.append(f"{k}:{v}")
        return sep.join(items)
