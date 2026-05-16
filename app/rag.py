import os

from dotenv import load_dotenv
from groq import Groq

from app.retriever import search_assessments


# Load environment variables
load_dotenv()


# Initialize Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def is_vague_query(text):
    

    """
    Detect vague hiring queries
    """

    text = text.lower()

    vague_terms = [
        "assessment",
        "test",
        "hiring",
        "need assessment"
    ]

    important_keywords = [
        "developer",
        "engineer",
        "manager",
        "sales",
        "java",
        "python",
        "communication",
        "leadership",
        "analyst"
    ]

    if len(text.split()) < 4:
        return True

    if not any(
        keyword in text
        for keyword in important_keywords
    ):
        return True

    for term in vague_terms:

        if text.strip() == term:
            return True

    return False

def is_off_topic(text):

    """
    Detect unrelated non-SHL queries
    """

    off_topic_keywords = [
        "salary",
        "legal",
        "lawsuit",
        "tax",
        "football",
        "recipe",
        "movie",
        "weather",
        "firing employees"
    ]

    text = text.lower()

    for keyword in off_topic_keywords:

        if keyword in text:
            return True

    return False

def is_comparison_query(text):

    """
    Detect comparison queries
    """

    comparison_words = [
        "difference",
        "compare",
        "vs",
        "versus"
    ]

    text = text.lower()

    for word in comparison_words:

        if word in text:
            return True

    return False

def generate_reply(messages):

    """
    Main chatbot function
    """

    conversation_text = ""

    latest_user_message = ""

    for msg in messages:

        if msg["role"] == "user":

            conversation_text += f"User: {msg['content']}\n"

            latest_user_message = msg["content"]

        else:

            conversation_text += f"Assistant: {msg['content']}\n"

    # Refuse off-topic queries
    if is_off_topic(latest_user_message):

        return {
            "reply": "I can only help with SHL assessments and assessment recommendations.",
            "recommendations": [],
            "end_of_conversation": False
        }
    
    # Ask clarification if vague
    if is_vague_query(latest_user_message):

        return {
            "reply": "Could you share the role, seniority level, and important skills you are hiring for?",
            "recommendations": [],
            "end_of_conversation": False
        }

    # Handle comparison queries
    if is_comparison_query(latest_user_message):

        comparison_query = latest_user_message.replace(
            "difference between",
            ""
        )

        comparison_results = search_assessments(
            comparison_query,
            top_k=2
        )

        comparison_context = ""

        for item in comparison_results:

            comparison_context += f"""

            Assessment Name:
            {item['name']}

            Description:
            {item['description']}

            """

        comparison_prompt = f"""
        Compare these SHL assessments.

        User query:
        {latest_user_message}

        Assessment information:
        {comparison_context}

        Explain the differences clearly and briefly.
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": comparison_prompt
                }
            ],
            temperature=0.2
        )

        return {
            "reply": response.choices[0].message.content,
            "recommendations": [],
            "end_of_conversation": False
        }
    
    # Retrieve assessments
    search_query = f"""
    Full conversation:
    {conversation_text}

    Latest requirement:
    {latest_user_message}

    Include:
    - technical skills
    - personality assessments
    - communication skills
    - behavioral skills
    if requested by the user.
    """

    retrieved = search_assessments(
        search_query,
        top_k=5
    )

    # Build catalog context
    catalog_context = ""

    for item in retrieved:

        catalog_context += f"""

        Assessment Name:
        {item['name']}

        Description:
        {item['description']}

        URL:
        {item['url']}

        """

    # Build prompt
    prompt = f"""
    You are an SHL assessment recommendation assistant.

    STRICT RULES:
    - ONLY recommend assessments from the provided SHL catalog.
    - NEVER invent assessment names.
    - Keep responses concise and professional.
    - Recommend between 1 and 10 assessments.
    - Focus on role, skills, seniority, and hiring requirements.
    - Explain recommendations briefly.
    - Keep response under 150 words.

    Full conversation:
    {conversation_text}

    Retrieved SHL assessments:
    {catalog_context}

    IMPORTANT:
    - Use ONLY provided assessment names.
    - Do NOT mention assessments not present in retrieved results.

    Generate:
    1. Brief conversational response
    2. Why the assessments fit
    """

    # Call Groq LLM
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are an SHL assessment recommendation assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    reply_text = response.choices[0].message.content

    # Build recommendation array
    recommendations = []

    for item in retrieved:

        item_text = (
            item["name"] + " " +
            item["description"]
        ).lower()

        if any(word in item_text for word in [
            "personality",
            "behavior",
            "opq"
        ]):

            test_type = "Personality"

        elif any(word in item_text for word in [
            "cognitive",
            "ability",
            "reasoning"
        ]):

            test_type = "Cognitive"

        elif any(word in item_text for word in [
            "technical",
            "java",
            "python",
            "sql",
            "programming"
        ]):

            test_type = "Technical"

        else:

            test_type = "General"

        recommendations.append({
            "name": item["name"],
            "url": item["url"],
            "test_type": test_type
        })

    return {
        "reply": reply_text,
        "recommendations": recommendations,
        "end_of_conversation": False
    }