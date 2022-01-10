import pytest

from src.dataclasses import Answer
from src.exceptions import (
    NotAQuestionError,
    NotAnAnswerError,
    NoCorrectAnswerError,
)
from src.questionnaire_parser import QuestionnaireParser


@pytest.fixture
def questionnaire_lines():
    return [
        "?question1",
        "answer",
        "*correct_answer",
        "?question2",
        "answer",
        "*correct_answer",
        "other_answer",
        "?question3",
        "answer",
        "other_answer",
        "*correct_answer",
        "?question4",
        "*correct_answer",
    ]


class TestQuestionnaireParser:
    def test_parse_questionnaire_parses_all_questions(self, questionnaire_lines):
        questionnaire = QuestionnaireParser.parse_questionnaire(
            questionnaire_name="test_name",
            questionnaire_lines=questionnaire_lines
        )

        assert len(questionnaire.questions) == 4

    def test_parse_question_parses_multiple_answers(
        self,
        questionnaire_lines,
    ):
        _, question = QuestionnaireParser.parse_question(
            questionnaire_lines=questionnaire_lines,
            current_line_index=7,
        )

        assert len(question.correct_answers) == 1
        assert len(question.incorrect_answers) == 2

    def test_read_question_text_errors_if_not_a_question(
        self,
        questionnaire_lines,
    ):
        with pytest.raises(NotAQuestionError):
            QuestionnaireParser.read_question_text(
                questionnaire_lines=questionnaire_lines, current_line_index=6
            )

    def test_read_question_text_returns_correct_text(self, questionnaire_lines):
        _, question_text = QuestionnaireParser.read_question_text(
            questionnaire_lines=questionnaire_lines, current_line_index=0
        )

        assert question_text == "question1"

    def test_parse_answer_errors_if_not_an_answer(self, questionnaire_lines):
        with pytest.raises(NotAnAnswerError):
            QuestionnaireParser.parse_answer(
                questionnaire_lines=questionnaire_lines, current_line_index=0
            )

    def test_parse_answer_returns_correct_answer(
        self,
        questionnaire_lines,
    ):
        _, answer, is_correct_for_current_question = QuestionnaireParser.parse_answer(
            questionnaire_lines=questionnaire_lines, current_line_index=6
        )

        assert answer.text == "other_answer"
        assert not is_correct_for_current_question

    def test_build_question_errors_if_no_correct_answer(self, questionnaire_lines):
        parsed_answers = [
            (Answer(text="answer"), False),
        ]

        with pytest.raises(NoCorrectAnswerError):
            QuestionnaireParser.build_question(
                "question_text", parsed_answers=parsed_answers
            )

    def test_build_question_accepts_multiple_correct_answers(self, questionnaire_lines):
        parsed_answers = [
            (Answer(text="correct_answer"), True),
            (Answer(text="other_correct_answer"), True),
        ]

        question = QuestionnaireParser.build_question(
            "question_text", parsed_answers=parsed_answers
        )
        assert len(question.correct_answers) == 2

    def test_build_question_returns_complete_question(self, questionnaire_lines):
        parsed_answers = [
            (Answer(text="correct_answer"), True),
            (Answer(text="answer"), False),
            (Answer(text="other_answer"), False),
        ]

        question = QuestionnaireParser.build_question(
            "question_text", parsed_answers=parsed_answers
        )

        assert question.text == "question_text"
        assert question.correct_answers == [
            answer for answer, is_correct in parsed_answers if is_correct
        ]
        assert question.incorrect_answers == [
            answer for answer, is_correct in parsed_answers if not is_correct
        ]
