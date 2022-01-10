import os
from pathlib import Path

from src.file_reader import read_files
from src.ui import MainUI


def main():
    directory_path = Path(os.path.join(os.path.dirname(__file__), "test/files/"))
    questionnaire_dict = read_files(directory_path)

    ui = MainUI()
    ui.display_questionnaire_selection(questionnaire_dict)
    ui.mainloop()


if __name__ == "__main__":
    main()
