# Syntra AI – Your Intelligent AI Companion

Syntra is a locally running AI chatbot built using Streamlit, Ollama, and Gemma 3:1B. It provides a conversational experience with chat history and long-term personal memory.

Users can start new conversations, revisit previous chats, and save personal information that Syntra can use in future conversations.

## Features

- **AI Chatbot:** Answers general questions using Gemma 3:1B.
- **New Conversations:** Start a fresh chat whenever needed.
- **Chat History:** Automatically saves previous conversations.
- **Long-Term Memory:** Remembers useful personal information across different chats.
- **Memory Management:** View, edit, and delete saved memory.
- **Chat Management:** Select or delete individual conversations and clear all chat history.
- **Pastel UI:** Simple interface with purple, pink, and golden-yellow colours.
- **Local Execution:** Runs locally using Ollama.

## Technologies Used

- Python
- Streamlit
- Ollama
- Gemma 3:1B
- LangChain
- SQLite

## Project Structure

```text
Syntra/
│
├── app.py
├── requirements.txt
└── cortex_memory.db
```

The SQLite database is created automatically when the application runs.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone: https://github.com/srudhyasankaranarayanan/Syntra-Chatbot
```

Navigate to the project folder:

```bash
cd Syntra
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

Download and install Ollama from:

https://ollama.com/

### 5. Download the Gemma Model

Run:

```bash
ollama pull gemma3:1b
```

### 6. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at:

```text
http://localhost:8501
```

## How Syntra Works

1. The user enters a question in the chat interface.
2. Syntra processes the question using Gemma 3:1B through Ollama.
3. The conversation is stored in an SQLite database.
4. Useful personal details are extracted and saved as long-term memory.
5. When the user starts a new chat, Syntra can use relevant saved information to provide personalised responses.

## Memory Management

Syntra maintains two types of information:

- **Conversation History:** Stores messages separately for each chat.
- **Long-Term Memory:** Stores useful personal details that can be used across conversations.

Users can view, edit, or clear their saved personal memory through the sidebar.

## Important Notes

- Ollama must be running while using Syntra.
- The Gemma 3:1B model must be downloaded before starting the application.
- Syntra runs locally and does not require an external AI API key.
- Chat history and memory are stored locally in SQLite.

## Screenshots
<img width="1474" height="677" alt="image" src="https://github.com/user-attachments/assets/28c335b3-ace8-47d4-ae4b-aa44e0277f88" />
<img width="1369" height="598" alt="image" src="https://github.com/user-attachments/assets/7d0d537f-e5c6-4e76-8946-dce8ba4f64f6" />
<img width="1476" height="598" alt="image" src="https://github.com/user-attachments/assets/0e30a6b4-4279-4490-8688-adad413d4cc3" />

## Future Enhancements

- Voice input and output.
- File upload and document understanding.
- Customisable chatbot themes.
- Improved memory retrieval.
- Export and download conversations.
- Support for additional AI models.

## Author

**Srudhya Sankaranarayanan**
---

**Syntra AI – Think. Learn. Explore.**
