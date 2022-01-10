import random
import tkinter as tk
from functools import partial
from tkinter import messagebox, ttk

from src import strings
from src.dataclasses import Questionnaire, Score, ValidatedQuestion
from src.exceptions import UnansweredQuestionError
from src.questionnaire_validator import QuestionnaireValidator
from src.scorer import collect_statistics


class GridUIMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid()  # noqa
        self.current_row = 0

    def add_label(self, column=0, *args, **kwargs):
        element = ttk.Label(master=self, *args, **kwargs).grid(  # noqa
            column=column, row=self.current_row
        )
        self.current_row += 1
        return element

    def add_menu_button(self, column=0, *args, **kwargs):
        element = ttk.Button(master=self, *args, **kwargs).grid(  # noqa
            column=column, row=self.current_row
        )
        self.current_row += 1
        return element

    def add_checkbox(self, column=0, *args, **kwargs):
        element = ttk.Checkbutton(master=self, *args, **kwargs).grid(  # noqa
            column=column, row=self.current_row
        )
        self.current_row += 1
        return element

    def add_radiobutton(self, column=0, *args, **kwargs):
        element = ttk.Radiobutton(master=self, *args, **kwargs).grid(  # noqa
            column=column, row=self.current_row
        )
        self.current_row += 1
        return element

    def add_separator(self, column=0, orient="horizontal", *args, **kwargs):
        ttk.Separator(
            master=self, orient=orient, *args, **kwargs  # noqa
        ).grid(
            column=column, row=self.current_row, sticky="ew", pady=10
        )
        self.current_row += 1


class MainUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = None

    def display_questionnaire_selection(self, questionnaires: list[Questionnaire]):
        if self.page:
            self.page.destroy()
        self.page = SelectionUI(questionnaires, master=self)
        self.page.display_questionnaire_selection()

    def display_questionnaire(self, questionnaire: Questionnaire):
        if self.page:
            self.page.destroy()
        self.page = QuestionnaireUI(questionnaire=questionnaire, master=self)
        self.page.display_questionnaire()

    def show_results(self, validated_questions: list[ValidatedQuestion]):
        if self.page:
            self.page.destroy()
        score = collect_statistics(validated_questions)
        self.page = ResultUI(
            validated_questions=validated_questions, score=score, master=self
        )
        self.page.display_results()


class SelectionUI(GridUIMixin, ttk.Frame):
    def __init__(self, questionnaires: list[Questionnaire], master=None):
        super().__init__(master=master)
        self._root().title(strings.QUESTIONNAIRE_SELECTION_TITLE)  # noqa
        self.grid()
        self.questionnaires = questionnaires
        self.questionnaire_selection = tk.StringVar()

    def display_questionnaire_selection(self):
        self._display_intro_text()
        for questionnaire in self.questionnaires:
            self._display_questionnaire_information(questionnaire)
        self._display_buttons()

    def _display_intro_text(self):
        self.add_label(text=strings.QUESTIONNAIRE_SELECTION_INFO)

    def _display_questionnaire_information(self, questionnaire: Questionnaire):
        self.add_separator()
        self.add_radiobutton(
            text=questionnaire.name,
            variable=self.questionnaire_selection,
            value=questionnaire.name,
        )

    def _display_buttons(self):
        self.add_separator()
        self.add_menu_button(
            text=strings.SELECT_QUESTIONNAIRE,
            command=self._select_questionnaire,
        )
        self.add_menu_button(text=strings.QUIT, command=self.quit)

    def _select_questionnaire(self):
        selection = self.questionnaire_selection.get()
        if not selection:
            return
        questionnaire = self._get_selected_questionnaire(selection)
        self.master.display_questionnaire(questionnaire)  # noqa

    def _get_selected_questionnaire(self, selection: str):
        return [
            questionnaire
            for questionnaire in self.questionnaires
            if questionnaire.name == selection
        ][0]


class QuestionnaireUI(GridUIMixin, ttk.Frame):
    def __init__(self, questionnaire: Questionnaire, master=None):
        super().__init__(master=master)
        self.grid()
        self._root().title(strings.QUESTIONNAIRE_TITLE)  # noqa
        self.questionnaire = questionnaire
        self.answer_selection_map = dict()

    def display_questionnaire(self):
        self._display_intro_text()
        for question in self.questionnaire.questions:
            self._display_question_text(question)
            answers = self._shuffle_answers(question)
            for answer in answers:
                self._display_answer(answer)
        self._display_buttons()

    def _display_intro_text(self):
        self.add_label(text=strings.QUESTIONNAIRE_INFO)

    def _display_question_text(self, question):
        self.add_separator()
        self.add_label(text=question.text)

    @staticmethod
    def _shuffle_answers(question):
        answers = question.correct_answers + question.incorrect_answers
        random.shuffle(answers)
        return answers

    def _display_answer(self, answer):
        self.answer_selection_map[answer] = tk.IntVar()
        self.add_checkbox(text=answer.text, variable=self.answer_selection_map[answer])

    def _display_buttons(self):
        self.add_separator()
        self.add_menu_button(text=strings.SHOW_RESULTS, command=self.show_results)
        self.add_menu_button(text=strings.QUIT, command=self.quit)

    def show_results(self):
        questions = self.questionnaire.questions
        selected_answers = self._collect_selected_answers()
        try:
            QuestionnaireValidator.check_all_questions_are_answered(
                questions, selected_answers
            )
        except UnansweredQuestionError:
            self._show_error()
        else:
            validated_questions = QuestionnaireValidator.validate_answers(
                questions, selected_answers
            )
            self.master.show_results(validated_questions)  # noqa

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
        self._root().title(strings.RESULT_TITLE)  # noqa
        self.grid()
        self.validated_questions = validated_questions
        self.score = score

    def display_results(self):
        self._display_score()

        for validated_question in self.validated_questions:
            question = validated_question.answered_question.question
            self.add_separator()
            self.add_label(text=question.text)
            if validated_question.is_correct:
                self._display_correctly_answered(validated_question)
            else:
                self._display_incorrectly_answered(validated_question)
                self._display_correct_answer(question)
        self._display_buttons()

    def _display_correctly_answered(self, validated_question: ValidatedQuestion):
        answer_text = ", ".join(
            answer.text for answer in validated_question.answered_question.user_answers
        )
        self.add_label(text=strings.correctly_answered(answer_text))

    def _display_incorrectly_answered(self, validated_question: ValidatedQuestion):
        answer_text = ", ".join(
            answer.text for answer in validated_question.answered_question.user_answers
        )
        self.add_label(text=strings.incorrectly_answered(answer_text))

    def _display_correct_answer(self, question):
        correct_answer_text = ", ".join(
            answer.text for answer in question.correct_answers
        )
        self.add_label(text=strings.corrected_answer(correct_answer_text))

    def _display_score(self):
        score_text = strings.score_text(
            self.score.correct_questions_count,
            self.score.questions_count,
            self.score.percentage_correct,
        )
        self.add_label(text=score_text)

    def _display_buttons(self):
        self.add_separator()
        self.add_menu_button(text=strings.QUIT, command=self.quit)
