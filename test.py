from docx import Document
from docx.enum.text import WD_TAB_LEADER

# 1. Mở file DOCX
doc = Document("Mẫu số 02d1.docx")

# 2. Duyệt qua từng paragraph để xử lý dot leader
for para in doc.paragraphs:
    # Xử lý tab stops: nếu leader = DOTS, đổi sang SPACES
    p_fmt = para.paragraph_format
    if p_fmt.tab_stops:
        for tstop in p_fmt.tab_stops:
            if tstop.leader == WD_TAB_LEADER.DOTS:
                # Có thể dùng WD_TAB_LEADER.NONE hoặc WD_TAB_LEADER.SPACES
                tstop.leader = WD_TAB_LEADER.SPACES

    # 3. Thay thế ký tự tab thực '\t' trong đoạn văn bằng chuỗi chấm thật
    # Số chấm bạn tuỳ ý chỉnh sửa (Ở đây là 10)
    para.text = para.text.replace('\t', '.' * 10)

# 4. Lưu ra file .docx mới đã chuyển dot leader
doc.save("Mẫu_số_02d1_chuyển_dot_leader.docx")
