from itertools import chain

from src.dataclasses import Question, Answer, AnsweredQuestion, ValidatedQuestion
from src.exceptions import UnansweredQuestionError


class QuestionnaireValidator:
    @staticmethod
    def check_all_questions_are_answered(
        questions: list[Question], selected_answers: list[Answer]
    ):
        for question in questions:
            possible_answers = chain(
                question.correct_answers, question.incorrect_answers
            )
            select_answers_for_question = set(selected_answers) & set(possible_answers)
            if len(select_answers_for_question) == 0:
                raise UnansweredQuestionError(unanswered_question=question)

    @staticmethod
    def validate_answers(questions: list[Question], user_answers: list[Answer]) -> list[ValidatedQuestion]:
        validated_questions = []
        for question in questions:
            validated_question = QuestionnaireValidator.validate_answer(question, user_answers)
            validated_questions.append(validated_question)

        return validated_questions

    @staticmethod
    def validate_answer(question: Question, user_answers: list[Answer]):
        answered_question = QuestionnaireValidator.select_answers_for_question(question, user_answers)
        validated_answer = QuestionnaireValidator.check_is_answered_correctly(answered_question)
        return validated_answer

    @staticmethod
    def select_answers_for_question(
        question: Question, user_answers: list[Answer]
    ) -> AnsweredQuestion:
        user_answers = [
            answer
            for answer in user_answers
            if answer in chain(question.correct_answers, question.incorrect_answers)
        ]
        return AnsweredQuestion(question=question, user_answers=user_answers)

    @staticmethod
    def check_is_answered_correctly(
        answered_question: AnsweredQuestion,
    ) -> ValidatedQuestion:
        is_correct = set(answered_question.question.correct_answers) == set(
            answered_question.user_answers
        )
        return ValidatedQuestion(
            answered_question=answered_question, is_correct=is_correct
        )
