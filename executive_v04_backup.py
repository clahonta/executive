from pathlib import Path
from datetime import datetime
import ollama
from workspace import load_excel_files


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

INBOX = WORKSPACE / "inbox"


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
# Load workspace content
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
# Load workspace inventory
# -----------------------------

def load_workspace_inventory():

    files = []

    folders = [
        WORKSPACE / "documents",
        WORKSPACE / "memory",
        WORKSPACE / "interviews",
        WORKSPACE / "inbox",
    ]

    for folder in folders:

        if not folder.exists():
            continue

        for file in folder.iterdir():

            if file.is_file() and not file.name.startswith("."):
                files.append(str(file))

    if not files:
        return "No files found."

    return "\n".join(files)



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
# Memory review
# -----------------------------

def memory_review(messages):

    review_prompt = """
Review this working session for possible project memory updates.

Do not modify any files.

Identify only information that may belong in:

- project_state.md
- open_questions.md
- decision_log.md

For each possible update provide:

1. Target file
2. Reason it belongs there
3. Proposed update
4. Whether owner confirmation is required

If no updates are needed, say so.
"""

    review_messages = messages.copy()

    review_messages.append(
        {
            "role": "user",
            "content": review_prompt
        }
    )

    response = ollama.chat(
        model=MODEL_NAME,
        messages=review_messages
    )

    return response["message"]["content"]



# -----------------------------
# Main chat loop
# -----------------------------

def main():

    system_prompt = load_system_prompt()

    workspace_context = load_workspace_context()

    workspace_inventory = load_workspace_inventory()

    excel_context = load_excel_files(INBOX)

    if excel_context:

        workspace_context += (
            "\n\n" +
            "\n\n".join(excel_context)
        )


    print("===================================")
    print("Executive AI v0.4")
    print("===================================")
    print()

    print("Loaded:")
    print(f"✓ {PROMPT_FILE}")
    print(f"✓ {WORKSPACE}")
    print()

    print("Commands:")
    print("/review-memory  - review possible memory updates")
    print("quit            - save and exit")
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

The PROJECT FILE INVENTORY below is authoritative.

PROJECT FILE INVENTORY:

{workspace_inventory}


PROJECT WORKSPACE CONTENT:

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


        if user_input == "/review-memory":

            print("\nExecutive Memory Review:\n")

            review = memory_review(messages)

            print(review)
            print()

            continue


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