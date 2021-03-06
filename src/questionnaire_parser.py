from src.dataclasses import Question, Answer
from src.exceptions import (
    NotAnAnswerError,
    NotAQuestionError,
    NotExactlyOneCorrectAnswerError,
)
from src import markers, strings


class QuestionnaireParser:
    @classmethod
    def parse_questionnaire(cls, questionnaire_lines: list[str]) -> list[Question]:
        current_line_index = 0
        questions = []
        while True:
            try:
                current_line_index, question = cls.parse_question(
                    questionnaire_lines,
                    current_line_index,
                )
            except IndexError:
                break
            questions.append(question)
        return questions

    @classmethod
    def parse_question(
        cls,
        questionnaire_lines: list[str],
        current_line_index: int,
    ) -> tuple[int, Question]:
        current_line_index, question_text = cls.read_question_text(
            questionnaire_lines, current_line_index
        )
        parsed_answers = []
        while True:
            try:
                (
                    current_line_index,
                    answer,
                    is_correct_for_current_question,
                ) = cls.parse_answer(questionnaire_lines, current_line_index)
            except (NotAnAnswerError, IndexError):
                break
            parsed_answers.append((answer, is_correct_for_current_question))
        question = cls.build_question(question_text, parsed_answers)
        return current_line_index, question

    @classmethod
    def read_question_text(
        cls, questionnaire_lines: list[str], current_line_index: int
    ) -> tuple[int, str]:
        txt = questionnaire_lines[current_line_index]
        if not cls._is_question(txt):
            raise NotAQuestionError
        txt = txt[1:]
        current_line_index += 1
        return current_line_index, txt

    @classmethod
    def parse_answer(
        cls, questionnaire_lines: list[str], current_line_index: int
    ) -> tuple[int, Answer, bool]:
        txt = questionnaire_lines[current_line_index]
        if cls._is_question(txt):
            raise NotAnAnswerError
        is_correct_for_current_question = cls._is_correct(txt)
        if is_correct_for_current_question:
            txt = txt[1:]
        current_line_index += 1
        return current_line_index, Answer(text=txt), is_correct_for_current_question

    @staticmethod
    def build_question(
        question_text: str, parsed_answers: list[tuple[Answer, bool]]
    ) -> Question:
        correct_answers = [
            answer
            for answer, is_correct_for_current_question in parsed_answers
            if is_correct_for_current_question
        ]
        incorrect_answers = [
            answer
            for answer, is_correct_for_current_question in parsed_answers
            if not is_correct_for_current_question
        ]
        incorrect_answers.append(Answer(text=strings.DONT_KNOW))
        if len(correct_answers) != 1:
            raise NotExactlyOneCorrectAnswerError
        return Question(
            text=question_text,
            correct_answers=correct_answers,
            incorrect_answers=incorrect_answers,
        )

    @staticmethod
    def _is_question(txt: str) -> bool:
        return txt.startswith(markers.QUESTION_MARKER)

    @staticmethod
    def _is_correct(txt: str) -> bool:
        return txt.startswith(markers.CORRECT_ANSWER_MARKER)
