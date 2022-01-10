from src.file_reader import read_file
from src.questionnaire_parser import QuestionnaireParser


def main():
    questionnaire_lines = read_file()
    QuestionnaireParser.parse_questionnaire(questionnaire_lines=questionnaire_lines)
