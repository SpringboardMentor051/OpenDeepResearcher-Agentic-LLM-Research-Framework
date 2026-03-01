"""
Simple LLM Integration with LM Studio
This module provides a simple interface to query the LLM running in LM Studio.
"""

from openai import OpenAI


class LLMPlanner:
    """Simple planner that integrates with LM Studio LLM."""
    
    def __init__(self, base_url="http://localhost:1234/v1", model="mistralai/ministral-3-3b"):
        """
        Initialize the LLM client.
        
        Args:
            base_url: The LM Studio server URL (default: http://localhost:1234/v1)
            model: The model identifier
        """
        self.client = OpenAI(
            base_url=base_url,
            api_key="lm-studio"  # LM Studio doesn't require a real API key
        )
        self.model = model
    
    def ask(self, prompt, temperature=0.7, max_tokens=500):
        """
        Send a prompt to the LLM and get a response.
        
        Args:
            prompt: The question or prompt to send to the LLM
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            The LLM's response as a string
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
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
    
    # Example prompts
    prompts = [
        "What is the capital of France?",
        "Explain about NVIDIA Chips.",
        "Write a haiku about programming."
    ]
    
    print("=" * 60)
    print("LLM Planner - Testing with LM Studio")
    print("=" * 60)
    
    for prompt in prompts:
        print(f"\n📝 Prompt: {prompt}")
        print("-" * 60)
        response = planner.ask(prompt)
        print(f"🤖 Response: {response}")
        print("-" * 60)
    
    # Interactive mode
    print("\n" + "=" * 60)
    print("Interactive Mode - Type your questions (or 'quit' to exit)")
    print("=" * 60)
    
    while True:
        user_input = input("\n❓ Your question: ")
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if user_input.strip():
            response = planner.ask(user_input)
            print(f"\n🤖 Response: {response}")