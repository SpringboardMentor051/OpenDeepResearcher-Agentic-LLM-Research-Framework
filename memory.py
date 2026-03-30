memory = []

def save_memory(query, result):
    memory.append({
        "query": query,
        "result": result
    })

def get_memory():
    return memory