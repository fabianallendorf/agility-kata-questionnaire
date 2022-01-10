from src.dataclasses import Question


class UnansweredQuestionError(Exception):
    def __init__(self, unanswered_question: Question):
        self.unanswered_question = unanswered_question


class NotAnAnswerError(Exception):
    pass


class NotAQuestionError(Exception):
    pass


class NoCorrectAnswerError(Exception):
    pass
