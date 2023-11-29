import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_embedding(text: str, model="text-embedding-ada-002") -> list[float]:
    try:
        return openai.embeddings.create(input=[text], model=model).data[0].embedding
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        raise e


class OpenAIClient:
    def __init__(self):
        self.num_requests_completed = 0
        self.num_current_requests = 0

    def generate_embedding(self, text):
        self.num_current_requests += 1
        embedding = get_embedding(text)
        self.num_current_requests -= 1
        self.num_requests_completed += 1
        return embedding
