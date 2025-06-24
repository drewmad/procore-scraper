# interactive_query.py
import openai, os, time

openai.api_key = os.getenv("OPENAI_API_KEY")

# Use the assistant ID from create_assistant.py
assistant_id = "asst_ueLOB0oOsC8ZQkymnJ3nBkSj"

def ask_question(question):
    """Ask a question to the Procore Assistant"""
    # Create a thread
    thread = openai.beta.threads.create()
    
    # Add the message to the thread
    message = openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question
    )
    
    # Run the assistant
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )
    
    # Wait for completion
    while run.status != "completed":
        time.sleep(1)
        run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status == "failed":
            return f"Error: {run.last_error}"
    
    # Get the response
    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    for msg in messages.data:
        if msg.role == "assistant":
            return msg.content[0].text.value
    
    return "No response received"

def main():
    print("🤖 Procore Documentation Assistant")
    print("Ask questions about Procore features, API, or documentation.")
    print("Type 'quit' or 'exit' to stop.\n")
    
    while True:
        try:
            question = input("❓ Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            print("🤔 Thinking...")
            answer = ask_question(question)
            print(f"\n💡 Answer:\n{answer}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    main() 