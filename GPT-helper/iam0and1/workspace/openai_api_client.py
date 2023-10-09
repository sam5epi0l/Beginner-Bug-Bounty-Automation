import os
import openai

class OpenAIAPIClient:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def send_commands_and_tools(self, commands, tools):
        prompt = "Act as a bug bounty hunter and help me find bugs on my website. Suggest next 10 commands that I should run based on the last 10 commands and the list of tools provided."
        context = "\n".join(commands)
        data = {
            "prompt": prompt,
            "context": context,
            "tools": tools
        }
        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=data["prompt"],
            max_tokens=100,
            context=data["context"],
            tools=data["tools"]
        )
        suggested_commands = response.choices[0].text.strip().split("\n")
        return suggested_commands
