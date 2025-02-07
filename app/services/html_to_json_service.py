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
            You are an AI expert in form data extraction. The input is an HTML document (converted from a DOCX file). 
            Your task is to analyze the HTML and identify every field where users need to input data, focusing on <span> elements that contain a unique 'id' attribute (UUID).

            **Goal**: Generate a JSON representation of these fields so that someone viewing only the JSON would understand the original text context (labels) and could re-enter data accordingly.

            **Requirements**:
            1. **Extract "id"**: Must be the exact value from the span's `id` attribute (no snake_case conversion).
            2. **Label**: 
            - Must be descriptive enough so that the user, seeing the JSON alone, can know what should be filled in.
            - If the HTML context for a field is ambiguous or incomplete, guess a label that best fits the meaning of the text. 
            - Preserve as much context from the HTML as possible (e.g., "Địa chỉ liên hệ (điện thoại, fax, email)", nếu có).
            3. **Type**: 
            - `"text-input"` for typical text fields,
            - `"date-picker"` for date fields (nếu rõ ràng là ngày/tháng/năm),
            - `"radio-box"` nếu phát hiện chọn radio,
            - `"check-box"` nếu phát hiện chọn checkbox,
            - `"select-box"` nếu thấy dropdown,
            - `"table"` nếu gặp table (nested fields trong `fields`).
            4. **Options**: 
            - Nếu là `"radio-box"` hoặc `"check-box"`, tạo danh sách `"options"`.
            - Nếu là `"select-box"`, cũng có `"options"`.
            5. **Giá trị ban đầu**: Trả về `"value": ""` (rỗng).
            6. **Trường hợp đặc biệt**:
            - Nếu gặp cấu trúc kiểu `..., ngày ... tháng ... năm ...`, hãy cố gắng đặt label sao cho người đọc hiểu đó là trường Địa chỉ, Ngày, Tháng, Năm, v.v.
            - Tương tự với các đoạn "..." ít thông tin; hãy đoán tên trường sao cho vẫn sát với bối cảnh nội dung.
            7. **Đầu ra cuối cùng**: 
            - Chỉ gồm một mảng JSON chứa các trường được nhận diện.
            - Bao bọc toàn bộ trong cặp ```json``` và ``` (fenced code block).
            - Không xuất thêm bất kỳ văn bản nào ngoài nội dung JSON.
            
            **Important note on tricky cases**:
            - If you see something like "`..., ngày ... tháng ... năm ...`", you might guess that the first span is an address or location (if context suggests so), or it could be a separate field. Then the next spans could be the day, month, and year. Label them in a way that makes sense, for example:
                - The first span could be "Địa chỉ" (if the context is about the place),
                - The second "Ngày",
                - The third "Tháng",
                - The fourth "Năm".
                In this scenario, typically you would assign `"type": "text-input"` to these if they are free-text fields. 
                Adjust the label if you have more context from the HTML.

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
            return extracted_jsons

        except Exception as e:
            logger.error(f"An error occurred in convert_html_to_json: {e}")
            return None