# query_assistant.py
import openai, os

openai.api_key = os.getenv("OPENAI_API_KEY")

# Replace with your actual assistant ID
assistant_id = "your_assistant_id_here"

def ask_question(question):
    thread = openai.beta.threads.create()
    openai.beta.threads.messages.create(
        thread_id=thread.id, role="user",
        content=question
    )
    run = openai.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant_id
    )
    msg = openai.beta.threads.messages.list(thread.id).data[0]
    return msg.content[0].text.value

# Example usage
if __name__ == "__main__":
    question = "How do I refresh an OAuth token?"
    answer = ask_question(question)
    print(f"Q: {question}")
    print(f"A: {answer}") 