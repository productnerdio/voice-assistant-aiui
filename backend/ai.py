import logging
import os
import httpx
import time
import openai

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

AI_COMPLETION_MODEL = os.getenv("AI_COMPLETION_MODEL", "gpt-4-turbo-preview")
LANGUAGE = os.getenv("LANGUAGE", "en")
INITIAL_PROMPT = f"""
You are developing a knowledge base assistant to provide helpful responses to users' questions based on a collection of documents in Markdown format. Your goal is to design the assistant to be reliable and informative, providing accurate answers whenever possible.

The assistant should follow these guidelines:

1. Knowledge Base Input: The assistant will be provided with a set of Markdown documents containing valuable information. These documents cover a wide range of topics and are structured to facilitate easy retrieval of information.

2. User Queries: Users will interact with the assistant by asking questions related to the topics covered in the knowledge base documents. These questions can vary in complexity and specificity.

3. Response Generation: When a user submits a question, the assistant should analyze the question and search for relevant information within the knowledge base documents. It should then generate a response that directly addresses the user's query, providing accurate and concise information.

4. Handling Unknown Queries: If the assistant cannot find relevant information to answer a user's question within the knowledge base documents, it should respond politely by indicating that it doesn't have the necessary information to provide a response.

5. Accuracy and Reliability: The assistant should prioritize accuracy and reliability in its responses, ensuring that the information provided is up-to-date and factually correct. It should avoid making speculative or uncertain statements.

6. User Experience: The assistant should aim to enhance the user experience by providing clear and understandable responses in a timely manner. It should use language that is friendly, professional, and easily comprehensible to users.

7. Continuous Improvement: As users interact with the assistant and ask new questions, the assistant should continuously learn and improve its knowledge base. It should be capable of incorporating new information and updates to ensure that its responses remain relevant and accurate over time.

8. Language Precision: You will always respond with full words and not the abbreviated text that is displayed in the knowledge documents.

9. Always replace bullet points (*) with numbers, such as 1, 2, 3 etc.

Always provide your responses in the language that corresponds to the ISO-639-1 code: {LANGUAGE}.
"""

FLOWISE_API_URL = os.getenv("FLOWISE_API_URL")
FLOWISE_API_KEY = os.getenv("FLOWISE_API_KEY")


async def get_completion(user_prompt, conversation_thus_far):
    if _is_empty(user_prompt):
        raise ValueError("Empty user prompt received")

    start_time = time.time()

    # Prepare the request payload
    request_payload = {
        "question": user_prompt,
        "messages": [{"role": "user", "content": user_prompt}]
    }

    # Asynchronous HTTP request using httpx
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {FLOWISE_API_KEY}"}
            response = await client.post(FLOWISE_API_URL, json=request_payload, headers=headers, timeout=15.0)
            if response.status_code == 200:
                result = response.json()
                completion = result.get("text", "")
                elapsed_time = time.time() - start_time
                logging.info(f"Response received from Flowise GPT bot in {elapsed_time:.2f} seconds")
                logging.info(f"Flowise GPT bot response: {completion}")
                return completion
            else:
                logging.error(f"Error occurred while calling Flowise GPT bot: {response.text}")
                raise Exception("Error calling Flowise GPT bot")
        except httpx.RequestError as e:
            logging.error(f"Network-related error when calling Flowise GPT bot: {e}")
            raise Exception(f"Network-related error: {e}")

def _is_empty(user_prompt: str):
    return not user_prompt or user_prompt.isspace()