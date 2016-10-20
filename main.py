import gui
import hardy_weinberg
import punnet

BOX_TITLE = "BZ 111 Quiz Program"


def run():
    user_choice = ''
    while user_choice not in ['Exit Program', None]:
        window = gui.SimpleWindow(title=BOX_TITLE,
                                  msg='BZ 111 Practice Problems',
                                  buttons=['Hardy-Weinberg', 'Punnet Squares',
                                           'Exit Program'])
        window.run()
        user_choice = window.clicked
        if user_choice == 'Hardy-Weinberg':
            user_choice = hardy_weinberg.run()
        if user_choice == 'Punnet Squares':
            user_choice = punnet.run()

if __name__ == "__main__":
    run()