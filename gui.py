import tkinter
from PIL import Image, ImageTk


BOX_TITLE = "BZ 111 Quiz Program"

DEFAULT_FONT = "Helvetica 11"

NUMBERS = tuple(range(0, 100))


def longest_line(string_list):
    """Return the length of the longest line in list

    :param string_list: list of strings
    :return: int
    """
    paragraph = '\n'.join(string_list)
    line_list = paragraph.split("\n")
    return max([len(line) for line in line_list])


class QuestionLoop(object):
    def __init__(self, title, prompt, questions, correct_answers, solution,
                 solution_table=None, checker=None):
        self.title = title
        self.prompt = prompt
        self.questions = questions
        self.correct_answers = correct_answers
        self.solution = solution
        self.solution_table = solution_table

        if checker is None:
            checker = self.default_checker
        self.answer_checker = checker

    def default_checker(self, raw_answers):
        """Compare raw_answers to correct answers

        :param raw_answers: list of strings (user answers)
        :return: list of booleans
        """
        formatted_answers = [x.strip().lower() for x in raw_answers]
        result = [user == correct for user, correct
                  in zip(formatted_answers, self.correct_answers)]
        len_diff = len(self.correct_answers) - len(formatted_answers)
        if len_diff > 0:
            for _ in range(len_diff):
                result.append(False)
        return result

    def ask_question(self, old_answers, old_correct_list):
        """Display the question and request a user response

        :param old_answers: list of strings
        :param old_correct_list: list of booleans
        :return: (list of strings, list of booleans)
        """
        the_question = EntryQuestion(title=self.title, msg=self.prompt,
                                     questions=self.questions,
                                     default_entry=old_answers,
                                     colors=old_correct_list)
        the_question.run()
        raw_answers = the_question.user_entries
        is_correct_list = self.answer_checker(raw_answers)
        return raw_answers, is_correct_list

    def display_correct_window(self):
        """Display the correct answers including user's wrong answers

        :return: Window
        """
        all_buttons = ['New Question', 'Show Solution', 'Main Menu']
        if self.solution is None:
            all_buttons.remove('Show Solution')
        window = SimpleWindow(self.title, msg="That's right!",
                              buttons=all_buttons)
        window.run()
        return window.clicked

    def display_incorrect_window(self, is_correct_list):
        """Display number of correct answers when fewer than all are correct

        :param is_correct_list: list of booleans
        :return: Window
        """
        correct_num = sum(is_correct_list)
        tried_num = len(self.correct_answers)
        if correct_num == tried_num:
            correct_num -= 1  # -1 credit if given extra answers
        window = SimpleWindow(self.title, msg='{} of {} correct.'.format(
            correct_num, tried_num), buttons=['Try Again', 'Show Answers',
                                              'Show Solution', 'Main Menu'])
        window.run()
        return window.clicked

    def show_answers(self, correct_answers, raw_answers, is_correct_list):
        """Display correct answers along with user answers when incorrect

        :param correct_answers: list of correct answers
        :param raw_answers:  list of un-formatted user answers
        :param is_correct_list: list of booleans
        :return: Window
        """
        corrected_answers = [real if is_correct
                             else '{} ({})'.format(real, user)
                             for real, user, is_correct in
                             zip(correct_answers, raw_answers,
                                 is_correct_list)]
        all_buttons = ['New Question', 'Show Solution', 'Main Menu']
        if self.solution is None:
            all_buttons.remove('Show Solution')
        window = EntryQuestion(title=self.title, questions=self.questions,
                               msg=('{}\n\nCorrect answer (Your answer)\n'
                                    ''.format(self.prompt)),
                               default_entry=corrected_answers,
                               colors=is_correct_list,
                               buttons=all_buttons, is_disabled=True)
        window.run()
        return window.clicked

    def show_solution(self):
        """Display the solution

        :return: Window
        """
        buttons = ['New Question', 'Main Menu']
        message = ('{}\n\n{}'.format(self.prompt, self.solution))
        if self.solution_table:
            window = TableWindow(title=self.title, buttons=buttons,
                                 msg=message, table=self.solution_table)
        else:
            window = SimpleWindow(title=self.title, buttons=buttons,
                                  msg=message)
        window.run()
        return window.clicked

    def main_loop(self, old_answers=None, old_correct_list=None):
        """Display the question, solution, and answer as requested by the user

        :param old_answers: list of strings: user's previous answers
        :param old_correct_list: list of booleans: if old answers were correct
        :return: string): user-response
        """
        if old_answers is None:
            old_answers = []
        if old_correct_list is None:
            old_correct_list = []
        raw_answers, is_correct_list = self.ask_question(old_answers,
                                                         old_correct_list)

        if sum(is_correct_list) == len(self.correct_answers):
            user_response = self.display_correct_window()
        else:
            user_response = self.display_incorrect_window(is_correct_list)
            if user_response == 'Try Again':
                self.main_loop(raw_answers, is_correct_list)
        if user_response == 'Show Answers':
            user_response = self.show_answers(self.correct_answers,
                                              raw_answers, is_correct_list)
        if user_response == 'Show Solution':
            user_response = self.show_solution()
        return user_response


class RadioLoop(QuestionLoop):
    def __init__(self, title, prompt, questions, correct_answers, solution,
                 choices, solution_table=None, checker=None):
        super().__init__(title, prompt, questions, correct_answers, solution,
                         solution_table, checker)
        if type(choices[0]) is not list:
            raise TypeError('Choices must be a nested list, not', choices)
        self.choices = choices

    def ask_question(self, old_answers, old_correct_list):
        the_question = RadioQuestion(title=self.title, msg=self.prompt,
                                     questions=self.questions,
                                     default_entry=old_answers,
                                     colors=old_correct_list,
                                     choices=self.choices)
        the_question.run()
        raw_answers = the_question.user_entries
        is_correct_list = self.answer_checker(raw_answers)
        return raw_answers, is_correct_list


class Window(object):
    def __init__(self, title='', width=None):
        self.root = tkinter.Tk()
        if width is not None:
            self.root.geometry()
        self.root.wm_title(title)
        self.canvas = tkinter.Canvas(self.root, borderwidth=10)
        self.window = self.scroll_window()
        self.clicked = None
        self.images = []

    def scroll_window(self):
        """Create a frame with a scroll bar

        :return: tkinter.Frame
        """
        window = tkinter.Frame(self.root)
        scroller = tkinter.Scrollbar(self.root, orient="vertical",
                                     command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroller.set)

        scroller.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=window, anchor="nw",
                                  tags="self.window")
        return window

    @staticmethod
    def make_text(location, msg, pad=0):
        """Create text Label with standard formatting

        :param location: tkinter.Frame or tkinter.Tk
        :param msg: string
        :param pad: int padding for x and y
        :return: tkinter/Label
        """
        text = tkinter.Label(location, text='\n{}\n'.format(msg),
                             wraplength=600, justify='left', anchor='w',
                             padx=pad, pady=pad, font=DEFAULT_FONT)

        return text

    def make_buttons(self, location, buttons, commands=None):
        """Create a frame of tkinter.Buttons

        :param location: tkinter.Frame or tkinter.Tk
        :param buttons: list of strings (button names)
        :param commands: list of functions
        :return: tkinter.Frame
        """
        button_frame = tkinter.Frame(location)
        self.make_spacer(button_frame).grid()
        for button_num, each_b in enumerate(buttons):
            self.make_spacer(button_frame, width=3).grid(
                column=NUMBERS[::2][button_num], row=1, sticky="nsew")

            if commands is None:
                def command_type(name=each_b):
                    self.click_and_close(name)
            else:
                command_type = commands[button_num]
            next_button = tkinter.Button(button_frame, text=each_b,
                                         command=command_type,
                                         font=DEFAULT_FONT)
            next_button.grid(column=NUMBERS[1::2][button_num], row=1,
                             sticky="nsew")
        return button_frame

    def to_ImageTk(self, image_PIL):
        """Convert PIL images and store

        :param image_PIL: PIL.image
        :return: ImageTk
        """
        pic = ImageTk.PhotoImage(image_PIL)
        self.images.append(pic)
        return pic

    @staticmethod
    def make_spacer(location, height=1, width=1):
        space = tkinter.Label(location, text='', font='Helvetica 1',
                              height=height, width=width)
        return space

    def click_and_close(self, button_name):
        """Store the name of the button clicked and close the window

        :param button_name: string
        :return: None
        """
        self.clicked = button_name
        self.root.destroy()

    def configure_canvas(self):
        """Calculate and implement proper scrolling area.

        :return: None
        """
        self.window.update_idletasks()   # this updates window size

        border = 10
        self.canvas.config(
            width=self.window.winfo_reqwidth() + border,
            height=min(350, self.window.winfo_reqheight() + border,))
        self.canvas.configure(scrollregion=(
            0, 0,
            self.window.winfo_reqwidth() + border,
            self.window.winfo_reqheight() + border))

    def run(self):
        self.configure_canvas()
        self.root.mainloop()


class SimpleWindow(Window):
    def __init__(self, title='', msg='', buttons=None):
        super().__init__(title=title)
        if buttons is None:
            buttons = ['Okay']
        self.clicked = None

        the_text = self.make_text(self.window, msg)
        the_text.pack()
        self.make_buttons(self.window, buttons).pack()


class TableWindow(Window):
    def __init__(self, table, title='', msg='', buttons=None):
        super().__init__(title)
        if buttons is None:
            buttons = ['Okay']
        self.make_text(self.window, msg).pack()
        self.make_table(self.window, table).pack()
        self.make_buttons(self.window, buttons).pack()

    @staticmethod
    def make_table(location, nested_list):
        table_frame = tkinter.Frame(location)
        for row_num, row in enumerate(nested_list):
            for col_num, cell in enumerate(row):
                anchor_type = "center"
                relief_type = 'ridge'
                if row_num == 0 or col_num == 0:
                    chosen_font = DEFAULT_FONT + ' bold'
                    relief_type = 'flat'
                    if col_num == 0:
                        anchor_type = 'e'
                else:
                    chosen_font = DEFAULT_FONT
                new_label = tkinter.Label(
                    table_frame, text=cell, anchor=anchor_type,
                    font=chosen_font, padx=5, pady=5, relief=relief_type)
                new_label.grid(row=row_num, column=col_num, sticky="nsew")
        return table_frame


class EntryQuestion(Window):
    def __init__(self, title='', msg='', questions=None, default_entry=None,
                 colors=None, image_path=None, buttons=None,
                 is_disabled=False):
        super().__init__(title)
        self.user_entries = []
        self.clicked = None

        self.make_text(self.window, msg).pack()
        if image_path is not None:
            self.make_image(self.window, image_path).pack()

        _, self.entries = self.make_entry_boxes(self.window,
                                                questions, default_entry,
                                                colors, is_disabled)
        if buttons is None:
            self.make_buttons(self.window, buttons=["Submit"],
                              commands=[self.submit]).pack()
        else:
            self.make_buttons(self.window, buttons=buttons).pack()

    @staticmethod
    def make_entry_boxes(location, questions, default_entry, colors,
                         is_disabled):
        if questions is None:
            questions = []
        if default_entry is None:
            default_entry = []
        if colors is None:
            colors = []
        entry_frame = tkinter.Frame(location)
        entries = []
        background = [None if x else 'pink' for x in colors]
        for row_num, each_q in enumerate(questions):
            try:
                next_color = background[row_num]
            except IndexError:
                next_color = None
            new_label = tkinter.Label(entry_frame, text=each_q,
                                      font=DEFAULT_FONT, anchor='e')
            new_entry = tkinter.Entry(entry_frame, bg=next_color, width=75)

            try:
                new_entry.insert(0, default_entry[row_num])
                if is_disabled:
                    new_entry.config(state="disabled",
                                     disabledbackground=next_color,
                                     disabledforeground="black")
            except IndexError:
                pass

            new_entry.grid(column=1, row=row_num, sticky="nsew")
            new_label.grid(column=0, row=row_num, sticky="nsew")

            entries.append(new_entry)
        entry_frame.pack()

        return entry_frame, entries

    def submit(self):
        self.user_entries = [x.get() for x in self.entries]
        self.root.destroy()


class RadioQuestion(Window):
    def __init__(self, title='', msg='', questions=None, choices=None,
                 image_path=None, buttons=None, colors=None,
                 default_entry=None):
        super().__init__(title)
        self.user_entries = []
        self.clicked = None

        self.make_text(self.window, msg).pack()
        if image_path is not None:
            self.make_image(self.window, image_path).pack()

        _, self.entries = self.make_radio_buttons(self.window, questions,
                                                  choices, default_entry,
                                                  colors)
        if buttons is None:
            self.make_buttons(self.window, buttons=["Submit"],
                              commands=[self.submit]).pack()
        else:
            self.make_buttons(self.window, buttons=buttons).pack()

    @staticmethod
    def make_radio_buttons(location, questions, choices, default_entry,
                           colors):
        if questions is None:
            questions = []
        if not default_entry:
            default_entry = [None for _ in questions]
        if choices is None:
            choices = [[]]

        radio_frame = tkinter.Frame(location)
        radio_vars = []

        for row_num, (each_q, choice_list) in enumerate(
                zip(questions, choices)):

            new_label = tkinter.Label(radio_frame, text=each_q,
                                      font=DEFAULT_FONT, anchor='e')
            new_label.grid(column=0, row=row_num, sticky="nsew")
            radio_vars.append(tkinter.StringVar())
            default_value = default_entry[row_num]
            radio_vars[row_num].set(default_value)
            for ch_num, each_ch in enumerate(choice_list):
                if each_ch == default_value and not colors[row_num]:
                    background = 'pink'
                else:
                    background = None
                new_choice = tkinter.Radiobutton(radio_frame, text=each_ch,
                                                 value=each_ch,
                                                 variable=radio_vars[row_num],
                                                 font=DEFAULT_FONT,
                                                 anchor='e', bg=background)
                new_choice.grid(column=1 + ch_num, row=row_num, sticky="nsew")

        radio_frame.pack()
        return radio_frame, radio_vars

    def submit(self):
        """Store user responses as a list of strings

        :return: None
        """
        self.user_entries = [x.get() for x in self.entries]
        self.root.destroy()


if __name__ == "__main__":

    test = RadioQuestion(msg='heres the info',
                         questions=['mom gamets?', 'dad gametes?'])


