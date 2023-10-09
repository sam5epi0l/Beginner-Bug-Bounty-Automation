import pyperclip

class Clipboard:
    @staticmethod
    def copy_to_clipboard(text):
        pyperclip.copy(text)
