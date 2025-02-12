# fastapi_project/app/services/html_to_json_service.py

import google.generativeai as genai
import json
import re  # Import the re module for regular expressions
from typing import Optional, List, Dict
from ..config import settings  # Ensure settings are imported correctly
import logging
import uuid
from bs4 import BeautifulSoup
import concurrent.futures
from bs4 import NavigableString

logger = logging.getLogger(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; }}
    h1, h2, h3, h4, h5, h6 {{ color: #2e6c80; }}
    table, th, td {{ padding: 20px; text-align: left; }}
    img {{ max-width: 100%; height: auto; }}
    ul, ol {{ margin: 0; padding-left: 40px; }}
    td {{ vertical-align: top; }}
    p {{ margin: 0 0 1em 0; }}
  </style>
</head>
<body style="margin: 75px 75px 75px 113px;">
  {content}
</body>
</html>
"""

def split_body_into_chunks(html, max_length=3000):
        """
        Chia nội dung trong thẻ body của HTML thành các chunk không vượt quá max_length ký tự.
        Nếu một phần tử đơn lẻ vượt quá max_length thì sẽ được chia nhỏ.
        """
        print("start split_body_into_chunks")
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.body
        if body is None:
            raise ValueError("Không tìm thấy thẻ <body> trong HTML.")
        
        # Lấy danh sách các phần tử con trực tiếp của body
        children = list(body.children)
        chunks = []
        current_chunk = ""
        
        for child in children:
            # Chuyển đổi phần tử sang chuỗi HTML
            child_str = str(child)
            # Nếu thêm child này sẽ vượt quá max_length:
            if len(current_chunk) + len(child_str) > max_length:
                # Nếu current_chunk không rỗng, lưu chunk hiện tại lại
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                
                # Nếu child_str đơn lẻ vượt quá max_length, cần tách nó thành các phần nhỏ hơn.
                if len(child_str) > max_length:
                    for i in range(0, len(child_str), max_length):
                        sub_chunk = child_str[i:i+max_length]
                        chunks.append(sub_chunk)
                else:
                    # Nếu child_str không vượt quá max_length, gán nó cho current_chunk (khởi đầu chunk mới)
                    current_chunk = child_str
            else:
                # Nếu không vượt quá, thêm child_str vào current_chunk
                current_chunk += child_str
        
        # Sau vòng lặp, nếu còn dư thì thêm vào danh sách chunks
        if current_chunk:
            chunks.append(current_chunk)
        
        # Bọc mỗi chunk vào mẫu HTML hoàn chỉnh
        final_pages = [HTML_TEMPLATE.format(content=chunk) for chunk in chunks]
        # print("chunks len",len(chunks))
        print("end split_body_into_chunks")
        return final_pages

def combine_nested_lists(nested_lists):
    """
    Nhận vào một danh sách các danh sách và trả về một danh sách chứa
    một danh sách kết hợp tất cả các phần tử con.
    """
    combined = []
    for sublist in nested_lists:
        combined.extend(sublist)
    return [combined]

class HtmlToJsonService:
    def __init__(self):
        print("Initializing HtmlToJsonService...")
        print("API Key:", settings.GOOGLE_GENERATIVE_AI_API_KEY)
        self.max_chunk_length = 25000
        # Configure API Key for Google Generative AI
        genai.configure(api_key=settings.GOOGLE_GENERATIVE_AI_API_KEY)

    def convert_html_to_json(self, html_content: str) -> Optional[List[Dict]]:
        """
        Chia nội dung HTML thành các chunk, sau đó với mỗi chunk gọi API của Google Generative AI
        để trích xuất các trường dữ liệu. Các kết quả JSON thu được từ từng chunk sẽ được gom lại.
        """
        try:
            # Tách nội dung HTML thành các chunk
            chunks = split_body_into_chunks(html_content, max_length=self.max_chunk_length)
            extracted_jsons = []
            
            for chunk_idx, chunk in enumerate(chunks):
                # Xây dựng prompt cho từng chunk HTML
                prompt = f"""
    You are an AI expert in form data extraction. Given an HTML document (converted from DOCX), identify all fields for user input by locating `<span>` elements with a unique `id` (UUID).

    Goal: Generate a JSON array representing these fields so that the JSON alone conveys the original context (labels) for data entry.

    Requirements:
    1. **ID**: Use the exact `id` value (do not convert to snake_case).
    2. **Label**: Extract or infer a descriptive label from the HTML. For ambiguous placeholders ("..."), guess a fitting label while preserving context (e.g., "Địa chỉ liên hệ (điện thoại, fax, email)").
    3. **Type**:
    - "text-input" for text fields,
    - "date-picker" for date fields (if day/month/year is clear),
    - "radio-box" for radio buttons,
    - "check-box" for checkboxes,
    - "select-box" for dropdowns,
    - "table" for tables (include nested `fields`).
    4. **Options**: For "radio-box", "check-box", or "select-box", include an "options" array.
    5. **Value**: Set "value": "" for all fields.
    6. **Special Cases**: For patterns like `..., ngày ... tháng ... năm ...`, assign labels such as "Địa chỉ" (if applicable), "Ngày", "Tháng", and "Năm" accordingly.
    7. **Output**: Return only a JSON array of these field objects, enclosed in fenced code blocks with ```json at the start and ``` at the end. Do not output any extra text.

    Here is the structure of the JSON object:
    {{
        "id": "unique-id",                // A unique identifier for the field (Big Note: no convert snake_case)
        "value": "field_value",           // Empty string for now
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

    HTML Content:
    {chunk}

    (Big Note: Do not convert id values to snake_case.)
                """
                
                # Gọi API của Google Generative AI cho chunk hiện tại
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                logger.info(f"Response from API for chunk {chunk_idx}: {response}")
                
                if not hasattr(response, 'candidates'):
                    logger.error(f"No candidates found in the response for chunk {chunk_idx}.")
                    continue
                
                for candidate_idx, candidate in enumerate(response.candidates):
                    if not hasattr(candidate, 'content') or not hasattr(candidate.content, 'parts'):
                        logger.warning(f"No content parts found in candidate {candidate_idx} for chunk {chunk_idx}.")
                        continue
                    
                    parts = candidate.content.parts
                    for part_idx, part in enumerate(parts):
                        text = part.text.strip()
                        logger.debug(f"Chunk {chunk_idx}, Candidate {candidate_idx}, Part {part_idx} Text: {text}")
                        
                        # Dùng regex để trích xuất JSON được bọc trong ```json ... ```
                        json_blocks = re.findall(r'```json\s*(.*?)\s*```', text, re.DOTALL)
                        if not json_blocks:
                            logger.warning(f"No JSON block found in candidate {candidate_idx}, part {part_idx} for chunk {chunk_idx}.")
                            continue
                        
                        for block_idx, json_str in enumerate(json_blocks):
                            try:
                                logger.debug(f"Extracted JSON String from chunk {chunk_idx}, candidate {candidate_idx}, part {part_idx}, block {block_idx}: {json_str}")
                                json_data = json.loads(json_str)
                                extracted_jsons.append(json_data)
                            except json.JSONDecodeError as jde:
                                logger.error(f"JSON Decode Error in chunk {chunk_idx}, candidate {candidate_idx}, part {part_idx}, block {block_idx}: {jde}")
                                raise ValueError("JSON Decode Error.")
                                
            if not extracted_jsons:
                logger.error("No valid JSON data extracted from any chunk.")
                return None
            
            return combine_nested_lists(extracted_jsons)
            
        except Exception as e:
            logger.error(f"An error occurred in convert_html_to_json: {e}")
            return None
        
    # def html_ai_processing(self, html_content: str) -> Optional[str]:
    #     """
    #     Xử lý nội dung HTML bằng Google Generative AI để chèn placeholders vào những vị trí cần điền dữ liệu.
    #     Trả về một chuỗi HTML duy nhất.

    #     Args:
    #         html_content (str): Nội dung HTML đầu vào.

    #     Returns:
    #         Optional[str]: Chuỗi HTML đã được xử lý, hoặc None nếu có lỗi.
    #     """
    #     try:
    #         # Tạo UUID mapping để theo dõi các placeholder và ID (not used in this version, but kept for potential future use)
    #         placeholder_uuid_map = {}

    #         def replace_placeholder_with_span(match):
    #             unique_id = str(uuid.uuid4())
    #             placeholder_uuid_map[unique_id] = match.group(0) # Lưu lại placeholder gốc nếu cần
    #             return f'<span id="{unique_id}">...</span>'

    #         # Tìm và thay thế các placeholder (ví dụ: "...") bằng span có id duy nhất
    #         # Ví dụ đơn giản, bạn có thể cần điều chỉnh regex này tùy thuộc vào placeholder bạn muốn tìm
    #         modified_html_content = re.sub(r'\.\.\.', replace_placeholder_with_span, html_content)

    #         # Prompt cho Google Generative AI API
    #         prompt = f"""
    #             Bạn là một trợ lý chuyên xử lý văn bản HTML.
    #             Tôi sẽ cung cấp cho bạn một đoạn mã HTML. Nhiệm vụ của bạn là:
    #             1. **Xác định các trường dữ liệu có thể điền vào trong HTML.** (Thay vì "vị trí cần điền dữ liệu" để rõ ràng hơn về ngữ nghĩa trường dữ liệu)
    #             2. **Đối với mỗi trường dữ liệu xác định được, hãy chèn dấu '...' để làm placeholder.**
    #             3. **Bao bọc *mỗi placeholder* '...' mới chèn bằng *một* thẻ `<span>` duy nhất với thuộc tính `id` duy nhất.** (Nhấn mạnh "mỗi placeholder" và "một thẻ span duy nhất")
    #             4. **Giữ nguyên cấu trúc HTML gốc và chỉ thay đổi nội dung ở những vị trí cần điền dữ liệu.**
    #             5. **Nếu đã có thẻ span (nội dung gồm các dấu chấm và có tồn tại uuid rồi) thì đoạn văn đó đó không cần tạo thêm thẻ span.**
    #             6. **Luôn luôn trả về HTML kể cả không có gì để sửa trong HTML gốc ban đầu**

    #             **Lưu ý quan trọng:**
    #             - Sử dụng UUID để tạo giá trị duy nhất cho thuộc tính `id` của mỗi thẻ `<span>`.
    #             - Không thay đổi cấu trúc HTML ban đầu, chỉ chèn thêm thẻ `<span>` và dấu '...' vào những vị trí thích hợp.
    #             - **Mỗi trường dữ liệu được xác định chỉ được bao bọc bởi *một* cặp thẻ `<span>...</span>` duy nhất.** (Đặc biệt lưu ý cái này)
    #             - Trả về **DUY NHẤT** phần mã HTML đã được chỉnh sửa, được bao bọc trong cặp thẻ ```html```.

    #             **Ví dụ:**

    #             **HTML đầu vào:**
    #             ```html
    #             <div>
    #                 <span>Tên công ty:<span id="123456">...</span></span>
    #                 <div>Địa chỉ:</div>
    #                 <p>Số điện thoại:</p>
    #             </div>
    #             ```

    #             **HTML đầu ra mong muốn:**
    #             ```html
    #             <div>
    #                 <span>Tên công ty: <span id="123456">...</span></span> // Không cần thêm trả về như cũ
    #                 <div>Địa chỉ: <span id="unique-uuid-2">...</span></div> // Thêm thẻ span mới
    #                 <p>Số điện thoại: <span id="unique-uuid-3">...</span></p> // Thêm thẻ span mới
    #             </div>
    #             ```
    #             **HTML đầu ra không mong muốn:**
    #             '''html
    #             </span>
    #             4. Số Fax:
    #                 <span id="28961891-a08e-468a-82d0-0a13956cc053">
    #                     <span id="81e37def-279e-45e8-b963-34ca56f68d33">...</span><span id="76357de8-c10a-4d7c-8da8-ba852e402d3f">...</span><span id="ae41b215-76c0-4da6-ba8c-aab50a583188">...</span><span id="35cf4b01-d304-4917-8b4c-b3452085366a">...</span>
    #                 </span>
    #             </span>
    #             '''

    #             **HTML đúng:**
    #             '''html
    #             </span>
    #             4. Số Fax:
    #                 <span id="28961891-a08e-468a-82d0-0a13956cc053">
    #                 ............
    #                 </span>
    #             </span>
    #             '''

    #             Đây là đoạn mã HTML đầu vào:
    #             ```html
    #             {modified_html_content}
    #             ```
    #         """

    #         logger.debug(f"Prompt gửi đến AI để xử lý HTML: {prompt}")

    #         # Gọi Google Generative AI API
    #         model = genai.GenerativeModel("gemini-1.5-flash")
    #         response = model.generate_content(prompt)
    #         print("response!!!!!!!!!!!!!!!!!!!!!!!!!!!\n",response)

    #         # Extract response candidates
    #         if not hasattr(response, 'candidates') or not response.candidates:
    #             logger.error("Không có candidates nào trong response từ AI cho xử lý HTML.")
    #             return None

    #         extracted_html_str = None

    #         for candidate_idx, candidate in enumerate(response.candidates):
    #             finish_reason = getattr(candidate, 'finish_reason', None)
    #             logger.debug(f"Candidate {candidate_idx}, Finish Reason: {finish_reason} (HTML processing)")

    #             if not hasattr(candidate, 'content') or not hasattr(candidate.content, 'parts') or not candidate.content.parts:
    #                 logger.warning(f"Không có content parts nào trong candidate {candidate_idx} cho xử lý HTML.")
    #                 continue

    #             parts = candidate.content.parts
    #             for part_idx, part in enumerate(parts):
    #                 text = part.text.strip()
    #                 logger.debug(f"Candidate {candidate_idx}, Part {part_idx} Text: {text} (HTML processing)")

    #                 # Use regex to extract html from ```html ... ```
    #                 html_blocks = re.findall(r'```html\s*(.*?)\s*```', text, re.DOTALL)

    #                 if not html_blocks:
    #                     logger.warning(f"Không tìm thấy khối html nào trong candidate {candidate_idx}, part {part_idx} cho xử lý HTML.")
    #                     continue

    #                 for block_idx, html_str in enumerate(html_blocks):
    #                     try:
    #                         logger.debug(f"Extracted html String từ candidate {candidate_idx}, part {part_idx}, block {block_idx}: {html_str}")
    #                         if extracted_html_str is None: # Lấy khối HTML đầu tiên hợp lệ
    #                             extracted_html_str = html_str
    #                         break # Chỉ lấy khối HTML đầu tiên và dừng lại
    #                     except Exception as e: # Bắt lỗi tổng quát hơn nếu có vấn đề khi xử lý html_str
    #                         logger.error(f"Lỗi khi xử lý HTML String trong candidate {candidate_idx}, part {part_idx}, block {block_idx}: {e}")
    #                         logger.debug(f"Failed html String: {html_str}")
    #                         continue # Tiếp tục nếu có lỗi với khối HTML này

    #                 if extracted_html_str: # Nếu đã tìm thấy và gán extracted_html_str, dừng vòng lặp parts
    #                     break
    #             if extracted_html_str: # Nếu đã tìm thấy và gán extracted_html_str, dừng vòng lặp candidates
    #                 break

    #         if not extracted_html_str:
    #             logger.warning("Không có dữ liệu html hợp lệ nào được trích xuất từ response cho xử lý HTML.")
    #             return None

    #         logger.info(f"Successfully extracted html string.")
    #         return extracted_html_str # Trả về chuỗi HTML

    #     except Exception as e:
    #         logger.exception(f"An error occurred in html_ai_processing: {e}") # Sử dụng logger.exception để log đầy đủ traceback
    #         return None

    def html_ai_processing(self, html_content: str) -> Optional[str]:
        """
        Xử lý nội dung HTML bằng Google Generative AI.
        Nếu HTML quá dài (vượt quá max_chunk_length), sẽ chia nhỏ nội dung theo thẻ body,
        sau đó xử lý từng chunk riêng và ghép lại kết quả cuối cùng.
        """
        try:
            # 1. Tiền xử lý: Thay thế các placeholder "..." bằng thẻ <span> có id duy nhất.
            placeholder_uuid_map = {}

            def replace_placeholder(match):
                unique_id = str(uuid.uuid4())
                placeholder_uuid_map[unique_id] = match.group(0)  # Lưu lại placeholder gốc nếu cần
                return f'<span id="{unique_id}">...</span>'

            modified_html_content = re.sub(r'\.\.\.', replace_placeholder, html_content)

            # 2. Nếu nội dung nhỏ hơn ngưỡng thì xử lý trực tiếp.
            if len(modified_html_content) <= self.max_chunk_length:
                processed_chunk = self.process_html_chunk(modified_html_content)
                return processed_chunk

            # 3. Đảm bảo HTML có thẻ <body>; nếu không, bọc nó vào cấu trúc đầy đủ.
            if not re.search(r'<body', modified_html_content, re.IGNORECASE):
                modified_html_content = f"<html><body>{modified_html_content}</body></html>"

            # 4. Chia nhỏ HTML thành các chunk sử dụng hàm split_body_into_chunks
            chunks: List[str] = split_body_into_chunks(modified_html_content, max_length=int(self.max_chunk_length/3))
            logger.info(f"Đã chia HTML thành {len(chunks)} chunk.")
            # độ dài của mỗi chunk
            for chunk in chunks:
                print("chunk length: ",len(chunk))

            # 5. Xử lý các chunk qua API song song.
            processed_chunks = [None] * len(chunks)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_index = {
                    executor.submit(self.process_html_chunk, chunk): idx
                    for idx, chunk in enumerate(chunks)
                }
                for future in concurrent.futures.as_completed(future_to_index):
                    idx = future_to_index[future]
                    try:
                        result = future.result()
                        if result is None:
                            logger.warning(f"Chunk {idx} không được xử lý. Sử dụng chunk gốc.")
                            result = chunks[idx]  # Fallback: dùng chunk gốc
                        processed_chunks[idx] = result
                    except Exception as exc:
                        logger.error(f"Chunk {idx} gặp lỗi: {exc}. Sử dụng chunk gốc.")
                        processed_chunks[idx] = chunks[idx]

            # 6. Ghép lại các chunk đã xử lý:
            # Vì các chunk ở bước 5 là HTML đầy đủ (có thẻ <html>/<body>),
            # ta cần trích xuất nội dung bên trong <body> của từng chunk để ghép lại.
            combined_body_content = ""
            for processed_chunk in processed_chunks:
                soup = BeautifulSoup(processed_chunk, "html.parser")
                body = soup.body
                if body:
                    # Ghép nội dung của tất cả các phần tử con của body
                    combined_body_content += "".join(str(child) for child in body.children)
                else:
                    # Nếu không có thẻ <body>, dùng cả HTML
                    combined_body_content += processed_chunk

            # 7. Bọc nội dung đã ghép vào mẫu HTML hoàn chỉnh.
            final_html = HTML_TEMPLATE.format(content=combined_body_content)
            return final_html

        except Exception as e:
            logger.exception(f"An error occurred in html_ai_processing: {e}")
            return None

    def process_html_chunk(self, chunk_html: str) -> Optional[str]:
        """
        Xử lý một chunk HTML qua Google Generative AI API.
        Trả về đoạn HTML đã được xử lý (được bao bọc trong cặp thẻ html).
        Nếu không thể trích xuất HTML hợp lệ từ response, trả về chunk gốc.
        """
        try:
            prompt = f"""
Bạn là một trợ lý chuyên xử lý văn bản HTML.
Tôi sẽ cung cấp cho bạn một đoạn mã HTML (một phần của file lớn).
Nhiệm vụ của bạn là:
1. Xác định các trường dữ liệu có thể điền vào trong HTML và chèn dấu '...' làm placeholder.
2. Bao bọc MỖI placeholder '...' mới chèn bằng một thẻ <span> duy nhất với thuộc tính id duy nhất.
3. Giữ nguyên cấu trúc HTML gốc và chỉ thay đổi nội dung ở những vị trí cần điền dữ liệu.
4. Nếu đã có thẻ span (nội dung gồm các dấu chấm và có tồn tại uuid) thì không tạo thêm thẻ mới.
5. Luôn luôn trả về HTML kể cả không có gì để sửa.

HTML đầu vào của bạn là:
html
{chunk_html}
Vui lòng trả về DUY NHẤT phần mã HTML đã được chỉnh sửa, được bao bọc trong cặp thẻ html.
""" 
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            print("Response từ API:\n%s", response)
            if not hasattr(response, 'candidates') or not response.candidates:
                logger.error("Không có candidates nào trong response từ AI cho xử lý HTML chunk.")
                return chunk_html  # Fallback: trả về chunk gốc

            extracted_html_str = None
            for candidate_idx, candidate in enumerate(response.candidates):
                finish_reason = getattr(candidate, 'finish_reason', None)
                logger.debug(f"Candidate {candidate_idx}, Finish Reason: {finish_reason}")

                if not hasattr(candidate, 'content') or not hasattr(candidate.content, 'parts') or not candidate.content.parts:
                    logger.warning(f"Không có content parts trong candidate {candidate_idx} cho HTML chunk.")
                    continue

                for part_idx, part in enumerate(candidate.content.parts):
                    text = part.text.strip()
                    logger.debug(f"Candidate {candidate_idx}, Part {part_idx} Text: {text}")

                    # Dùng regex để trích xuất nội dung nằm giữa cặp thẻ html
                    html_blocks = re.findall(r'<html\s*>(.*?)\s*</html>', text, re.DOTALL)
                    if html_blocks:
                        extracted_html_str = html_blocks[0]
                        break
                    else:
                        # Fallback: nếu không tìm được khối HTML bằng regex, kiểm tra xem text có bắt đầu bằng thẻ HTML không
                        stripped_text = text.strip()
                        if (stripped_text.startswith("<html") or 
                            stripped_text.startswith("<div") or 
                            stripped_text.startswith("<body")):
                            extracted_html_str = stripped_text
                            break
                        else:
                            logger.warning(f"Không tìm thấy khối HTML trong candidate {candidate_idx}, part {part_idx}.")
                if extracted_html_str:
                    break

            if not extracted_html_str:
                logger.warning("Không có dữ liệu HTML hợp lệ nào được trích xuất từ response cho HTML chunk.")
                return chunk_html  # Fallback: trả về chunk gốc

            logger.info("Extracted HTML chunk thành công.")
            return extracted_html_str

        except Exception as e:
            logger.exception(f"An error occurred in process_html_chunk: {e}")
            return chunk_html  # Fallback: trả về chunk gốc

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