from src.dataclasses import ValidatedQuestion, Score


def collect_statistics(validated_questions: list[ValidatedQuestion]) -> Score:
    questions_count = len(validated_questions)
    correct_questions = [q for q in validated_questions if q.is_correct]
    correct_questions_count = len(correct_questions)
    percentage_correct = len(correct_questions) / len(validated_questions)
    return Score(
        questions_count=questions_count,
        correct_questions_count=correct_questions_count,
        percentage_correct=percentage_correct,
    )
