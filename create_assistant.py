# create_assistant.py
import openai, os

openai.api_key = os.getenv("OPENAI_API_KEY")

# Get the vector store ID (you'll need to replace this with your actual store ID)
store_id = "your_vector_store_id_here"  # Replace with actual ID from create_store.py

assistant = openai.beta.assistants.create(
    name="Procore QA",
    model="gpt-4o-mini",
    tools=[{"type": "retrieval", "vector_store_ids": [store_id]}],
    instructions="Answer using Procore docs; cite sha1 metadata."
)
print("assistant:", assistant.id) 