from ollama import chat

def ask_llm(query: str, llm, temp: float) -> str:
    if not llm:
        raise Exception("LLM Unavaible")

    system_prompt = """"""
    assitant_prompt = """"""
    user_prompt = query
    response = chat(model='qwen3:8b', messages=[
    {
        'role': 'system',
        'content': system_prompt
    },
    {
        'role': 'user',
        'content': user_prompt
    },
    {
        'role': 'assistant',
        'content': assitant_prompt
    }
    ], options={"temperature": temp})
    
    return response.message.content
