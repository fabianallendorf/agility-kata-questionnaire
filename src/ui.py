import random
import tkinter as tk
from tkinter import ttk

from src.dataclasses import Question
from src.questionnaire_validator import QuestionnaireValidator


class QuestionnaireUI(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.grid()
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
                ttk.Checkbutton(master=self, text=answer.text, variable=self.check_vars[answer]).grid(column=1, row=row)
                row += 1
        ttk.Label(master=self, text="\n").grid(column=1, row=row)
        row += 1
        ttk.Button(master=self, text="Show results", command=self.show_results).grid(
            column=0, row=row
        )
        ttk.Button(master=self, text="Quit", command=self.quit).grid(
            column=2, row=row
        )  # self.destroy ?

    def show_results(self):
        selected_answers = self._collect_selected_answers()
        print(selected_answers)

    def _collect_selected_answers(self):
        selected_answers = []
        for answer, var in self.check_vars.items():
            is_selected = var.get()
            if is_selected:
                selected_answers.append(answer)
        return selected_answers
