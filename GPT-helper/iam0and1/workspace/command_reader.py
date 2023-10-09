import os

class CommandReader:
    @staticmethod
    def read_last_commands():
        home_dir = os.path.expanduser("~")
        history_file = os.path.join(home_dir, ".bash_history")
        with open(history_file, "r") as file:
            lines = file.readlines()
            last_commands = lines[-10:]
        return last_commands
