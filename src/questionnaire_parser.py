from src.dataclasses import Question, Answer
from src.exceptions import (
    NotAnAnswerError,
    NotAQuestionError,
    NotExactlyOneCorrectAnswerError,
)


class QuestionnaireParser:
    def __init__(self):
        self.current_line_index = 0
        self.max_line_index = 0

    def parse_questionnaire(self, questionnaire_lines: list[str]) -> list[Question]:
        questions = []
        self.current_line_index = 0
        self.max_line_index = len(questionnaire_lines)
        while self.current_line_index < self.max_line_index:
            question = self.parse_question(questionnaire_lines)
            questions.append(question)
        return questions

    def parse_question(
        self,
        questionnaire_lines: list[str],
    ) -> Question:
        parsed_lines_count, question_text = self.read_question_text(questionnaire_lines)
        self.current_line_index += parsed_lines_count
        parsed_answers = []
        while self.current_line_index < self.max_line_index:
            try:
                (
                    parsed_lines_count,
                    answer,
                    is_correct_for_current_question,
                ) = self.parse_answer(questionnaire_lines)
            except NotAnAnswerError:
                break
            self.current_line_index += parsed_lines_count
            parsed_answers.append((answer, is_correct_for_current_question))
        question = self.build_question(question_text, parsed_answers)
        return question

    def read_question_text(
        self,
        questionnaire_lines: list[str],
    ) -> tuple[int, str]:
        txt = questionnaire_lines[self.current_line_index]
        if not self._is_question(txt):
            raise NotAQuestionError
        txt = txt[1:]
        return 1, txt

    def parse_answer(
        self,
        questionnaire_lines: list[str],
    ) -> tuple[int, Answer, bool]:
        txt = questionnaire_lines[self.current_line_index]
        if self._is_question(txt):
            raise NotAnAnswerError
        is_correct = self._is_correct(txt)
        if is_correct:
            txt = txt[1:]
        return 1, Answer(text=txt), is_correct

    @staticmethod
    def _is_question(txt: str) -> bool:
        return txt.startswith("?")

    @staticmethod
    def _is_correct(txt: str) -> bool:
        return txt.startswith("*")

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
        if len(correct_answers) != 1:
            raise NotExactlyOneCorrectAnswerError
        return Question(
            text=question_text,
            correct_answers=correct_answers,
            incorrect_answers=incorrect_answers,
        )
