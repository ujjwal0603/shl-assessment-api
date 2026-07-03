import os
from dotenv import load_dotenv
load_dotenv()

try:
    from google.genai import client
    c = client.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
    models = c.models.list()
    print("Available models:")
    for m in models:
        print(m.name)
except Exception as e:
    import traceback
    traceback.print_exc()
