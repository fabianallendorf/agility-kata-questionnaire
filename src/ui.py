import random
import tkinter as tk
from functools import partial
from tkinter import ttk, messagebox

from src import strings
from src.dataclasses import Question, Answer
from src.exceptions import UnansweredQuestionError
from src.questionnaire_validator import QuestionnaireValidator


class QuestionnaireUI(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.grid()
        self._root().title(strings.TITLE)  # noqa
        self.answer_selection_map = dict()
        self.current_row = 0

    def display_questionnaire(self, questions: list[Question]):
        for question in questions:
            self._display_question_text(question)
            answers = self._shuffle_answers(question)
            for answer in answers:
                self._display_answer(answer)
        self._display_buttons(questions)

    def _display_question_text(self, question):
        ttk.Label(master=self, text="\n").grid(column=1, row=self.current_row)
        self.current_row += 1
        ttk.Label(master=self, text=question.text).grid(column=1, row=self.current_row)
        self.current_row += 1

    @staticmethod
    def _shuffle_answers(question):
        answers = question.correct_answers + question.incorrect_answers
        random.shuffle(answers)
        return answers

    def _display_answer(self, answer):
        self.answer_selection_map[answer] = tk.IntVar()
        ttk.Checkbutton(
            master=self, text=answer.text, variable=self.answer_selection_map[answer],
        ).grid(column=1, row=self.current_row)
        self.current_row += 1

    def _display_buttons(self, questions):
        ttk.Label(master=self, text="\n").grid(column=1, row=self.current_row)
        self.current_row += 1
        ttk.Button(
            master=self,
            text=strings.SHOW_RESULTS,
            command=partial(self.show_results, questions),
        ).grid(column=0, row=self.current_row)
        ttk.Button(master=self, text=strings.QUIT, command=self.quit).grid(
            column=2, row=self.current_row
        )  # self.destroy ?
        self.current_row += 1

    def show_results(self, questions: list[Question]):
        selected_answers = self._collect_selected_answers()
        self._check_all_questions_are_answered(questions, selected_answers)

        # validator.validate_answers(questions, selected_answers)
        print(selected_answers, questions)

    @staticmethod
    def _check_all_questions_are_answered(
        questions: list[Question], selected_answers: list[Answer]
    ):
        try:
            QuestionnaireValidator.check_all_questions_are_answered(
                questions, selected_answers
            )
        except UnansweredQuestionError:
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
