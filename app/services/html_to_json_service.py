# fastapi_project/app/services/html_to_json_service.py

import google.generativeai as genai
import json
import re  # Import the re module for regular expressions
from typing import Optional, List, Dict
from ..config import settings  # Ensure settings are imported correctly
import logging

logger = logging.getLogger(__name__)

class HtmlToJsonService:
    def __init__(self):
        print("Initializing HtmlToJsonService...")
        print("API Key:", settings.GOOGLE_GENERATIVE_AI_API_KEY)
        # Configure API Key for Google Generative AI
        genai.configure(api_key=settings.GOOGLE_GENERATIVE_AI_API_KEY)

    def convert_html_to_json(self, html_content: str) -> Optional[List[Dict]]:
        try:
            # Prompt for Google Generative AI API
            prompt = f"""
            You are an AI expert in form data extraction. The input is an HTML document. 
            Your task is to analyze the HTML and identify every field where users need to input data, specifically focusing on <span> elements that contain a 'uuid' (id attribute).
            
            Predict and generate a JSON object that matches the following structure:
            - For regular input fields (text, number, etc.), use the type "text-input".
            - For radio buttons or checkboxes, use the type "radio-box" and provide a list of options.
            - For dropdowns or select fields, use the type "select-box" and provide a list of options.
            - For tables, use the type "table" and include a list of fields under the "fields" property.
            - For date field, you should use the type "date-picker".
            
            For each field in the HTML:
            1. Assign a unique "id" directly from the 'id' attribute of the span. Note: No convert the 'id' to snake_case.
            2. Use the label text as the "label". Be careful to read the HTML to see if the label for that input box is correct. If not, change it to make it as understandable as possible for the user.
            3. Classify the "type" based on the context and surrounding text.
            4. Populate the "options" array for "radio-box" and "select-box" types.
            5. For tables, include nested fields under the "fields" property.
            
            Example classification:
            - For a field labeled 'Giới tính:', you can guess that it will be classified as 'radio-box' and create 'Nam' and 'Nữ' options for this label.
            
            Here is the structure of the JSON object:
            {{
              "id": "unique-id",                // A unique identifier for the field (Big Note: no convert snake_case)
              "value": "field_value",           // Emty string for now
              "label": "Field label",           // Extracted text from the HTML
              "type": "field_type",             // One of: "text-input", "radio-box", "select-box", "table"
              "options": ["option1", "option2"], // Required if type is "radio-box" or "select-box"
              "fields": [                       // Required if type is "table"
                {{
                  "id": "unique_id",
                  "value": "field_value",
                  "label": "Field label",
                  "type": "field_type"
                }}
              ]
            }}
            
            Here is the HTML content:
            {html_content}
            
            (Big Note: no convert id to snake_case)
            Return only the JSON output, enclosed within ```json``` and ``` blocks.
            """

            # Call Google Generative AI API
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            # print("Response:", response)

            # Extract response candidates
            if not hasattr(response, 'candidates'):
                logger.error("No candidates found in the response.")
                return None

            extracted_jsons = []

            for candidate_idx, candidate in enumerate(response.candidates):
                finish_reason = getattr(candidate, 'finish_reason', None)
                
                if not hasattr(candidate, 'content') or not hasattr(candidate.content, 'parts'):
                    logger.warning(f"No content parts found in candidate {candidate_idx}.")
                    continue

                parts = candidate.content.parts
                for part_idx, part in enumerate(parts):
                    text = part.text.strip()
                    logger.debug(f"Candidate {candidate_idx}, Part {part_idx} Text: {text}")

                    # Use regex to extract JSON from ```json ... ```
                    json_blocks = re.findall(r'```json\s*(.*?)\s*```', text, re.DOTALL)
                    
                    if not json_blocks:
                        logger.warning(f"No JSON block found in candidate {candidate_idx}, part {part_idx}.")
                        continue

                    for block_idx, json_str in enumerate(json_blocks):
                        try:
                            logger.debug(f"Extracted JSON String from candidate {candidate_idx}, part {part_idx}, block {block_idx}: {json_str}")
                            json_data = json.loads(json_str)
                            extracted_jsons.append(json_data)
                        except json.JSONDecodeError as jde:
                            logger.error(f"JSON Decode Error in candidate {candidate_idx}, part {part_idx}, block {block_idx}: {jde}")
                            logger.debug(f"Failed JSON String: {json_str}")
                            raise ValueError(status_code=400, detail="JSON Decode Error.")

            if not extracted_jsons:
                logger.error("No valid JSON data extracted from the response.")
                return None

            # logger.info(f"Successfully extracted {len(extracted_jsons)} JSON objects.")
            # print("Extracted JSONs:", extracted_jsons)
            return extracted_jsons

        except Exception as e:
            logger.error(f"An error occurred in convert_html_to_json: {e}")
            return None