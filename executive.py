from pathlib import Path
from datetime import datetime
import ollama


# -----------------------------
# Configuration
# -----------------------------

MODEL_NAME = "llama3.1:8b"

PROMPT_FILE = Path("prompts/executive.md")

WORKSPACE = Path.home() / "ExecutiveWorkspace"

MEMORY_PATHS = [
    WORKSPACE / "documents",
    WORKSPACE / "memory",
    WORKSPACE / "interviews",
]

CONVERSATION_OUTPUT = WORKSPACE / "memory" / "conversations"


# -----------------------------
# Load Executive instructions
# -----------------------------

def load_system_prompt():

    if not PROMPT_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {PROMPT_FILE}"
        )

    return PROMPT_FILE.read_text()


# -----------------------------
# Load workspace memory
# -----------------------------

def load_workspace_context():

    context = []

    for folder in MEMORY_PATHS:

        if not folder.exists():
            continue

        for file in folder.glob("*.md"):

            text = file.read_text()

            context.append(
                f"""
==============================
FILE: {file.name}
LOCATION: {folder}

{text}
==============================
"""
            )

    if not context:
        return "No workspace memory found."

    return "\n\n".join(context)


# -----------------------------
# Save conversation
# -----------------------------

def save_conversation(messages):

    CONVERSATION_OUTPUT.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    output_file = (
        CONVERSATION_OUTPUT /
        f"session_{timestamp}.md"
    )

    with open(output_file, "w") as f:

        f.write("# Executive Conversation\n\n")
        f.write(
            f"Date: {datetime.now()}\n\n"
        )

        for message in messages:

            role = message["role"].upper()

            f.write(
                f"## {role}\n\n"
            )

            f.write(
                message["content"]
            )

            f.write("\n\n")

    print()
    print("Conversation saved:")
    print(output_file)


# -----------------------------
# Main chat loop
# -----------------------------

def main():

    system_prompt = load_system_prompt()

    workspace_context = load_workspace_context()

    print("===================================")
    print("Executive AI v0.2")
    print("===================================")
    print()

    print("Loaded:")
    print(f"✓ {PROMPT_FILE}")
    print(f"✓ {WORKSPACE}")
    print()

    print("Type 'quit' to exit.")
    print()

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"""
You are starting a new working session.

Below is the current project workspace.

Use this as background context.
Do not assume every item is a final decision.
Ask questions when clarification is needed.

PROJECT WORKSPACE:

{workspace_context}
"""
        }
    ]

    while True:

        user_input = input("> ")

        if user_input.lower() in ["quit", "exit"]:

            save_conversation(messages)

            print("Goodbye.")
            break


        messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )


        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages
        )


        answer = response["message"]["content"]


        print("\nExecutive:")
        print(answer)
        print()


        messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


if __name__ == "__main__":
    main()