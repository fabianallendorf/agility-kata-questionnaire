SHOW_RESULTS = "Be hopeful"
QUIT = "Abandon hope"
SELECT_QUESTIONNAIRE = "Choose hope"
DONT_KNOW = "I am hopeless"

UNANSWERED_QUESTION_ERROR_TITLE = "Missing answer"
UNANSWERED_QUESTION_ERROR_MESSAGE = "Some questions were not answered."

QUESTIONNAIRE_SELECTION_TITLE = "Questionnaire selection"
QUESTIONNAIRE_SELECTION_INFO = "Please choose a questionnaire from the following list:"

QUESTIONNAIRE_TITLE = "Questionnaire"
QUESTIONNAIRE_INFO = "Please answer the following questions:"

RESULT_TITLE = "Results"


def correctly_answered(answer_text: str) -> str:
    return f"Your answer is correct: '{answer_text}'"


def incorrectly_answered(answer_text: str) -> str:
    return f"Your answer is incorrect: '{answer_text}'"


def corrected_answer(answer_text: str) -> str:
    return f"The correct answer is: '{answer_text}'"


def score_text(
    correct_count: int, questions_count: int, percentage_correct: float
) -> str:
    return (
        f"{correct_count} out of {questions_count} "
        f"questions answered correctly ({percentage_correct:.0%})"
    )
