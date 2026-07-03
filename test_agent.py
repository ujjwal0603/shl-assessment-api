import os
from dotenv import load_dotenv
load_dotenv()

from schemas import ChatRequest, Message
from agent import process_chat

request = ChatRequest(
    messages=[
        Message(role="user", content="We need a solution for senior leadership.")
    ]
)

try:
    print("Testing API...")
    response = process_chat(request)
    print("\n--- Reply ---")
    print(response.reply)
    print("\n--- Recommendations ---")
    for r in response.recommendations:
        print(f"- {r.name} ({r.test_type}): {r.url}")
    print("\n--- End of Conversation ---")
    print(response.end_of_conversation)
except Exception as e:
    import traceback
    traceback.print_exc()
