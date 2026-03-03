#Simple LLM Integration with LM Studio

from openai import OpenAI

class LLMPlanner:
    
    def __init__(self, base_url="http://localhost:1234/v1", model="mistralai/ministral-3-3b"):
        
        self.client = OpenAI(
            base_url=base_url,
            api_key="lm-studio"
        )
        self.model = model
    
    def ask(self, system_prompt, query, temperature=0.7, max_tokens=500):
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"


# Example usage
if __name__ == "__main__":
    # Create the planner instance
    planner = LLMPlanner()
    
    # Define system prompt for AI researcher
    system_prompt = """You are an expert AI researcher with deep knowledge in machine learning, data science, and artificial intelligence. 
    
Your responsibilities:
- Analyze complex research questions thoroughly
- Provide evidence-based, accurate information
- Structure your responses in a clear, organized manner
- Explain technical concepts in both simple and detailed ways
- Identify gaps in current knowledge and suggest future research directions
- Cite relevant methodologies and best practices

Response Structure:
1. **Summary**: Brief overview of the answer (2-3 sentences)
2. **Key Points**: Main findings or concepts (bullet points)
3. **Explanation**: Detailed explanation of each key point
4. **Implications**: Practical applications and relevance
5. **References**: Related concepts or areas for further study

Always maintain scientific rigor and provide balanced perspectives."""

    # Interactive mode with prompt + query separation
    print("\n" + "=" * 60)
    print("AI Researcher Mode - Knowledge Q&A")
    print("=" * 60)
    
    while True:
        query = input("\n❓ Your research question: ")
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if query.strip():
            print("\n🔍 Researching...")
            response = planner.ask(system_prompt, query)
            print(f"\n🤖 Response:\n{response}")
            print("-" * 60)