import json
import os
from typing import TypedDict

from dotenv import load_dotenv
from imap_tools import MailBoxUnencrypted, AND
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

load_dotenv()

IMAP_HOST = os.getenv('IMAP_HOST')
IMAP_PORT = os.getenv('IMAP_PORT')
IMAP_USER = os.getenv('IMAP_USER')
IMAP_PASSWORD = os.getenv('IMAP_PASSWORD')

CHAT_MODEL = 'qwen3:8b'


class ChatState(TypedDict):
    messages: list


def connect():
    mail_box = MailBoxUnencrypted(host=IMAP_HOST, port=IMAP_PORT)
    mail_box.login(username=IMAP_USER, password=IMAP_PASSWORD)
    return mail_box


@tool
def list_unread_emails():
    """Return a bullet list of every UNREAD message's UID, subject, date and sender"""

    print("List Unread Emails Tool called")

    with connect() as mb:
        unread = list(mb.fetch(criteria=AND(seen=False), headers_only=True, mark_seen=False))
    if not unread:
        return 'You have no unread messages.'
    response = json.dumps([
        {
            'uid': mail.uid,
            'date': mail.date.astimezone().strftime('%Y-%m-%d %H:%M'),
            'subject': mail.subject,
            'sender': mail.from_
        } for mail in unread
    ])

    return response


@tool
def summarize_email(uid):
    """Summarize a single e-mail given its IMAP UID. Return a short summary of the e-mail's content/body
    in a plain text"""
    print("Summarize Email Tool called on ", uid)

    with connect() as mb:
        mail = next(mb.fetch(AND(uid=uid), mark_seen=False), None)

    if not mail:
        return f"could not summarize email with uid {uid}"

    prompt = (
        "Summarize this e-mail concisely:\n\n"
        f"Subject: {mail.subject}\n"
        f"Sender: {mail.from_}\n"
        f"Date: {mail.date}\n\n"
        f"{mail.text or mail.html}"
    )

    return raw_llm.invoke(prompt).content


llm = init_chat_model(CHAT_MODEL, model_provider='ollama')
llm = llm.bind_tools([list_unread_emails, summarize_email])

raw_llm = init_chat_model(CHAT_MODEL, model_provider='ollama')


def llm_node(state):
    response = llm.invoke(state['messages'])
    return {'messages': state['messages'] + [response]}


def router(state):
    last_message = state['messages'][-1]
    return 'tools' if getattr(last_message, 'tool_calls', None) else 'end'


tool_node = ToolNode([list_unread_emails, summarize_email])


def tools_node(state):
    result = tool_node.invoke(state)

    return {
        'messages': state['messages'] + result['messages']
    }


class LocalAgent:

    def __init__(self):
        graph = StateGraph(ChatState)
        graph.add_node('llm', llm_node)
        graph.add_node('tools', tools_node)
        graph.add_edge(START, 'llm')
        graph.add_edge('tools', 'llm')
        graph.add_conditional_edges('llm', router, {'tools': 'tools', 'end': END})
        self.agent = graph.compile()

        self.state = {'messages': []}

    def invoke(self, user_message):
        self.state['messages'].append({'role': 'user', 'content': user_message})
        self.state = self.agent.invoke(self.state)
        print(self.state['messages'][-1].content)
