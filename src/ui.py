import random
import tkinter as tk
from functools import partial
from tkinter import ttk, messagebox

from src import ui_strings
from src.dataclasses import Question, Answer
from src.exceptions import UnansweredQuestionError
from src.questionnaire_validator import QuestionnaireValidator


class QuestionnaireUI(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.grid()
        self._root().title(ui_strings.TITLE)  # noqa
        self.check_vars = dict()

    def display_questionnaire(self, questions: list[Question]):
        row = 0
        for question in questions:
            ttk.Label(master=self, text="\n").grid(column=1, row=row)
            row += 1
            ttk.Label(master=self, text=question.text).grid(column=1, row=row)
            row += 1
            answers = question.correct_answers + question.incorrect_answers
            random.shuffle(answers)
            for answer in answers:
                self.check_vars[answer] = tk.IntVar()
                ttk.Checkbutton(
                    master=self, text=answer.text, variable=self.check_vars[answer]
                ).grid(column=1, row=row)
                row += 1
        ttk.Label(master=self, text="\n").grid(column=1, row=row)
        row += 1
        ttk.Button(
            master=self,
            text=ui_strings.SHOW_RESULTS,
            command=partial(self.show_results, questions),
        ).grid(column=0, row=row)
        ttk.Button(master=self, text=ui_strings.QUIT, command=self.quit).grid(
            column=2, row=row
        )  # self.destroy ?

    def show_results(self, questions: list[Question]):
        selected_answers = self._collect_selected_answers()
        self._check_all_questions_are_answered(questions, selected_answers)

        # validator.validate_answers(questions, selected_answers)
        print(selected_answers, questions)

    @staticmethod
    def _check_all_questions_are_answered(questions: list[Question], selected_answers: list[Answer]):
        try:
            QuestionnaireValidator.check_all_questions_are_answered(questions, selected_answers)
        except UnansweredQuestionError:
            messagebox.showerror(
                ui_strings.UNANSWERED_QUESTION_ERROR_TITLE,
                ui_strings.UNANSWERED_QUESTION_ERROR_MESSAGE,
            )

    def _collect_selected_answers(self):
        selected_answers = []
        for answer, var in self.check_vars.items():
            is_selected = var.get()
            if is_selected:
                selected_answers.append(answer)
        return selected_answers
