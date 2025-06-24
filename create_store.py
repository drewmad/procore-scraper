# create_store.py
import openai, os, time

openai.api_key = os.getenv("OPENAI_API_KEY")

# 2-A upload the file
file_id = openai.files.create(
    file=open("openai_payload.json", "rb"),
    purpose="assistants"
).id
print("file:", file_id)

# 2-B create the vector-store
store = openai.beta.vector_stores.create(
    name="procore-docs",
    file_ids=[file_id],
    metadata={"source": "procore"}
)
print("vector_store:", store.id)

# 2-C block until indexing finished (optional)
while store.status != "completed":
    time.sleep(5)
    store = openai.beta.vector_stores.retrieve(store.id)
print("✓ ready") 