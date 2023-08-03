from openai import GPT
from openai.api_resources.completion import Completion

class GPTService:
    def __init__(self):
        self.gpt = GPT(engine="text-davinci-003")  # Specify your engine here

    def generate(self, prompt):
        response = Completion.create(engine=self.gpt, prompt=prompt, max_tokens=100)  # Specify your parameters here
        return response.choices[0].text.strip()
