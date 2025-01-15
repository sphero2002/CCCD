# fastapi_project/app/services/item_service.py

from app.services.docx_converter import DocxToHtmlConverter
import os
from tempfile import NamedTemporaryFile, gettempdir
from win32com import client  # Sử dụng pywin32 để chuyển đổi .doc sang .docx
import pythoncom
import uuid
import logging

logger = logging.getLogger(__name__)

class ItemService:
    def convert_docx_to_html(self, file_bytes: bytes, file_extension: str) -> str:
        # Tạo file tạm thời với đúng định dạng
        with NamedTemporaryFile(delete=False, suffix=file_extension) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        try:
            # Nếu file là .doc, chuyển đổi sang .docx trước
            if file_extension == ".doc":
                docx_path = self.convert_doc_to_docx(file_bytes)  # Truyền file_bytes
                tmp_path = docx_path  # Sử dụng file .docx đã chuyển đổi
            # Chuyển đổi .docx sang HTML
            converter = DocxToHtmlConverter(tmp_path)
            html_output = converter.convert_document()
        finally:
            # Xóa file tạm thời
            os.remove(tmp_path)
            if file_extension == ".doc" and os.path.exists(docx_path):
                os.remove(docx_path)  # Xóa file .docx đã chuyển đổi nếu có
        
        return html_output

    def convert_doc_to_docx(self, file_bytes: bytes, output_dir: str = None) -> str:
        """
        Chuyển đổi file .doc (dạng bytes) sang .docx và lưu vào thư mục chỉ định.
        Không cần lưu lại file .docx trên đĩa sau khi chuyển đổi.

        :param file_bytes: Dữ liệu bytes của file .doc.
        :param output_dir: Thư mục để lưu file .docx đã chuyển đổi. Mặc định là thư mục tạm.
        :return: Đường dẫn tới file .docx đã lưu.
        """
        docx_path = None
        try:
            # Đảm bảo thư mục đích tồn tại, mặc định là thư mục tạm
            if not output_dir:
                output_dir = gettempdir()
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Thư mục đích đã được xác định tại: {output_dir}")
            
            # Tạo file tạm thời với đuôi .doc
            with NamedTemporaryFile(delete=False, suffix=".doc", mode='wb') as tmp:
                tmp.write(file_bytes)
                tmp.flush()
                os.fsync(tmp.fileno())
                doc_path = tmp.name
            logger.info(f"File tạm thời .doc đã được tạo tại: {doc_path}")
            
            # Kiểm tra nếu file đã được ghi chính xác
            if not os.path.exists(doc_path) or os.path.getsize(doc_path) == 0:
                raise ValueError("File .doc tạm thời không tồn tại hoặc có kích thước bằng 0.")
            
            # Tạo tên file .docx độc nhất
            unique_id = uuid.uuid4().hex
            docx_filename = f"converted_{unique_id}.docx"
            docx_path = os.path.join(output_dir, docx_filename)
            docx_path = os.path.abspath(docx_path)  # Chuyển thành đường dẫn tuyệt đối
            logger.info(f"Đường dẫn lưu file .docx sẽ là: {docx_path}")
            
            # Khởi tạo COM
            pythoncom.CoInitialize()
            
            # Khởi động ứng dụng Word
            word = client.Dispatch("Word.Application")
            word.Visible = False  # Ẩn cửa sổ Word
            word.DisplayAlerts = 0  # Tắt cảnh báo
            
            try:
                # Đảm bảo rằng Word không bị lỗi mở file
                # Sử dụng ReadOnly=True để tránh khóa file
                logger.info(f"Mở file .doc tại: {doc_path}")
                doc = word.Documents.Open(doc_path, ReadOnly=True, Visible=False)
                logger.info(f"Đã mở file .doc tại: {doc_path}")
                
                # Lưu dưới dạng .docx (FileFormat=16)
                logger.info(f"Lưu file .docx tại: {docx_path}")
                doc.SaveAs(docx_path, FileFormat=16)
                logger.info(f"Đã lưu file .docx tại: {docx_path}")
                
                # Đóng tài liệu
                doc.Close()
                logger.info(f"Đã đóng file .doc tại: {doc_path}")
            except Exception as e:
                logger.error(f"Lỗi khi chuyển đổi .doc sang .docx: {e}")
                # Thêm thông tin kiểm tra file .doc
                if os.path.exists(doc_path):
                    file_size = os.path.getsize(doc_path)
                    logger.error(f"File .doc tại {doc_path} có kích thước: {file_size} bytes")
                # Thêm thông tin nội dung file (nếu có thể)
                try:
                    with open(doc_path, "rb") as f:
                        content = f.read()
                        logger.error(f"Nội dung file .doc: {content[:100]}...")  # Ghi ra 100 byte đầu tiên
                except Exception as ex:
                    logger.error(f"Không thể đọc nội dung file .doc để debug: {ex}")
                raise RuntimeError(f"Lỗi khi chuyển đổi .doc sang .docx: {e}")
            finally:
                # Đóng ứng dụng Word
                word.Quit()
                logger.info("Đã đóng ứng dụng Word.")
                
                # Giải phóng COM
                pythoncom.CoUninitialize()
                
                # Xóa file tạm thời .doc
                if os.path.exists(doc_path):
                    os.remove(doc_path)
                    logger.info(f"Đã xóa file tạm thời: {doc_path}")
            
            # Kiểm tra nếu file .docx đã được tạo
            if not os.path.exists(docx_path) or os.path.getsize(docx_path) == 0:
                raise ValueError("File .docx đã chuyển đổi không tồn tại hoặc có kích thước bằng 0.")
            return docx_path
        except Exception as e:
            logger.error(f"Đã xảy ra lỗi trong quá trình chuyển đổi: {e}")
            raise