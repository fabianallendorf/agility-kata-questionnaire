import random
import tkinter as tk
from tkinter import ttk, messagebox

from src import strings
from src.dataclasses import Question, ValidatedQuestion, Questionnaire
from src.exceptions import UnansweredQuestionError
from src.questionnaire_validator import QuestionnaireValidator


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
        self.page = ResultUI(validated_questions=validated_questions, master=self)
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


class QuestionnaireUI(ttk.Frame):
    def __init__(self, questions: list[Question], master=None):
        super().__init__(master=master)
        self.grid()
        self._root().title(strings.TITLE)  # noqa
        self.questions = questions
        self.answer_selection_map = dict()
        self.current_row = 0

    def display_questionnaire(self):
        for question in self.questions:
            self._display_question_text(question)
            answers = self._shuffle_answers(question)
            for answer in answers:
                self._display_answer(answer)
        self._display_buttons()

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
            master=self,
            text=answer.text,
            variable=self.answer_selection_map[answer],
        ).grid(column=1, row=self.current_row)
        self.current_row += 1

    def _display_buttons(self):
        ttk.Label(master=self, text="\n").grid(column=1, row=self.current_row)
        self.current_row += 1
        ttk.Button(
            master=self,
            text=strings.SHOW_RESULTS,
            command=self.show_results,
        ).grid(column=0, row=self.current_row)
        ttk.Button(master=self, text=strings.QUIT, command=self.quit).grid(
            column=2, row=self.current_row
        )
        self.current_row += 1

    def show_results(self):
        selected_answers = self._collect_selected_answers()
        try:
            QuestionnaireValidator.check_all_questions_are_answered(
                self.questions, selected_answers
            )
        except UnansweredQuestionError:
            self._show_error()
        else:
            validated_questions = QuestionnaireValidator.validate_answers(self.questions, selected_answers)
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


class ResultUI(ttk.Frame):
    def __init__(self, validated_questions: list[ValidatedQuestion], master=None):
        super().__init__(master=master)
        self._root().title(strings.SHOW_RESULTS)  # noqa
        self.grid()
        self.validated_questions = validated_questions
        self.row_index = 0

    def display_results(self):
        for validated_question in self.validated_questions:
            question = validated_question.answered_question.question
            ttk.Label(master=self, text=question.text).grid(column=0, row=self.row_index)
            self.row_index += 1
            if validated_question.is_correct:
                answer_text = ",".join(answer.text for answer in validated_question.answered_question.user_answers)
                ttk.Label(master=self, text=f"Your answer '{answer_text}' is correct").grid(column=1, row=self.row_index, padx=5)
                self.row_index += 1
            else:
                answer_text = ",".join(answer.text for answer in validated_question.answered_question.user_answers)
                ttk.Label(master=self, text=f"Your answer '{answer_text}' is wrong").grid(column=1,row=self.row_index, padx=5)
                self.row_index += 1
                correct_answer_text = ",".join(answer.text for answer in question.correct_answers)
                ttk.Label(master=self, text=f"The correct answer is '{correct_answer_text}'").grid(column=1, row=self.row_index, padx=5)
                self.row_index += 1


