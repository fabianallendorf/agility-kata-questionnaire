import random
import tkinter as tk
from functools import partial
from tkinter import ttk, messagebox

from src import strings
from src.dataclasses import Question, ValidatedQuestion, Score, Questionnaire
from src.exceptions import UnansweredQuestionError
from src.questionnaire_validator import QuestionnaireValidator
from src.scorer import collect_statistics


class MainUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = None

    def display_questionnaire_selection(self, questionnaires: list[Questionnaire]):
        if self.page:
            self.page.destroy()
        self.page = SelectionUI(questionnaires, master=self)
        self.page.display_questionnaire_selection()

    def display_questionnaire(self, questions: list[Question]):
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


class SelectionUI(ttk.Frame):
    def __init__(self, questionnaires: list[Questionnaire], master=None):
        super().__init__(master=master)
        self._root().title(strings.SHOW_RESULTS)  # noqa
        self.grid()
        self.current_row = 0
        self.questionnaires = questionnaires
        self.questionnaire_selection = tk.StringVar()

    def display_questionnaire_selection(self):
        for questionnaire in self.questionnaires:
            self._display_questionnaire_information(questionnaire)
        self._display_buttons()

    def _display_questionnaire_information(self, questionnaire: Questionnaire):
        ttk.Label(master=self, text="\n").grid(column=1, row=self.current_row)
        self.current_row += 1
        ttk.Radiobutton(
            master=self,
            text=questionnaire.name,
            variable=self.questionnaire_selection,
            value=questionnaire.name
        ).grid(column=1, row=self.current_row)
        self.current_row += 1

    def _display_buttons(self):
        ttk.Label(master=self, text="\n").grid(column=1, row=self.current_row)
        self.current_row += 1
        ttk.Button(
            master=self,
            text=strings.SELECT_QUESTIONNAIRE,
            command=self._select_questionnaire,
        ).grid(column=0, row=self.current_row)
        ttk.Button(master=self, text=strings.QUIT, command=self.quit).grid(
            column=2, row=self.current_row
        )
        self.current_row += 1

    def _select_questionnaire(self):
        selection = self.questionnaire_selection.get()
        if not selection:
            return
        questionnaire = [questionnaire for questionnaire in self.questionnaires if questionnaire.name == selection][0]
        self.master.display_questionnaire(questionnaire.questions)

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
            column=column, row=self.current_row, sticky="ew", pady=10
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
        ttk.Button(
            master=self, text=strings.SHOW_RESULTS, command=self.show_results
        ).grid(column=0, row=self.current_row)
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
        self._display_separator()
        for validated_question in self.validated_questions:
            question = validated_question.answered_question.question
            self.add_label(text=question.text, column=1)
            if validated_question.is_correct:
                self._display_correctly_answered(validated_question)
            else:
                self._display_incorrectly_answered(validated_question)
                self._display_correct_answer(question)
            self._display_separator()
        self._display_buttons()

    def _display_separator(self):
        self.add_separator(orient="horizontal", column=1)

    def _display_correctly_answered(self, validated_question: ValidatedQuestion):
        answer_text = ",".join(
            answer.text for answer in validated_question.answered_question.user_answers
        )
        self.add_label(text=f"Your answer '{answer_text}' is correct", column=1)

    def _display_incorrectly_answered(self, validated_question: ValidatedQuestion):
        answer_text = ",".join(
            answer.text for answer in validated_question.answered_question.user_answers
        )
        self.add_label(text=f"Your answer '{answer_text}' is wrong", column=1)

    def _display_correct_answer(self, question):
        correct_answer_text = ",".join(
            answer.text for answer in question.correct_answers
        )
        self.add_label(text=f"The correct answer is '{correct_answer_text}'", column=1)

    def _display_score(self):
        score_text = (
            f"{self.score.correct_questions_count} out of {self.score.questions_count} "
            f"questions answered correctly ({self.score.percentage_correct:.0%})"
        )
        self.add_label(text=score_text, column=1)

    def _display_buttons(self):
        button_frame = ttk.Frame(master=self)
        button_frame.grid(column=1, row=self.current_row)
        questions = [q.answered_question.question for q in self.validated_questions]
        ttk.Button(master=button_frame, text="A new hope", command=partial(self.master.display_questionnaire, questions)).grid(column=0, row=0)
        ttk.Button(master=button_frame, text="Abandon hope", command=self.quit).grid(column=1, row=0)
