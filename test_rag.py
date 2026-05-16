from app.rag import generate_reply


messages = [
    {
        "role": "user",
        "content": "Hiring Java backend developer with communication skills"
    }
]


response = generate_reply(messages)

print(response)
