import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

SYSTEM_PROMPT = """
You are an SHL assessment recommendation assistant.

You ONLY recommend assessments from the SHL catalog.

Ask clarification questions when needed.
Never hallucinate assessments.
"""

def generate_reply(user_message, retrieved_assessments):

    catalog_context = "\n".join([
        f"""
        Name: {a['name']}
        Type: {a['test_type']}
        Description: {a['description']}
        URL: {a['url']}
        """
        for a in retrieved_assessments
    ])

    prompt = f"""
    {SYSTEM_PROMPT}

    USER QUERY:
    {user_message}

    RETRIEVED ASSESSMENTS:
    {catalog_context}

    Generate a helpful response.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    fake_results = [
        {
            "name": "Java 8 (New)",
            "test_type": "Technical",
            "description": "Java assessment",
            "url": "https://example.com"
        }
    ]

    reply = generate_reply(
        "Hiring a Java backend developer",
        fake_results
    )

    print(reply)