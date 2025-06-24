# query_assistant.py
import openai, os
import time

openai.api_key = os.getenv("OPENAI_API_KEY")

# Use the assistant ID from create_assistant.py
assistant_id = "asst_ueLOB0oOsC8ZQkymnJ3nBkSj"

# Create a thread
thread = openai.beta.threads.create()
print("thread:", thread.id)

# Add a message to the thread
message = openai.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="What is Procore and what are its main features?"
)
print("message:", message.id)

# Run the assistant
run = openai.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant_id
)
print("run:", run.id)

# Wait for completion
while run.status != "completed":
    time.sleep(1)
    run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    print(f"status: {run.status}")

# Get the response
messages = openai.beta.threads.messages.list(thread_id=thread.id)
for msg in messages.data:
    if msg.role == "assistant":
        print("\nAssistant response:")
        print(msg.content[0].text.value)
        break 