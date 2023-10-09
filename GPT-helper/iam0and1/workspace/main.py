from command_reader import CommandReader
from bug_bounty_tool_reader import BugBountyToolReader
from openai_api_client import OpenAIAPIClient
from clipboard import Clipboard

def main():
    # Read last commands
    command_reader = CommandReader()
    last_commands = command_reader.read_last_commands()

    # Read bug bounty tools
    tool_reader = BugBountyToolReader()
    bug_bounty_tools = tool_reader.read_bug_bounty_tools()

    # Send commands and tools to OpenAI API
    openai_client = OpenAIAPIClient()
    suggested_commands = openai_client.send_commands_and_tools(last_commands, bug_bounty_tools)

    # Display suggested commands
    print("Suggested Commands:")
    for i, command in enumerate(suggested_commands, start=1):
        print(f"{i}. {command}")

    # Select and copy a command to clipboard
    selected_command = input("Select a command number to copy to clipboard: ")
    if selected_command.isdigit() and int(selected_command) in range(1, len(suggested_commands) + 1):
        Clipboard.copy_to_clipboard(suggested_commands[int(selected_command) - 1])
        print("Command copied to clipboard!")
    else:
        print("Invalid command number.")

if __name__ == "__main__":
    main()
