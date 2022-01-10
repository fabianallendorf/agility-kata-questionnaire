import pytest

from src.dataclasses import Answer, AnsweredQuestion, Question
from src.exceptions import UnansweredQuestionError
from src.questionnaire_validator import QuestionnaireValidator


class TestRaisesIfAnswersAreMissing:
    def test_detects_missing_question(self):
        first_correct_answer = Answer(text="0")
        first_question = Question(
            text="How many tests did Malte write",
            correct_answers=[first_correct_answer],
            incorrect_answers=[Answer(text="1"), Answer(text="too many")],
        )
        second_question = Question(
            text="How many lebkuchen did Fabian eat",
            correct_answers=[Answer(text="1")],
            incorrect_answers=[Answer(text="-1"), Answer(text="too many")],
        )

        with pytest.raises(UnansweredQuestionError) as exc:
            QuestionnaireValidator.check_all_questions_are_answered(
                questions=[first_question, second_question],
                selected_answers=[first_correct_answer],
            )
        assert exc.value.unanswered_question == second_question

    def test_raises_if_unkown_answeres_are_passed_in(self):
        some_random_answers = Answer(text="random")
        first_question = Question(
            text="How many tests did Malte write",
            correct_answers=[Answer(text="0")],
            incorrect_answers=[Answer(text="1"), Answer(text="too many")],
        )

        with pytest.raises(UnansweredQuestionError):
            QuestionnaireValidator.check_all_questions_are_answered(
                questions=[first_question],
                selected_answers=[some_random_answers],
            )


class TestAllAnswersAreGiven:
    def test_no_questions(self):
        QuestionnaireValidator.check_all_questions_are_answered(
            questions=[], selected_answers=[]
        )

    def test_does_not_raise_if_all_question_are_answered(self):
        incorrect_answer = Answer(text="1")
        first_question = Question(
            text="How many tests did Malte write",
            correct_answers=[Answer(text="0")],
            incorrect_answers=[incorrect_answer, Answer(text="too many")],
        )

        QuestionnaireValidator.check_all_questions_are_answered(
            questions=[first_question],
            selected_answers=[incorrect_answer],
        )


class TestSelectAnswersForQuestion:
    def test_returns_correct_answered_question(self):
        correct_answer = Answer(text="oranges that are hard to peel")
        other_answer = Answer(text="42")
        question = Question(
            text="What is Maltes current Nemesis?",
            correct_answers=[correct_answer],
            incorrect_answers=[],
        )

        answered_question = QuestionnaireValidator.select_answers_for_question(
            question=question, user_answers=[correct_answer, other_answer]
        )

        assert answered_question.question == question
        assert answered_question.user_answers == [correct_answer]


class TestCheckIsAnsweredCorrectly:
    def test_answer_is_correct(self):
        correct_answer = Answer(text="oranges that are hard to peel")
        question = Question(
            text="What is Maltes current Nemesis?",
            correct_answers=[correct_answer],
            incorrect_answers=[Answer(text="Fabian")],
        )
        answered_question = AnsweredQuestion(
            question=question, user_answers=[correct_answer]
        )

        validated_question = QuestionnaireValidator.check_is_answered_correctly(
            answered_question=answered_question
        )

        assert validated_question.is_correct is True

    def test_answer_is_incorrect(self):
        incorrect_answer = Answer(text="Fabian")
        question = Question(
            text="What is Maltes current Nemesis?",
            correct_answers=[Answer(text="oranges that are hard to peel")],
            incorrect_answers=[incorrect_answer],
        )
        answered_question = AnsweredQuestion(
            question=question, user_answers=[incorrect_answer]
        )

        validated_question = QuestionnaireValidator.check_is_answered_correctly(
            answered_question=answered_question
        )

        assert validated_question.is_correct is False

    def test_did_not_answer(self):
        question = Question(
            text="What is Maltes current Nemesis?",
            correct_answers=[Answer(text="oranges that are hard to peel")],
            incorrect_answers=[Answer(text="Fabian")],
        )
        answered_question = AnsweredQuestion(question=question, user_answers=[])

        validated_question = QuestionnaireValidator.check_is_answered_correctly(
            answered_question=answered_question
        )

        assert validated_question.is_correct is False

    def test_answer_is_partly_correct(self):
        one_correct_answer = Answer(text="Malte")
        question = Question(
            text="Who is working on this kata?",
            correct_answers=[one_correct_answer, Answer(text="Fabian")],
            incorrect_answers=[Answer(text="Matt")],
        )
        answered_question = AnsweredQuestion(
            question=question, user_answers=[one_correct_answer]
        )

        validated_question = QuestionnaireValidator.check_is_answered_correctly(
            answered_question=answered_question
        )

        assert validated_question.is_correct is False
