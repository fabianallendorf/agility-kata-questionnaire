import random
import tkinter as tk
from tkinter import ttk, messagebox

from src import strings
from src.dataclasses import Question, Answer, ValidatedQuestion, Score
from src.exceptions import UnansweredQuestionError
from src.questionnaire_validator import QuestionnaireValidator
from src.scorer import collect_statistics


class MainUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = None

    def display_questionnaire(self, questions):
        if self.page:
            self.page.destroy()
        self.page = QuestionnaireUI(questions=questions, master=self)
        self.page.display_questionnaire()

    def show_results(self, validated_questions: list[ValidatedQuestion]):
        if self.page:
            self.page.destroy()
        score = collect_statistics(validated_questions)
        self.page = ResultUI(
            validated_questions=validated_questions, score=score, master=self
        )
        self.page.display_results()


class GridUIMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid()
        self.current_row = 0

    def add_label(self, column=0, *args, **kwargs):
        element = ttk.Label(master=self, *args, **kwargs).grid(
            column=column, row=self.current_row
        )
        self.current_row += 1
        return element

    def add_button(self, column=0, *args, **kwargs):
        element = ttk.Button(master=self, *args, **kwargs).grid(
            column=column, row=self.current_row
        )
        self.current_row += 1
        return element

    def add_checkbox(self, column=0, *args, **kwargs):
        element = ttk.Checkbutton(master=self, *args, **kwargs).grid(
            column=column, row=self.current_row
        )
        self.current_row += 1
        return element

    def add_separator(self, column=0, *args, **kwargs):
        element = ttk.Separator(master=self, *args, **kwargs).grid(
            column=column, row=self.current_row
        )
        self.current_row += 1
        return element


class QuestionnaireUI(GridUIMixin, ttk.Frame):
    def __init__(self, questions: list[Question], master=None):
        super().__init__(master=master)
        self.grid()
        self._root().title(strings.TITLE)  # noqa
        self.questions = questions
        self.answer_selection_map = dict()

    def display_questionnaire(self):
        for question in self.questions:
            self._display_question_text(question)
            answers = self._shuffle_answers(question)
            for answer in answers:
                self._display_answer(answer)
        self._display_buttons()

    def _display_question_text(self, question):
        self.add_label(text="\n", column=1)
        self.add_label(text=question.text, column=1)

    @staticmethod
    def _shuffle_answers(question):
        answers = question.correct_answers + question.incorrect_answers
        random.shuffle(answers)
        return answers

    def _display_answer(self, answer):
        self.answer_selection_map[answer] = tk.IntVar()
        self.add_checkbox(
            text=answer.text, variable=self.answer_selection_map[answer], column=1
        )

    def _display_buttons(self):
        self.add_label(text="\n")
        ttk.Button(master=self, text=strings.SHOW_RESULTS, command=self.show_results).grid(column=0, row=self.current_row)
        self.add_button(text=strings.QUIT, command=self.quit, column=2)

    def show_results(self):
        selected_answers = self._collect_selected_answers()
        try:
            QuestionnaireValidator.check_all_questions_are_answered(
                self.questions, selected_answers
            )
        except UnansweredQuestionError:
            self._show_error()
        else:
            validated_questions = QuestionnaireValidator.validate_answers(
                self.questions, selected_answers
            )
            self.master.show_results(validated_questions)

    @staticmethod
    def _show_error():
        messagebox.showerror(
            strings.UNANSWERED_QUESTION_ERROR_TITLE,
            strings.UNANSWERED_QUESTION_ERROR_MESSAGE,
        )

    def _collect_selected_answers(self):
        selected_answers = []
        for answer, selection in self.answer_selection_map.items():
            is_selected = selection.get()
            if is_selected:
                selected_answers.append(answer)
        return selected_answers


class ResultUI(GridUIMixin, ttk.Frame):
    def __init__(
        self, validated_questions: list[ValidatedQuestion], score: Score, master=None
    ):
        super().__init__(master=master)
        self._root().title(strings.SHOW_RESULTS)  # noqa
        self.grid()
        self.validated_questions = validated_questions
        self.score = score

    def display_results(self):
        self._display_score()
        self.row_index += 1
        self._display_separator()
        self.row_index += 1
        for validated_question in self.validated_questions:
            question = validated_question.answered_question.question
            ttk.Label(master=self, text=question.text).grid(
                column=1, row=self.row_index
            )
            self.row_index += 1
            if validated_question.is_correct:
                self._display_correctly_answered(validated_question)
                self.row_index += 1
            else:
                self._display_incorrectly_answered(validated_question)
                self.row_index += 1
                self._display_correct_answer(question)
                self.row_index += 1
            self._display_separator()
            self.row_index += 1

    def _display_separator(self):
        separator = ttk.Separator(master=self, orient="horizontal")
        separator.grid(column=1, sticky="ew", pady=10)

    def _display_correctly_answered(self, validated_question: ValidatedQuestion):
        answer_text = ",".join(
            answer.text for answer in validated_question.answered_question.user_answers
        )
        ttk.Label(master=self, text=f"Your answer '{answer_text}' is correct").grid(
            column=1, row=self.row_index
        )

    def _display_incorrectly_answered(self, validated_question: ValidatedQuestion):
        answer_text = ",".join(
            answer.text for answer in validated_question.answered_question.user_answers
        )
        ttk.Label(master=self, text=f"Your answer '{answer_text}' is wrong").grid(
            column=1, row=self.row_index
        )

    def _display_correct_answer(self, question):
        correct_answer_text = ",".join(
            answer.text for answer in question.correct_answers
        )
        ttk.Label(
            master=self, text=f"The correct answer is '{correct_answer_text}'"
        ).grid(column=1, row=self.row_index)

    def _display_score(self):
        score_text = (
            f"{self.score.correct_questions_count} out of {self.score.questions_count} "
            f"questions answered correctly ({self.score.percentage_correct:.0%})"
        )
        self.add_label(master=self, text=score_text).grid(column=1, row=self.row_index)
