import os
from pathlib import Path

from src.file_reader import read_files
from src.questionnaire_parser import QuestionnaireParser
from src.ui import MainUI


def main():
    directory_path = Path(os.path.join(os.path.dirname(__file__), "test/files/"))
    file_dict = read_files(directory_path)

    questionnaires = QuestionnaireParser.parse_questionnaires(file_dict)

    ui = MainUI()
    ui.display_questionnaire_selection(questionnaires)
    ui.mainloop()


if __name__ == "__main__":
    main()
