from mantium_client.api_client import MantiumClient
from mantium_spec.api.applications_api import ApplicationsApi
from dotenv import load_dotenv
import os
import re

class CodeReview:
    def __init__(self, mantium_client_id, mantium_client_secret, gpt_model):
        # Initialize Mantium client
        self.mantium_client = MantiumClient(mantium_client_id, mantium_client_secret)
        self.apps_api = ApplicationsApi(self.mantium_client)
        
        # Initialize GPT model
        self.gpt_model = gpt_model

    def review(self, billing_codes, medical_data):
        correct_codes = set()
        mismatched_codes = []
        gpt_outputs = {}  # Store GPT outputs for each field
        
        # Iterate through the fields and make a call for each one
        for field in ['diagnosis', 'procedures', 'medical_history', 'clinical_notes']:
            print(medical_data[field])
            
            # Query Mantium's RAG model
            rag_candidates = self.apps_api.query_application('64cc1bcca95c216d0358e859', dict(query=medical_data[field], retriever_top_k=4))
            print(rag_candidates)
            
            # Refine candidates using GPT model
            refinement_prompt = f"Consider the original summary: {medical_data[field]} and the top result from the vector database: {rag_candidates['documents'][0]['content']} and return ALL relevant and correct ICD-10 code"
            print(refinement_prompt)
            refined_answer = self.gpt_model.generate(refinement_prompt)
            print(refined_answer)

            # Store the full refined answer for this field
            gpt_outputs[field] = refined_answer

            # Extract codes from the refined answer
            codes_from_refined_answer = re.findall(r'\b[A-Z][0-9.]+\b', refined_answer)
            
            # Consider parent codes as well, e.g., I21 for I21.09
            parent_codes = {code.split('.')[0] for code in codes_from_refined_answer}
            correct_codes |= set(codes_from_refined_answer) | parent_codes
            print(correct_codes)

        # Compare the generated codes with the submitted billing codes
        errors = []
        for code in billing_codes:
            if code not in correct_codes:
                errors.append(f"Error: Code {code} is not relevant to the provided information.")
                mismatched_codes.append(code)

        return errors, gpt_outputs, mismatched_codes, list(correct_codes)