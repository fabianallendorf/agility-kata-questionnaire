from importlib import resources
from src.file_reader import read_file
import test.files
from src.questionnaire_parser import QuestionnaireParser


class TestQuestionnaireParser:
    def test_parse_questionnaire_parses_all_questions(self):
        with resources.path(test.files, test.files.WITH_MULTIPLE_QUESTIONS) as path:
            lines = read_file(path)

        parser = QuestionnaireParser()
        questions = parser.parse_questionnaire(questionnaire_lines=lines)

        assert len(questions) == 4

    def test_parse_question_parses_multiple_answers(self):
        with resources.path(test.files, test.files.WITH_MULTIPLE_QUESTIONS) as path:
            lines = read_file(path)

        parser = QuestionnaireParser()
        parser.current_line_index = 7
        parser.max_line_index = 11

        question = parser.parse_question(questionnaire_lines=lines)

        assert len(question.correct_answers) == 1
        assert len(question.incorrect_answers) == 2
