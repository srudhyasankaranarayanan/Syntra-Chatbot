
import sqlite3
import uuid
from pathlib import Path

import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


# -------------------- SETTINGS --------------------

st.set_page_config(
    page_title="Syntra ",
    page_icon="🧠",
    layout="wide"
)

MODEL = "gemma3:1b"
OLLAMA_URL = "http://localhost:11434"

# Keep this filename unchanged to preserve existing chats and memory.
DB_FILE = Path(__file__).with_name("cortex_memory.db")


# -------------------- DATABASE --------------------

def connect():
    return sqlite3.connect(DB_FILE)


def setup_database():
    with connect() as db:

        db.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY(chat_id) REFERENCES chats(chat_id)
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS profile_memory (
                id INTEGER PRIMARY KEY CHECK(id = 1),
                notes TEXT NOT NULL DEFAULT ''
            )
        """)

        db.execute("""
            INSERT OR IGNORE INTO profile_memory (id, notes)
            VALUES (1, '')
        """)


def new_chat():
    chat_id = str(uuid.uuid4())

    with connect() as db:
        db.execute(
            "INSERT INTO chats (chat_id, title) VALUES (?, ?)",
            (chat_id, "New chat")
        )

    return chat_id


def list_chats():
    with connect() as db:
        return db.execute("""
            SELECT chat_id, title
            FROM chats
            ORDER BY updated_at DESC
        """).fetchall()


def read_messages(chat_id):
    with connect() as db:
        rows = db.execute("""
            SELECT role, content
            FROM messages
            WHERE chat_id = ?
            ORDER BY id
        """, (chat_id,)).fetchall()

    return [
        {"role": role, "content": content}
        for role, content in rows
    ]


def save_message(chat_id, role, content):
    with connect() as db:
        db.execute("""
            INSERT INTO messages (chat_id, role, content)
            VALUES (?, ?, ?)
        """, (chat_id, role, content))

        db.execute("""
            UPDATE chats
            SET updated_at = CURRENT_TIMESTAMP
            WHERE chat_id = ?
        """, (chat_id,))


def rename_first_chat(chat_id, first_message):
    title = " ".join(first_message.strip().split())[:42]

    if len(first_message.strip()) > 42:
        title += "..."

    with connect() as db:
        db.execute("""
            UPDATE chats
            SET title = ?
            WHERE chat_id = ? AND title = 'New chat'
        """, (title or "New chat", chat_id))


def get_saved_memory():
    with connect() as db:
        row = db.execute(
            "SELECT notes FROM profile_memory WHERE id = 1"
        ).fetchone()

    return row[0] if row else ""


def save_memory(notes):
    with connect() as db:
        db.execute("""
            UPDATE profile_memory
            SET notes = ?
            WHERE id = 1
        """, (notes,))


def delete_chat(chat_id):
    with connect() as db:
        db.execute(
            "DELETE FROM messages WHERE chat_id = ?",
            (chat_id,)
        )

        db.execute(
            "DELETE FROM chats WHERE chat_id = ?",
            (chat_id,)
        )


def delete_all_chats():
    with connect() as db:
        db.execute("DELETE FROM messages")
        db.execute("DELETE FROM chats")


setup_database()


# -------------------- AI MODEL --------------------

@st.cache_resource
def get_model():
    return ChatOllama(
        model=MODEL,
        base_url=OLLAMA_URL,
        temperature=0.5
    )


def reply_to_user(chat_id, user_text):
    model = get_model()
    saved_memory = get_saved_memory()

    # The current question is already saved in the database.
    # Exclude it here to avoid sending it twice to the model.
    history = read_messages(chat_id)[:-1]

    system_text = f"""
You are Syntra, a friendly and helpful personal AI assistant.

Answer the user's questions directly in clear, simple language.

PERSONAL INFORMATION ABOUT THE USER:
{saved_memory if saved_memory else "No personal details have been saved yet."}

Instructions:
- Use personal information only when relevant.
- Do not invent personal facts.
- If you do not know something, say so.
- Answer general questions normally.
- A new chat is a fresh conversation.
- You may use relevant long-term personal information from previous chats.
- Be friendly, helpful and clear.
"""

    prompt_messages = [
        SystemMessage(content=system_text)
    ]

    # Keep the latest 10 messages as current chat context.
    for item in history[-10:]:

        if item["role"] == "user":
            prompt_messages.append(
                HumanMessage(content=item["content"])
            )

        elif item["role"] == "assistant":
            prompt_messages.append(
                AIMessage(content=item["content"])
            )

    prompt_messages.append(
        HumanMessage(content=user_text)
    )

    result = model.invoke(prompt_messages)

    return result.content


# -------------------- PERSONAL MEMORY --------------------

def refresh_personal_memory(user_text):
    """
    Update a small personal profile using useful facts
    explicitly shared by the user.
    """

    model = get_model()
    old_memory = get_saved_memory()

    instruction = f"""
You maintain Syntra's short personal memory.

CURRENT SAVED NOTES:
{old_memory if old_memory else "(empty)"}

NEW MESSAGE FROM THE USER:
{user_text}

Update the notes only if the user explicitly shared a useful
personal fact, preference, goal, study detail or ongoing project.

RULES:
- Keep useful existing notes.
- Do not guess or invent facts.
- Ignore general questions and temporary conversation.
- Do not save passwords, API keys or other secrets.
- Keep the result short, clear and in bullet points.
- If there is no useful new information, return the existing notes.
- Return only the updated notes.
- Do not add an introduction.
"""

    result = model.invoke([
        HumanMessage(content=instruction)
    ])

    updated = result.content

    if isinstance(updated, list):
        updated = "\n".join(
            str(part.get("text", ""))
            if isinstance(part, dict)
            else str(part)
            for part in updated
        )

    updated = str(updated).strip()

    if updated:
        save_memory(updated)


# -------------------- PASTEL DESIGN --------------------

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #fbf3ff,
        #fff1f5,
        #fff9e8
    );
    color: #493653;
}

.main .block-container {
    max-width: 1050px;
    padding-top: 1.8rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #eadcff,
        #f8dce9 65%,
        #ffedbd
    );
    border-right: 2px solid #e6c36b;
}

h1 {
    color: #8755a8 !important;
}

h2, h3 {
    color: #a45d91 !important;
}

[data-testid="stChatMessage"] {
    background: rgba(255,255,255,.82);
    border: 1px solid #ead5f5;
    border-radius: 16px;
    padding: 12px;
}

.stButton > button {
    background: linear-gradient(
        120deg,
        #d8b9ef,
        #f3c1d5
    );
    color: #50345c;
    border: 1px solid #e6c6ed;
    border-radius: 11px;
    font-weight: 600;
}

.stButton > button:hover {
    border-color: #d7a7df;
    color: #50345c;
}

[data-testid="stChatInput"] {
    border: 1px solid #d8b9e8;
    border-radius: 15px;
}

[data-testid="stExpander"] {
    background: rgba(255,255,255,.65);
    border: 1px solid #ead5f5;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)


# -------------------- SIDEBAR --------------------

st.sidebar.title("🧠 Syntra")
st.sidebar.caption("Your Intelligent AI Companion")

if st.sidebar.button(
    "＋ Start a new chat",
    use_container_width=True
):
    st.session_state.chat_id = new_chat()
    st.rerun()


# Load all conversations.
chats = list_chats()

if not chats:
    st.session_state.chat_id = new_chat()
    st.rerun()


chat_ids = [item[0] for item in chats]
chat_titles = {item[0]: item[1] for item in chats}


if (
    "chat_id" not in st.session_state
    or st.session_state.chat_id not in chat_ids
):
    st.session_state.chat_id = chat_ids[0]


# Conversation history selector.
chosen_id = st.sidebar.selectbox(
    "Your chat history",
    options=chat_ids,
    index=chat_ids.index(st.session_state.chat_id),
    format_func=lambda chat_id: chat_titles[chat_id]
)


if chosen_id != st.session_state.chat_id:
    st.session_state.chat_id = chosen_id
    st.rerun()


# Delete selected conversation.
if st.sidebar.button(
    "Delete selected chat",
    use_container_width=True
):
    delete_chat(st.session_state.chat_id)
    remaining_chats = list_chats()

    if remaining_chats:
        st.session_state.chat_id = remaining_chats[0][0]
    else:
        st.session_state.chat_id = new_chat()

    st.rerun()


st.sidebar.divider()

# Personal memory section.
st.sidebar.subheader("🌷 Saved memory")

memory_text = get_saved_memory()

if memory_text:
    st.sidebar.success("Syntra has saved notes")
else:
    st.sidebar.info("No personal notes saved yet")


with st.sidebar.expander("View or edit memory"):

    edited_memory = st.text_area(
        "Information Syntra can use in new chats",
        value=memory_text,
        height=180,
        key="memory_notes_editor"
    )

    if st.button(
        "Save memory notes",
        use_container_width=True
    ):
        save_memory(edited_memory)
        st.success("Memory updated!")
        st.rerun()


if st.sidebar.button(
    "Forget saved memory",
    use_container_width=True
):
    save_memory("")
    st.rerun()


st.sidebar.divider()

if st.sidebar.button(
    "Delete all chats",
    use_container_width=True
):
    delete_all_chats()
    st.session_state.chat_id = new_chat()
    st.rerun()


st.sidebar.caption(f"Model: {MODEL}")
st.sidebar.caption("Runs locally with Ollama")


# -------------------- MAIN CHAT --------------------

st.title("Syntra")

st.markdown(
    "Your Intelligent AI Companion — Think, Learn, Explore."
)

st.caption(
    "Past chats are saved. Useful personal notes can carry into a new chat."
)


active_chat = st.session_state.chat_id

messages = read_messages(active_chat)


# Display previous messages.
for message in messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input.
question = st.chat_input("Ask Syntra anything...")


if question:

    # Give the first conversation a suitable title.
    if not messages:
        rename_first_chat(active_chat, question)

    # Save the user's question.
    save_message(active_chat, "user", question)

    with st.chat_message("user"):
        st.markdown(question)

    # Generate AI response.
    with st.chat_message("assistant"):

        with st.spinner("Syntra is thinking..."):

            try:
                answer = reply_to_user(
                    active_chat,
                    question
                )

                st.markdown(answer)

                # Save assistant response.
                save_message(
                    active_chat,
                    "assistant",
                    answer
                )

                # Update long-term memory.
                try:
                    refresh_personal_memory(question)

                except Exception:
                    pass

            except Exception as error:

                st.error(
                    "Syntra could not connect to Ollama. "
                    "Check that Ollama is running and the model is installed. "
                    f"Details: {error}"
                )

    st.rerun()
