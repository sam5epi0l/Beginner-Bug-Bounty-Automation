import json

class BugBountyToolReader:
    @staticmethod
    def read_bug_bounty_tools():
        with open("commands.json", "r") as file:
            tools = json.load(file)
        return tools
