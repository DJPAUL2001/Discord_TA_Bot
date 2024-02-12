import os
from time import sleep
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    # defaults to
    api_key=os.getenv("OPENAI_KEY_GRADING")
)

print(os.getcwd())
# Step 1: Create an assistant
# Upload a file with an "assistants" purpose
file = client.files.create(
    file=open("Student Guide 1.3.docx", "rb"), purpose="assistants"
)

# Add the file to the assistant
assistant = client.beta.assistants.create(
    instructions="""You are a high school computer science teacher. 
    Your responsibility is to leave student feedback on Makecode assignments!
    Read the instructions for all the student activities, 
    and leave constructive feedback to the code the students shares with you.
    """,
    model="gpt-3.5-turbo-0125",
    tools=[{"type": "retrieval"}],
    file_ids=[file.id],
)

# Step 2: Create a Thread
# A Thread represents a conversation. We recommend creating one
# Thread per user as soon as the user initiates the conversation.
# Pass any user-specific context and files in this thread by
# creating Messages.
thread = client.beta.threads.create()


def ask_one_question(client, thread):
    # Step 3: Add a Message to a Thread
    # A message contains the user's text, and optionally,
    # any files that the user uploads.
    user_input = input("What's your question? ")
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input,
        file_ids=[file.id],
    )

    # Step 4: Run the Assistant
    # For the Assistant to respond to the user message, you need to create a Run.
    # This makes the Assistant read the Thread and decide whether to calll tools
    # or simply user the model to best answer the user query. As the run
    # progresses, the assistant appends Messages to the thread with the role="assistant".
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="The user is a students who needs feedback on his Makecode python code.",
    )

    # Step 5: Display the Assistant's Response
    # This creates a Run in a queued status. You can periodically
    # retrieve the Run to check on its status to see if it has moved to completed.

    print(run.status)
    while run.status != "completed":
        sleep(1)
        print("Waiting for the Assistant to respond...")
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print(run.status)

    # Once the Run completes, you can retrieve the
    # Messages added by the Assistant to the Thread.
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    for m in messages:
        print(m.role + ": " + str(m.content[0].text))


while True:
    ask_one_question(client, thread)
