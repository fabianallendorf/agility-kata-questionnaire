from src.file_reader import read_file
import test.files
from importlib import resources


def test_read_empty_file():
    with resources.path(test.files, test.files.EMPTY) as path:
        lines = read_file(path)
    assert lines == []


def test_read_file_with_content():
    with resources.path(test.files, test.files.WITH_CONTENT) as path:
        lines = read_file(path)
    assert lines == ["?question1", "answer", "*correct_answer"]


def test_read_file_with_many_blank_lines():
    with resources.path(test.files, test.files.WITH_BLANK_LINES) as path:
        lines = read_file(path)
    assert lines == ["line"]
