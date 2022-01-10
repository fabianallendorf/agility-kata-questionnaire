from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Answer:
    text: str
    id: UUID = field(default_factory=uuid4)


@dataclass(frozen=True)
class Question:
    text: str
    correct_answers: list[Answer]
    incorrect_answers: list[Answer]
    id: UUID = field(default_factory=uuid4)


@dataclass(frozen=True)
class AnsweredQuestion:
    question: Question
    user_answers: list[Answer]


@dataclass(frozen=True)
class ValidatedQuestion:
    answered_question: AnsweredQuestion
    is_correct: bool


@dataclass
class Score:
    questions_count: int
    correct_questions_count: int
    percentage_correct: float


@dataclass
class Questionnaire:
    name: str
    questions: list[Question]
