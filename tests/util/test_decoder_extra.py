from pathlib import Path

from tko.util.decoder import Decoder


def test_decoder_load_falls_back_to_latin1(tmp_path: Path) -> None:
    file_path = tmp_path / "latin1.txt"
    file_path.write_bytes(b"caf\xe9")

    value = Decoder.load(file_path)

    assert value == "cafe\u0301\n" or value == "caf\u00e9\n"
