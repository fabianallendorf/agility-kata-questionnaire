import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def read_file(path: Path) -> list[str]:
    content = path.read_text()
    return content.strip().splitlines()


def read_files(directory_path: Path) -> dict[str, list[str]]:
    filename_content_dict = {}
    for file in os.listdir(directory_path):
        file_name, extension = os.path.splitext(file)
        if extension == ".txt":
            file_path = Path(os.path.join(directory_path, file))
            filename_content_dict[file_name] = read_file(file_path)
            logger.warning(f"{file_name} read in")
    return filename_content_dict
