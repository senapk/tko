import yaml
import os
import tempfile
import time
from pathlib import Path
from typing import Any

def atomic_write_yaml(path: Path, data: dict[str, Any]) -> None:
    path = Path(path).resolve()
    dir_path = path.parent
    # Garante que o diretório existe
    dir_path.mkdir(parents=True, exist_ok=True)
    
    tmp_path: Path | None = None

    try:
        # 1. Cria e escreve no arquivo temporário
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=dir_path,
            delete=False,
            suffix=".tmp"
        ) as f:
            tmp_path = Path(f.name)
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
            
            # Garante que os dados saíram do buffer do Python para o SO
            f.flush()
            # Garante que o SO escreveu no hardware
            os.fsync(f.fileno())

        # 2. Substituição Atômica
        # Tentamos o replace. Se houver erro de permissão (comum no Windows), 
        # fazemos uma breve espera.
        for attempt in range(3):
            try:
                os.replace(tmp_path, path)
                break
            except PermissionError:
                if attempt < 2:
                    time.sleep(0.05 * (attempt + 1))
                else:
                    raise
        
        # 3. Persistência do Diretório (Apenas POSIX)
        if os.name == "posix":
            # Abre o diretório para sincronizar a alteração do nome do arquivo
            dir_fd = os.open(str(dir_path), os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)

    except Exception as e:
        # Se algo deu errado e o temp ainda existe, tentamos limpar
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        raise e