from importlib import resources

import test.files
from src.file_reader import read_file
from src.questionnaire_parser import QuestionnaireParser
from src.ui import QuestionnaireUI


def main():
    with resources.path(test.files, test.files.WITH_MULTIPLE_QUESTIONS) as path:
        questionnaire_lines = read_file(path)

    parser = QuestionnaireParser()
    questions = parser.parse_questionnaire(questionnaire_lines=questionnaire_lines)

    ui = QuestionnaireUI()
    ui.display_questionnaire(questions)
    ui.mainloop()


if __name__ == "__main__":
    main()
