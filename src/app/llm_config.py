import sys
import os
sys.path.append(os.path.dirname(__file__))

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def get_llm(temperature: float = 0) -> ChatOpenAI:
    """Get configured LLM instance."""
    return ChatOpenAI(
        base_url=os.getenv("LLM_BASE_URL"),
        api_key=os.getenv("LLM_API_KEY"),
        model=os.getenv("LLM_MODEL_NAME"),
        temperature=temperature
    )

def test_llm():
    """Test LLM configuration."""
    llm = get_llm()
    response = llm.invoke("Say 'LLM config working' if you can read this.")
    print(f"LLM Test: {response.content}")
    return True

if __name__ == "__main__":
    test_llm()
