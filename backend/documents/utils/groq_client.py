import json
import re
import time
import logging
import groq
from django.conf import settings
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GroqClient:
    SYSTEM_PROMPT = """
    You are an insurance policy expert. Respond in JSON format with:
    - "answer": Concise answer to the question
    - "relevant_clauses": List of clauses with:
        - "clause_text": Exact text from document
        - "document_id": Source document
        - "page_number": Page number
    
    Steps:
    1. Find relevant clauses in context
    2. Extract exact text
    3. Identify source and page
    4. Formulate concise answer
    
    Example:
    {
        "answer": "The grace period is 30 days.",
        "relevant_clauses": [
            {
                "clause_text": "Section 4.2: Premium payments have a 30-day grace period.",
                "document_id": "policy.pdf",
                "page_number": "12"
            }
        ]
    }
    """

    def __init__(self):
        self.client = groq.Client(api_key=settings.GROQ_API_KEY)

    def generate_response(self, context: str, query: str) -> Dict[str, Any]:
        start_time = time.time()
        try:
            # Truncate context if needed
            if len(context) > settings.MAX_CONTEXT_LENGTH:
                context = context[:settings.MAX_CONTEXT_LENGTH] + "\n\n[CONTEXT TRUNCATED]"
            
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION:\n{query}"}
            ]
            
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                temperature=0.1,
                max_tokens=1024,
                response_format={"type": "json_object"},
                stop=["</s>", "[/INST]"]
            )
            
            output = response.choices[0].message.content
            parsed = json.loads(output.strip())
            parsed['response_time'] = time.time() - start_time
            return parsed
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', output, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                parsed['response_time'] = time.time() - start_time
                return parsed
            return {
                "answer": "Error processing response",
                "relevant_clauses": [],
                "response_time": time.time() - start_time
            }
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            return {
                "answer": "I couldn't process that request. Please try again.",
                "relevant_clauses": [],
                "response_time": time.time() - start_time
            }