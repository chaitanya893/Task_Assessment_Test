import requests

def ask_ai(context: str, question: str):

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": f"""
Answer based only on context.

Context:
{context}

Question:
{question}
""",
                "stream": False
            }
        )

        data = response.json()

        if "response" in data:
            return data["response"]

        return "No AI response"

    except Exception as e:
        print("AI ERROR:", e)
        return "AI failed"