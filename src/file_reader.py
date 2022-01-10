from pathlib import Path


def read_file(path: Path) -> list[str]:
    content = path.read_text()
    return content.strip().splitlines()
