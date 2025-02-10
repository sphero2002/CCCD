# fastapi_project/app/services/html_to_json_service.py

import google.generativeai as genai
import json
import re  # Import the re module for regular expressions
from typing import Optional, List, Dict
from ..config import settings  # Ensure settings are imported correctly
import logging
import uuid
from bs4 import BeautifulSoup

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
        
    def html_ai_processing(self, html_content: str) -> Optional[str]:
        """
        Xử lý nội dung HTML bằng Google Generative AI để chèn placeholders vào những vị trí cần điền dữ liệu.
        Trả về một chuỗi HTML duy nhất.

        Args:
            html_content (str): Nội dung HTML đầu vào.

        Returns:
            Optional[str]: Chuỗi HTML đã được xử lý, hoặc None nếu có lỗi.
        """
        try:
            # Tạo UUID mapping để theo dõi các placeholder và ID (not used in this version, but kept for potential future use)
            placeholder_uuid_map = {}

            def replace_placeholder_with_span(match):
                unique_id = str(uuid.uuid4())
                placeholder_uuid_map[unique_id] = match.group(0) # Lưu lại placeholder gốc nếu cần
                return f'<span id="{unique_id}">...</span>'

            # Tìm và thay thế các placeholder (ví dụ: "...") bằng span có id duy nhất
            # Ví dụ đơn giản, bạn có thể cần điều chỉnh regex này tùy thuộc vào placeholder bạn muốn tìm
            modified_html_content = re.sub(r'\.\.\.', replace_placeholder_with_span, html_content)

            # Prompt cho Google Generative AI API
            prompt = f"""
                Bạn là một trợ lý chuyên xử lý văn bản HTML.
                Tôi sẽ cung cấp cho bạn một đoạn mã HTML. Nhiệm vụ của bạn là:
                1. **Xác định các trường dữ liệu có thể điền vào trong HTML.** (Thay vì "vị trí cần điền dữ liệu" để rõ ràng hơn về ngữ nghĩa trường dữ liệu)
                2. **Đối với mỗi trường dữ liệu xác định được, hãy chèn dấu '...' để làm placeholder.**
                3. **Bao bọc *mỗi placeholder* '...' mới chèn bằng *một* thẻ `<span>` duy nhất với thuộc tính `id` duy nhất.** (Nhấn mạnh "mỗi placeholder" và "một thẻ span duy nhất")
                4. **Giữ nguyên cấu trúc HTML gốc và chỉ thay đổi nội dung ở những vị trí cần điền dữ liệu.**
                5. **Nếu đã có thẻ span (nội dung gồm các dấu chấm và có tồn tại uuid rồi) thì đoạn văn đó đó không cần tạo thêm thẻ span.**
                6. **Luôn luôn trả về HTML kể cả không có gì để sửa trong HTML gốc ban đầu**

                **Lưu ý quan trọng:**
                - Sử dụng UUID (Universally Unique Identifier) để tạo giá trị duy nhất cho thuộc tính `id` của mỗi thẻ `<span>`.
                - Không thay đổi cấu trúc HTML ban đầu, chỉ chèn thêm thẻ `<span>` và dấu '...' vào những vị trí thích hợp.
                - **Mỗi trường dữ liệu được xác định chỉ được bao bọc bởi *một* cặp thẻ `<span>...</span>` duy nhất.** (Đặc biệt lưu ý cái này)
                - Trả về **DUY NHẤT** phần mã HTML đã được chỉnh sửa, được bao bọc trong cặp thẻ ```html```.

                **Ví dụ:**

                **HTML đầu vào:**
                ```html
                <div>
                    <span>Tên công ty:<span id="123456">...</span></span>
                    <div>Địa chỉ:</div>
                    <p>Số điện thoại:</p>
                </div>
                ```

                **HTML đầu ra mong muốn:**
                ```html
                <div>
                    <span>Tên công ty: <span id="123456">...</span></span> // Không cần thêm trả về như cũ
                    <div>Địa chỉ: <span id="unique-uuid-2">...</span></div> // Thêm thẻ span mới
                    <p>Số điện thoại: <span id="unique-uuid-3">...</span></p> // Thêm thẻ span mới
                </div>
                ```
                **HTML đầu ra không mong muốn:**
                '''html
                </span>
                4. Số Fax:
                    <span id="28961891-a08e-468a-82d0-0a13956cc053">
                        <span id="81e37def-279e-45e8-b963-34ca56f68d33">...</span><span id="76357de8-c10a-4d7c-8da8-ba852e402d3f">...</span><span id="ae41b215-76c0-4da6-ba8c-aab50a583188">...</span><span id="35cf4b01-d304-4917-8b4c-b3452085366a">...</span>
                    </span>
                </span>
                '''

                **HTML đúng:**
                '''html
                </span>
                4. Số Fax:
                    <span id="28961891-a08e-468a-82d0-0a13956cc053">
                    ............
                    </span>
                </span>
                '''

                Đây là đoạn mã HTML đầu vào:
                ```html
                {modified_html_content}
                ```
            """

            logger.debug(f"Prompt gửi đến AI để xử lý HTML: {prompt}")

            # Gọi Google Generative AI API
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            print("response!!!!!!!!!!!!!!!!!!!!!!!!!!!\n",response)

            # Extract response candidates
            if not hasattr(response, 'candidates') or not response.candidates:
                logger.error("Không có candidates nào trong response từ AI cho xử lý HTML.")
                return None

            extracted_html_str = None

            for candidate_idx, candidate in enumerate(response.candidates):
                finish_reason = getattr(candidate, 'finish_reason', None)
                logger.debug(f"Candidate {candidate_idx}, Finish Reason: {finish_reason} (HTML processing)")

                if not hasattr(candidate, 'content') or not hasattr(candidate.content, 'parts') or not candidate.content.parts:
                    logger.warning(f"Không có content parts nào trong candidate {candidate_idx} cho xử lý HTML.")
                    continue

                parts = candidate.content.parts
                for part_idx, part in enumerate(parts):
                    text = part.text.strip()
                    logger.debug(f"Candidate {candidate_idx}, Part {part_idx} Text: {text} (HTML processing)")

                    # Use regex to extract html from ```html ... ```
                    html_blocks = re.findall(r'```html\s*(.*?)\s*```', text, re.DOTALL)

                    if not html_blocks:
                        logger.warning(f"Không tìm thấy khối html nào trong candidate {candidate_idx}, part {part_idx} cho xử lý HTML.")
                        continue

                    for block_idx, html_str in enumerate(html_blocks):
                        try:
                            logger.debug(f"Extracted html String từ candidate {candidate_idx}, part {part_idx}, block {block_idx}: {html_str}")
                            if extracted_html_str is None: # Lấy khối HTML đầu tiên hợp lệ
                                extracted_html_str = html_str
                            break # Chỉ lấy khối HTML đầu tiên và dừng lại
                        except Exception as e: # Bắt lỗi tổng quát hơn nếu có vấn đề khi xử lý html_str
                            logger.error(f"Lỗi khi xử lý HTML String trong candidate {candidate_idx}, part {part_idx}, block {block_idx}: {e}")
                            logger.debug(f"Failed html String: {html_str}")
                            continue # Tiếp tục nếu có lỗi với khối HTML này

                    if extracted_html_str: # Nếu đã tìm thấy và gán extracted_html_str, dừng vòng lặp parts
                        break
                if extracted_html_str: # Nếu đã tìm thấy và gán extracted_html_str, dừng vòng lặp candidates
                    break

            if not extracted_html_str:
                logger.warning("Không có dữ liệu html hợp lệ nào được trích xuất từ response cho xử lý HTML.")
                return None

            logger.info(f"Successfully extracted html string.")
            return extracted_html_str # Trả về chuỗi HTML

        except Exception as e:
            logger.exception(f"An error occurred in html_ai_processing: {e}") # Sử dụng logger.exception để log đầy đủ traceback
            return None
        
    def flatten_id_spans(self, html_str):
        """
        Hàm này nhận vào một chuỗi HTML và xử lý các thẻ <span> có thuộc tính id lồng nhau.
        Nếu một thẻ <span> có id chứa các thẻ <span> con cũng có id, 
        thì nội dung của các thẻ con sẽ được gộp lại thành nội dung của thẻ cha và 
        các thẻ con sẽ bị loại bỏ.
        """
        soup = BeautifulSoup(html_str, 'html.parser')
        
        # Duyệt qua tất cả các thẻ <span> có thuộc tính id
        for span in soup.find_all('span', id=True):
            # Tìm tất cả các thẻ <span> con (trong mọi cấp) có thuộc tính id
            descendant_spans = span.find_all('span', id=True)
            if descendant_spans:
                # Lấy nội dung (text) của các thẻ con, loại bỏ khoảng trắng thừa
                combined_text = ''.join([desc.get_text(strip=True) for desc in descendant_spans])
                # Xóa sạch nội dung con của thẻ cha
                span.clear()
                # Thêm nội dung đã gộp vào thẻ cha
                span.append(combined_text)
        
        return soup.prettify()