import random
import tkinter as tk
from itertools import chain
from tkinter import ttk

from src.dataclasses import Question


class QuestionnaireUI(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.grid()

    def display_questionnaire(self, questions: list[Question]):
        row = 0
        for question in questions:
            ttk.Label(master=self, text=question.text).grid(column=0, row=row)
            answers = question.correct_answers + question.incorrect_answers
            random.shuffle(answers)
            for answer in answers:
                row += 1
                ttk.Checkbutton(master=self, text=answer.text).grid(column=0, row=row)
            row += 1

        ttk.Button(master=self, text="Show results", command=self.show_results).grid(
            column=0, row=row
        )
        ttk.Button(master=self, text="Quit", command=self.destroy).grid(
            column=0, row=row
        )
