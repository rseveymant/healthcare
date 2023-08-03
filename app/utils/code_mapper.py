from mantium_client.api_client import MantiumClient
from mantium_spec.api.applications_api import ApplicationsApi
from dotenv import load_dotenv
import os

class ICD10Generator:
    def __init__(self, mantium_client_id, mantium_client_secret, gpt_model):
        # Initialize Mantium client
        self.mantium_client = MantiumClient(mantium_client_id, mantium_client_secret)
        self.apps_api = ApplicationsApi(self.mantium_client)
        
        # Initialize GPT model
        self.gpt_model = gpt_model

    def generate(self, input_text):
        print(input_text)
        # Step 1: Use Mantium's RAG model to generate ICD-10 candidates
        rag_candidates = self.apps_api.query_application('64cbf1271dbc4547923267cd', dict(query=input_text, retriever_top_k=1))

        # Step 2: Refine candidates using GPT model
        print(rag_candidates['documents'][0]['content'])
        refinement_prompt = f"Consider the original summary: {input_text} and the top result {rag_candidates['documents'][0]['content']} and return ALL relevant and correct ICD-10 code"
        
        #Step 2: Refine candidates using GPT model
        refined_answer = self.gpt_model.generate(refinement_prompt)

        # Step 3: Return refined answer
        return refined_answer
