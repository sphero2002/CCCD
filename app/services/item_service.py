import os
import subprocess
import uuid
import logging
from tempfile import NamedTemporaryFile, gettempdir

from app.services.docx_converter import DocxToHtmlConverter

logger = logging.getLogger(__name__)

class ItemService:
    def convert_docx_to_html(self, file_bytes: bytes, file_extension: str) -> str:
        # Tạo file tạm thời với đúng định dạng
        with NamedTemporaryFile(delete=False, suffix=file_extension) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        docx_path = None  # Khởi tạo biến docx_path để tránh lỗi tham chiếu trước gán

        try:
            # Nếu file là .doc, chuyển đổi sang .docx trước
            if file_extension.lower() == ".doc":
                docx_path = self.convert_doc_to_docx(tmp_path)
                tmp_path = docx_path  # Sử dụng file .docx đã chuyển đổi
            elif file_extension.lower() == ".docx":
                # Đảm bảo rằng file là .docx
                pass
            else:
                raise ValueError("Unsupported file extension.")

            # Chuyển đổi .docx sang HTML
            converter = DocxToHtmlConverter(tmp_path)
            html_output = converter.convert_document()
        except Exception as e:
            logger.error(f"Error in convert_docx_to_html: {e}")
            raise
        finally:
            # Xóa file tạm thời
            os.remove(tmp_path)
            if docx_path and os.path.exists(docx_path):  # Chỉ xóa nếu docx_path không phải None
                os.remove(docx_path)  # Xóa file .docx đã chuyển đổi nếu có

        return html_output

    def convert_doc_to_docx(self, doc_path: str, output_dir: str = None) -> str:
        if not output_dir:
            output_dir = gettempdir()

        # Tạo tên file tạm thời cho .docx
        docx_filename = f"converted_{uuid.uuid4().hex}.docx"
        docx_path = os.path.join(output_dir, docx_filename)

        # Thực hiện chuyển đổi bằng LibreOffice
        try:
            # Lệnh chuyển đổi: soffice --headless --convert-to docx "input.doc" --outdir "output_dir"
            command = [
                "soffice",
                "--headless",
                "--convert-to",
                "docx",
                doc_path,
                "--outdir",
                output_dir
            ]
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            logger.error(f"LibreOffice conversion failed: {e.stderr.decode()}")
            raise RuntimeError("Failed to convert .doc to .docx") from e

        # Kiểm tra xem file .docx đã được tạo chưa
        if not os.path.exists(docx_path):
            # LibreOffice có thể tạo file với tên khác, do đó tìm file .docx trong output_dir
            converted_files = [f for f in os.listdir(output_dir) if f.lower().endswith(".docx")]
            if converted_files:
                docx_path = os.path.join(output_dir, converted_files[0])
            else:
                raise FileNotFoundError("Converted .docx file not found.")

        return docx_path
