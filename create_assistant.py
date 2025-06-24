# create_assistant.py
import openai, os

openai.api_key = os.getenv("OPENAI_API_KEY")

# Use the file ID from the upload (replace with your actual file ID)
file_id = "file-T8SNWWqVN4As6Nrvx2VXm2"  # From create_store.py output

try:
    # Try creating assistant with code_interpreter tool and file_ids
    assistant = openai.beta.assistants.create(
        name="Procore QA",
        model="gpt-4o-mini",
        tools=[{"type": "code_interpreter"}],
        tool_resources={"code_interpreter": {"file_ids": [file_id]}},
        instructions="Answer using Procore docs; cite filename metadata."
    )
    print("assistant:", assistant.id)
    print("files attached during creation")
    
except Exception as e:
    print("Error creating assistant with files:", e)
    print("Creating assistant without files...")
    
    # Create assistant without files
    assistant = openai.beta.assistants.create(
        name="Procore QA",
        model="gpt-4o-mini",
        tools=[{"type": "code_interpreter"}],
        instructions="Answer using Procore docs; cite filename metadata."
    )
    print("assistant:", assistant.id)
    print("Note: Files need to be attached separately") 