import json

from local_agent import LocalAgent
from local_mail_server import LocalMailServer

if __name__ == "__main__":
    print("Starting local mail server")
    local_mail_server = LocalMailServer()
    local_mail_server.start()
    with open("emails.json") as email_file:
        emails = json.load(email_file)
        for email in emails:
            local_mail_server.send_email(email)
    print("Starting Agent")
    local_agent = LocalAgent()

    print('Type an instruction or "quit".\n')
    while True:
        user_message = input('> ')
        if user_message.lower() == 'quit':
            break
        local_agent.invoke(user_message)
    print("Stopping Agent")
    local_mail_server.stop_server()
