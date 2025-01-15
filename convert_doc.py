import os
import uuid
from tempfile import NamedTemporaryFile
from win32com import client
import pythoncom  # Để xử lý các vấn đề liên quan đến COM threading
import logging

# Thiết lập logging để theo dõi các lỗi và thông tin
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocConverter:
    def convert_doc_to_docx(self, file_bytes: bytes, output_dir: str = "converted_docs") -> str:
        """
        Chuyển đổi file .doc (dạng bytes) sang .docx và lưu vào thư mục chỉ định.

        :param file_bytes: Dữ liệu bytes của file .doc.
        :param output_dir: Thư mục để lưu file .docx đã chuyển đổi. Mặc định là 'converted_docs' trong thư mục hiện tại.
        :return: Đường dẫn tới file .docx đã lưu.
        """
        try:
            # Đảm bảo thư mục đích tồn tại
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Thư mục đích đã được xác định tại: {output_dir}")
            
            # Tạo file tạm thời với đuôi .doc
            with NamedTemporaryFile(delete=False, suffix=".doc") as tmp:
                tmp.write(file_bytes)
                doc_path = tmp.name
            logger.info(f"File tạm thời .doc đã được tạo tại: {doc_path}")
            
            # Tạo tên file .docx độc nhất
            unique_id = uuid.uuid4().hex
            docx_filename = f"converted_{unique_id}.docx"
            docx_path = os.path.join(output_dir, docx_filename)
            logger.info(f"Đường dẫn lưu file .docx sẽ là: {docx_path}")
            
            # Khởi tạo COM
            pythoncom.CoInitialize()
            
            # Khởi động ứng dụng Word
            word = client.Dispatch("Word.Application")
            word.Visible = False  # Ẩn cửa sổ Word
            word.DisplayAlerts = 0  # Tắt cảnh báo
            
            try:
                # Mở file .doc
                doc = word.Documents.Open(doc_path)
                logger.info(f"Đã mở file .doc tại: {doc_path}")
                
                # Lưu dưới dạng .docx (FileFormat=16)
                doc.SaveAs(docx_path, FileFormat=16)
                logger.info(f"Đã lưu file .docx tại: {docx_path}")
                
                # Đóng tài liệu
                doc.Close()
                logger.info(f"Đã đóng file .doc tại: {doc_path}")
            except Exception as e:
                logger.error(f"Lỗi khi chuyển đổi .doc sang .docx: {e}")
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
            
            return docx_path
        except Exception as e:
            logger.error(f"Đã xảy ra lỗi trong quá trình chuyển đổi: {e}")
            raise

# Ví dụ sử dụng:
if __name__ == "__main__":
    import sys

    # Kiểm tra xem có đường dẫn file .doc đầu vào không
    if len(sys.argv) != 2:
        print("Usage: python convert_doc.py <path_to_doc_file>")
        sys.exit(1)

    doc_file_path = sys.argv[1]

    # Đọc dữ liệu bytes từ file .doc
    try:
        with open(doc_file_path, "rb") as f:
            file_bytes = f.read()
    except FileNotFoundError:
        print(f"Không tìm thấy file: {doc_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Đã xảy ra lỗi khi đọc file: {e}")
        sys.exit(1)

    # Tạo instance của DocConverter và chuyển đổi
    converter = DocConverter()
    try:
        converted_path = converter.convert_doc_to_docx(file_bytes, output_dir="C:/Users/locfa/Documents/ConvertedDocs")
        print(f"Đã chuyển đổi thành công! File .docx được lưu tại: {converted_path}")
    except Exception as e:
        print(f"Đã xảy ra lỗi trong quá trình chuyển đổi: {e}")
