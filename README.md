A local AI email agent where everything runs offline, including the LLM and the mail server.

Powered by LangGraph + Ollama, the agent can:
- List all unread emails (with UIDs, subjects, dates, senders)
- Summarize the content of a specific email (by UID)

It uses a local mail server (localmail package), but you can also connect it to any online IMAP server if needed.
This could a good starting point for anyone interested in building local AI applications. You can download the repo and execute `uv run main.py` to get started

Graph:

<img width="338" height="432" alt="Untitled-2024-03-18-2023(8)" src="https://github.com/user-attachments/assets/c2047ffa-0b2d-417f-ac82-c2eeba255b13" />

