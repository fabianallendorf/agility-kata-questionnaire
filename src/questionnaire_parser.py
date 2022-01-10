from src import markers
from src.dataclasses import Answer, Question, Questionnaire
from src.exceptions import NoCorrectAnswerError, NotAnAnswerError, NotAQuestionError


class QuestionnaireParser:
    @classmethod
    def parse_questionnaires(
        cls, file_dict: dict[str, list[str]]
    ) -> list[Questionnaire]:
        questionnaires = []
        for name, lines in file_dict.items():
            questionnaire = QuestionnaireParser.parse_questionnaire(
                questionnaire_name=name, questionnaire_lines=lines
            )
            if len(questionnaire.questions) == 0:
                continue
            questionnaires.append(questionnaire)
        return questionnaires

    @classmethod
    def parse_questionnaire(
        cls, questionnaire_name: str, questionnaire_lines: list[str]
    ) -> Questionnaire:
        current_line_index = 0
        questions = []
        while True:
            try:
                current_line_index, question = cls.parse_question(
                    questionnaire_lines,
                    current_line_index,
                )
            except (NotAQuestionError, IndexError):
                break
            questions.append(question)
        return Questionnaire(questions=questions, name=questionnaire_name)

    @classmethod
    def parse_question(
        cls,
        questionnaire_lines: list[str],
        current_line_index: int,
    ) -> tuple[int, Question]:
        current_line_index, question_text, is_required = cls.read_question_text(
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
        question = cls.build_question(question_text, is_required, parsed_answers)
        return current_line_index, question

    @classmethod
    def read_question_text(
        cls, questionnaire_lines: list[str], current_line_index: int
    ) -> tuple[int, str, bool]:
        txt = questionnaire_lines[current_line_index]
        if not cls._is_question(txt):
            raise NotAQuestionError
        if cls._is_required(txt):
            is_required = True
            txt = txt[2:]
        else:
            is_required = False
            txt = txt[1:]
        current_line_index += 1
        return current_line_index, txt, is_required

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
        question_text: str, is_required: bool, parsed_answers: list[tuple[Answer, bool]]
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
        if len(correct_answers) < 1:
            raise NoCorrectAnswerError
        return Question(
            text=question_text,
            required=is_required,
            correct_answers=correct_answers,
            incorrect_answers=incorrect_answers,
        )

    @staticmethod
    def _is_question(txt: str) -> bool:
        return txt.startswith(markers.QUESTION_MARKER)

    @staticmethod
    def _is_correct(txt: str) -> bool:
        return txt.startswith(markers.CORRECT_ANSWER_MARKER)

    @staticmethod
    def _is_required(txt: str) -> bool:
        return txt.startswith(markers.REQUIRED_QUESTION_MARKER)
