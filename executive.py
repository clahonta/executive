from pathlib import Path
from datetime import datetime
import json
import re

import ollama

from workspace import load_excel_files


# ============================================================
# Executive AI v0.5
#
# Local project steward with persistent memory management
# ============================================================


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

MODEL_NAME = "llama3.1:8b"

PROMPT_FILE = Path("prompts/executive.md")


# ------------------------------------------------------------
# Workspace Configuration
# ------------------------------------------------------------

WORKSPACE = Path.home() / "ExecutiveWorkspace"


DOCUMENTS_PATH = WORKSPACE / "documents"

MEMORY_PATH = WORKSPACE / "memory"

INTERVIEWS_PATH = WORKSPACE / "interviews"

INBOX_PATH = WORKSPACE / "inbox"


# Conversation storage

CONVERSATIONS_PATH = (
    MEMORY_PATH / "conversations"
)


# Memory proposal storage

PROPOSALS_PATH = (
    MEMORY_PATH / "proposals"
)


# ------------------------------------------------------------
# Memory Files
# ------------------------------------------------------------

PROJECT_STATE_FILE = (
    MEMORY_PATH / "project_state.md"
)

OPEN_QUESTIONS_FILE = (
    MEMORY_PATH / "open_questions.md"
)

DECISION_LOG_FILE = (
    MEMORY_PATH / "decision_log.md"
)


# Only these files can ever be modified automatically

ALLOWED_MEMORY_FILES = {

    "project_state.md":
        PROJECT_STATE_FILE,

    "open_questions.md":
        OPEN_QUESTIONS_FILE,

    "decision_log.md":
        DECISION_LOG_FILE,
}


# ------------------------------------------------------------
# Session State
# ------------------------------------------------------------

SESSION_START = datetime.now()


# ------------------------------------------------------------
# Utility Functions
# ------------------------------------------------------------

def ensure_workspace():

    folders = [

        WORKSPACE,

        DOCUMENTS_PATH,

        MEMORY_PATH,

        INTERVIEWS_PATH,

        INBOX_PATH,

        CONVERSATIONS_PATH,

        PROPOSALS_PATH,

    ]

    for folder in folders:
        folder.mkdir(
            parents=True,
            exist_ok=True
        )



def load_system_prompt():

    if not PROMPT_FILE.exists():

        raise FileNotFoundError(
            f"Missing system prompt: {PROMPT_FILE}"
        )

    return PROMPT_FILE.read_text()



def timestamp():

    return datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )



# ------------------------------------------------------------
# Workspace Inventory
# ------------------------------------------------------------

def load_workspace_inventory():

    files = []

    search_paths = [

        DOCUMENTS_PATH,

        MEMORY_PATH,

        INTERVIEWS_PATH,

        INBOX_PATH,

    ]


    for folder in search_paths:

        if not folder.exists():
            continue


        for item in folder.rglob("*"):

            if item.is_file():

                if item.name.startswith("."):
                    continue

                files.append(
                    str(item)
                )


    if not files:

        return "No files found."


    return "\n".join(
        sorted(files)
    )



# ------------------------------------------------------------
# Workspace Context Loading
# ------------------------------------------------------------

def load_workspace_context():

    context = []


    search_paths = [

        DOCUMENTS_PATH,

        MEMORY_PATH,

        INTERVIEWS_PATH,

    ]


    for folder in search_paths:

        if not folder.exists():
            continue


        for file in folder.rglob("*.md"):


            text = file.read_text(
                errors="ignore"
            )


            context.append(
                f"""
==============================
FILE:
{file}

CONTENT:

{text}
==============================
"""
            )


    if not context:

        return (
            "No markdown workspace "
            "documents found."
        )


    return "\n\n".join(context)



# ------------------------------------------------------------
# Excel Context Loading
# ------------------------------------------------------------

def load_inbox_context():

    excel_context = load_excel_files(
        INBOX_PATH
    )


    if not excel_context:

        return ""


    return "\n\n".join(
        excel_context
    )



# ============================================================
# END OF PART 1
# ============================================================
# ============================================================
# Conversation Management
# ============================================================


def save_conversation(messages):

    CONVERSATIONS_PATH.mkdir(
        parents=True,
        exist_ok=True
    )


    output_file = (
        CONVERSATIONS_PATH /
        f"session_{timestamp()}.md"
    )


    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:


        f.write(
            "# Executive Conversation\n\n"
        )


        f.write(
            f"Date: {datetime.now()}\n\n"
        )


        for message in messages:

            role = (
                message["role"]
                .upper()
            )


            f.write(
                f"## {role}\n\n"
            )


            f.write(
                message["content"]
            )


            f.write(
                "\n\n"
            )


    print()
    print(
        "Conversation saved:"
    )
    print(
        output_file
    )



# ============================================================
# Memory Proposal Management
# ============================================================


def create_proposal(content):

    PROPOSALS_PATH.mkdir(
        parents=True,
        exist_ok=True
    )


    proposal_file = (
        PROPOSALS_PATH /
        f"proposal_{timestamp()}.md"
    )


    with open(
        proposal_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "# Memory Update Proposal\n\n"
        )

        f.write(
            f"Created: {datetime.now()}\n\n"
        )

        f.write(
            "Status: Pending Approval\n\n"
        )

        f.write(
            "------------------------------\n\n"
        )

        f.write(
            content
        )


    return proposal_file



def get_latest_proposal():

    if not PROPOSALS_PATH.exists():

        return None


    proposals = list(
        PROPOSALS_PATH.glob(
            "proposal_*.md"
        )
    )


    if not proposals:

        return None


    return sorted(
        proposals
    )[-1]



def load_latest_proposal():

    proposal = (
        get_latest_proposal()
    )


    if proposal is None:

        return None, None


    return (
        proposal,
        proposal.read_text(
            encoding="utf-8"
        )
    )



# ============================================================
# Memory Proposal Validation
# ============================================================


def extract_target_file(proposal_text):

    """
    Extracts the intended memory file
    from a proposal.

    Expected format:

    TARGET:
    open_questions.md
    """

    match = re.search(
        r"TARGET:\s*(.*)",
        proposal_text,
        re.IGNORECASE
    )


    if not match:

        return None


    target = (
        match.group(1)
        .strip()
    )


    return target



def validate_memory_target(target):

    if target is None:

        return None


    return ALLOWED_MEMORY_FILES.get(
        target
    )



# ============================================================
# Apply Memory Update
# ============================================================


def apply_memory_update():

    proposal_file, proposal = (
        load_latest_proposal()
    )


    if proposal is None:

        print(
            "No pending memory proposal found."
        )

        return



    target_name = (
        extract_target_file(
            proposal
        )
    )


    target_file = (
        validate_memory_target(
            target_name
        )
    )


    if target_file is None:

        print(
            "ERROR:"
        )

        print(
            "Proposal target is invalid."
        )

        print(
            "Only approved memory files may be updated:"
        )

        for name in ALLOWED_MEMORY_FILES:
            print(
                f"- {name}"
            )

        return



    print()

    print(
        "Applying memory update:"
    )

    print(
        proposal_file
    )

    print()

    print(
        "Updating:"
    )

    print(
        target_file
    )


    with open(
        target_file,
        "a",
        encoding="utf-8"
    ) as f:


        f.write(
            "\n\n"
        )


        f.write(
            proposal
        )


    archive_name = (
        proposal_file.parent /
        "applied"
    )


    archive_name.mkdir(
        exist_ok=True
    )


    proposal_file.rename(
        archive_name /
        proposal_file.name
    )


    print()

    print(
        "Memory update complete."
    )



# ============================================================
# END OF PART 2
# ============================================================
# ============================================================
# Command Handling
# ============================================================


def show_help():

    print()

    print("Executive Commands")
    print("==================")

    print()

    print("/help")
    print(
        "Show available commands."
    )

    print()

    print("/memory-status")
    print(
        "Show current memory files and pending proposals."
    )

    print()

    print("/memory-review")
    print(
        "Analyze the current conversation and create a memory proposal."
    )

    print()

    print("/memory-approve")
    print(
        "Apply the latest approved memory proposal."
    )

    print()

    print("/quit")
    print(
        "Exit Executive and save conversation."
    )

    print()



# ============================================================
# Memory Status Command
# ============================================================


def show_memory_status():

    print()

    print(
        "Executive Memory Status"
    )

    print(
        "======================="
    )

    print()


    print(
        "Memory Files:"
    )


    for name, path in ALLOWED_MEMORY_FILES.items():

        exists = (
            "FOUND"
            if path.exists()
            else "MISSING"
        )

        print(
            f"- {name}: {exists}"
        )


    print()


    print(
        "Pending Proposals:"
    )


    proposal = (
        get_latest_proposal()
    )


    if proposal:

        print(
            f"- {proposal}"
        )

    else:

        print(
            "- None"
        )


    print()



# ============================================================
# Memory Review Command
# ============================================================


def create_memory_review(messages):

    print()

    print(
        "Reviewing conversation for memory updates..."
    )


    review_prompt = """

You are reviewing a project conversation.

Your task is to identify information that belongs
in persistent project memory.

Only identify:

- confirmed decisions
- unresolved questions
- important project state changes
- requirements
- architectural choices
- constraints

Do not capture:
- casual discussion
- temporary thoughts
- duplicate information


Return your response in this exact format:

TARGET:
<one of:
project_state.md
open_questions.md
decision_log.md
>


REASON:
<why this belongs in memory>


UPDATE:
<the exact markdown content that should be added>


If no memory update is required, return:

NO_UPDATE

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


    proposal = (
        response["message"]["content"]
    )


    if proposal.strip() == "NO_UPDATE":

        print()

        print(
            "No memory update required."
        )

        return



    proposal_file = (
        create_proposal(
            proposal
        )
    )


    print()

    print(
        "Memory proposal created:"
    )

    print(
        proposal_file
    )

    print()

    print(
        "Review this file before approval."
    )



# ============================================================
# Command Router
# ============================================================


def handle_command(
    command,
    messages
):

    command = (
        command.lower()
        .strip()
    )


    if command == "/help":

        show_help()

        return True



    if command == "/memory-status":

        show_memory_status()

        return True



    if command == "/memory-review":

        create_memory_review(
            messages
        )

        return True



    if command == "/memory-approve":

        apply_memory_update()

        return True



    return False



# ============================================================
# END OF PART 3
# ============================================================
# ============================================================
# Main Executive Application
# ============================================================


def build_initial_context():

    inventory = (
        load_workspace_inventory()
    )


    workspace_context = (
        load_workspace_context()
    )


    excel_context = (
        load_inbox_context()
    )


    if excel_context:

        workspace_context += (

            "\n\n"
            "==============================\n"
            "EXCEL SOURCE MATERIALS\n"
            "==============================\n\n"
            +
            excel_context

        )


    return f"""

You are starting a new Executive AI working session.

The project workspace is local and authoritative.

The application has provided the following file inventory.

PROJECT FILE INVENTORY:

{inventory}


WORKSPACE CONTENT:

{workspace_context}


Operating rules:

- The file inventory is authoritative.
- Do not claim access to files not listed.
- Treat documents as project memory, not absolute truth.
- Distinguish decisions from assumptions.
- Ask questions when information is unclear.
- Important project knowledge should be proposed for memory storage.

"""


def start_session():

    ensure_workspace()


    system_prompt = (
        load_system_prompt()
    )


    initial_context = (
        build_initial_context()
    )


    print()

    print(
        "==================================="
    )

    print(
        "Executive AI v0.5"
    )

    print(
        "==================================="
    )

    print()


    print(
        "Loaded:"
    )

    print(
        f"✓ {PROMPT_FILE}"
    )

    print(
        f"✓ {WORKSPACE}"
    )

    print()

    print(
        "Commands:"
    )

    print(
        "/help for available commands"
    )

    print()


    messages = [

        {
            "role": "system",
            "content": system_prompt
        },

        {
            "role": "user",
            "content": initial_context
        }

    ]


    return messages



# ============================================================
# Chat Loop
# ============================================================


def run():

    messages = (
        start_session()
    )


    while True:


        try:

            user_input = input("> ")


        except KeyboardInterrupt:

            print()

            print(
                "Saving conversation..."
            )

            save_conversation(
                messages
            )

            break



        if not user_input.strip():

            continue



        if user_input.lower() in [

            "quit",
            "exit",
            "/quit"

        ]:


            save_conversation(
                messages
            )


            print()

            print(
                "Goodbye."
            )


            break



        # ------------------------------------------------
        # Commands
        # ------------------------------------------------

        if user_input.startswith("/"):

            handled = (
                handle_command(
                    user_input,
                    messages
                )
            )


            if handled:

                continue



        # ------------------------------------------------
        # Normal conversation
        # ------------------------------------------------


        messages.append(

            {
                "role": "user",
                "content": user_input
            }

        )


        try:


            response = ollama.chat(

                model=MODEL_NAME,

                messages=messages

            )


            answer = (
                response["message"]["content"]
            )


        except Exception as e:


            answer = (

                "ERROR communicating with Ollama:\n\n"
                +
                str(e)

            )



        print()

        print(
            "Executive:"
        )

        print(
            answer
        )

        print()


        messages.append(

            {
                "role": "assistant",
                "content": answer
            }

        )



# ============================================================
# Program Entry Point
# ============================================================


if __name__ == "__main__":

    run()


# ============================================================
# END OF PART 4
# ============================================================

# ============================================================
# Memory Safety and Diagnostics
# ============================================================


def show_latest_proposal():

    proposal_file, proposal = (
        load_latest_proposal()
    )


    print()


    if proposal is None:

        print(
            "No pending memory proposal."
        )

        print()

        return



    print(
        "Latest Memory Proposal"
    )

    print(
        "======================"
    )

    print()

    print(
        f"FILE:\n{proposal_file}"
    )

    print()

    print(
        proposal
    )

    print()



# ============================================================
# Duplicate Protection
# ============================================================


def memory_already_contains(
    target_file,
    content
):

    if not target_file.exists():

        return False


    existing = (
        target_file.read_text(
            encoding="utf-8"
        )
    )


    normalized_existing = (
        existing.lower()
        .strip()
    )


    normalized_content = (
        content.lower()
        .strip()
    )


    return (
        normalized_content
        in
        normalized_existing
    )



# ============================================================
# Safer Memory Application
# ============================================================


def apply_memory_update():

    proposal_file, proposal = (
        load_latest_proposal()
    )


    if proposal is None:

        print()

        print(
            "No pending memory proposal found."
        )

        return



    target_name = (
        extract_target_file(
            proposal
        )
    )


    target_file = (
        validate_memory_target(
            target_name
        )
    )


    if target_file is None:

        print()

        print(
            "ERROR: Invalid memory target."
        )

        print(
            "Allowed targets:"
        )


        for name in ALLOWED_MEMORY_FILES:

            print(
                f"- {name}"
            )


        return



    update_match = re.search(

        r"UPDATE:\s*(.*)",

        proposal,

        re.DOTALL

    )


    if not update_match:

        print()

        print(
            "ERROR:"
        )

        print(
            "Proposal does not contain UPDATE section."
        )

        return



    update_content = (
        update_match.group(1)
        .strip()
    )


    if memory_already_contains(

        target_file,

        update_content

    ):

        print()

        print(
            "Memory already contains this information."
        )

        print(
            "No update applied."
        )

        return



    with open(

        target_file,

        "a",

        encoding="utf-8"

    ) as f:


        f.write(

            "\n\n"

        )


        f.write(

            update_content

        )


    archive_folder = (

        PROPOSALS_PATH /

        "applied"

    )


    archive_folder.mkdir(

        parents=True,

        exist_ok=True

    )


    proposal_file.rename(

        archive_folder /

        proposal_file.name

    )


    print()

    print(
        "Memory update applied successfully."
    )

    print()

    print(
        f"Updated: {target_file}"
    )



# ============================================================
# Startup Diagnostics
# ============================================================


def startup_diagnostics():

    print()

    print(
        "Workspace Diagnostics"
    )

    print(
        "====================="
    )

    print()


    print(
        "Workspace:"
    )

    print(
        WORKSPACE
    )

    print()


    print(
        "Memory files:"
    )


    for name, path in ALLOWED_MEMORY_FILES.items():

        status = (

            "OK"

            if path.exists()

            else "MISSING"

        )


        print(
            f"- {name}: {status}"
        )


    print()


    print(
        "Inventory count:"
    )


    inventory = (
        load_workspace_inventory()
    )


    if inventory:

        count = len(
            inventory.splitlines()
        )

    else:

        count = 0


    print(
        count
    )

    print()



# ============================================================
# Command Extension
# ============================================================


_old_handle_command = handle_command



def handle_command(
    command,
    messages
):


    if command.lower().strip() == "/memory-show":

        show_latest_proposal()

        return True



    return _old_handle_command(
        command,
        messages
    )



# ============================================================
# END OF PART 5
# ============================================================

# ============================================================
# Final v0.5 Operational Notes
# ============================================================

"""
Executive AI v0.5

Memory workflow:

1. Start Executive

2. Review project material

Example:

"Review HTG_layer1_data_dictionary.xlsx.
Identify unknown concepts, missing information,
and questions we need answered."


3. Executive discusses findings.

4. Request memory review:

/memory-review


5. Review generated proposal:

/memory-show


6. If correct:

/memory-approve


7. Verify:

/memory-status


Expected updates:

~/ExecutiveWorkspace/memory/open_questions.md

or

~/ExecutiveWorkspace/memory/project_state.md

or

~/ExecutiveWorkspace/memory/decision_log.md


The Executive should never silently modify memory.
All memory updates flow through proposals.
"""



# ============================================================
# END OF EXECUTIVE AI v0.5
# ============================================================