from bs4 import BeautifulSoup, NavigableString, Tag
from typing import List

def wrap_in_tag(content: str, tag: str, attrs: dict) -> str:
    """Tạo chuỗi HTML với tag và các thuộc tính đã cho."""
    if attrs:
        attr_str = " ".join(f'{key}="{value}"' for key, value in attrs.items())
        return f"<{tag} {attr_str}>{content}</{tag}>"
    else:
        return f"<{tag}>{content}</{tag}>"

class HtmlChunkSplitter:
    def __init__(self, max_length: int = 3000):
        self.max_length = max_length

    def split_sibling_elements(self, siblings, max_length: int = None, parent_tag: str = "div") -> List[str]:
        """
        Chia danh sách các phần tử con (sibling) thành các nhóm sao cho tổng độ dài của mỗi nhóm
        không vượt quá max_length. Mỗi nhóm sẽ được bao bọc trong thẻ (parent_tag) để giữ lại context.

        Nếu một sibling (với kiểu Tag) có chuỗi HTML vượt quá giới hạn, ta sẽ đệ quy chia nhỏ theo
        các thẻ con của nó.

        Args:
            siblings: Danh sách các phần tử (Tag hoặc NavigableString)
            max_length (int, optional): Giới hạn độ dài; nếu không truyền, dùng self.max_length.
            parent_tag (str, optional): Thẻ dùng để bao bọc mỗi nhóm. Mặc định là "div".
        Returns:
            List[str]: Danh sách các chuỗi HTML.
        """
        if max_length is None:
            max_length = self.max_length

        chunks = []
        current_group = []
        current_length = 0

        for sibling in siblings:
            # Nếu đối tượng chỉ chứa khoảng trắng thì bỏ qua
            if isinstance(sibling, NavigableString) and not sibling.strip():
                continue

            # Xác định chuỗi của sibling
            if isinstance(sibling, NavigableString):
                sibling_str = str(sibling)
                # Nếu chuỗi quá dài, chia theo ký tự (không thể chia theo tag)
                if len(sibling_str) > max_length:
                    # Nếu có dữ liệu đang tích lũy, hoàn thiện nhóm hiện tại
                    if current_group:
                        group_html = "".join(current_group)
                        group_html = f"<{parent_tag}>{group_html}</{parent_tag}>"
                        chunks.append(group_html)
                        current_group = []
                        current_length = 0
                    # Chia nhỏ văn bản theo ký tự
                    for i in range(0, len(sibling_str), max_length):
                        segment = sibling_str[i:i+max_length]
                        chunk = f"<{parent_tag}>{segment}</{parent_tag}>"
                        chunks.append(chunk)
                    continue
            elif isinstance(sibling, Tag):
                sibling_str = str(sibling)
                # Nếu chuỗi của tag vượt quá giới hạn, hãy thử chia theo nội dung con
                if len(sibling_str) > max_length:
                    if sibling.contents:
                        # Sử dụng hàm đệ quy để chia nhỏ tag theo con
                        split_chunks = self.split_tag_by_children(sibling, max_length)
                        chunks.extend(split_chunks)
                        continue
                    else:
                        # Nếu tag không có con (hoặc chỉ chứa văn bản), fallback: chia theo ký tự
                        for i in range(0, len(sibling_str), max_length):
                            segment = sibling_str[i:i+max_length]
                            chunks.append(segment)
                        continue
            else:
                # Nếu không thuộc hai loại trên, chuyển về chuỗi
                sibling_str = str(sibling)

            # Thêm sibling vào nhóm hiện tại nếu không vượt quá giới hạn
            if current_length + len(sibling_str) > max_length and current_group:
                group_html = "".join(current_group)
                group_html = f"<{parent_tag}>{group_html}</{parent_tag}>"
                chunks.append(group_html)
                current_group = [sibling_str]
                current_length = len(sibling_str)
            else:
                current_group.append(sibling_str)
                current_length += len(sibling_str)

        # Nếu còn dữ liệu trong nhóm cuối cùng, thêm vào danh sách
        if current_group:
            group_html = "".join(current_group)
            group_html = f"<{parent_tag}>{group_html}</{parent_tag}>"
            chunks.append(group_html)

        return chunks

    def split_tag_by_children(self, tag_element: Tag, max_length: int) -> List[str]:
        """
        Nếu một Tag có chuỗi HTML vượt quá giới hạn, ta sẽ lấy nội dung con của nó và chia nhỏ theo các con.
        Sau đó, bọc lại mỗi chunk bằng tag cha có các thuộc tính ban đầu.

        Args:
            tag_element (Tag): Phần tử HTML cần chia nhỏ.
            max_length (int): Giới hạn độ dài tối đa.
        Returns:
            List[str]: Danh sách các chuỗi HTML được chia nhỏ, mỗi chuỗi được bao bọc trong tag ban đầu.
        """
        # Lấy danh sách con
        children = tag_element.contents
        # Đệ quy chia nhỏ các con
        child_chunks = self.split_sibling_elements(children, max_length, parent_tag=tag_element.name)
        # Mỗi chunk hiện tại được tạo ra bởi split_sibling_elements có thể không giữ lại các thuộc tính của tag ban đầu.
        # Ta tái tạo lại tag với thuộc tính ban đầu.
        wrapped_chunks = []
        attrs = tag_element.attrs
        for chunk in child_chunks:
            # Lấy nội dung bên trong của chunk (loại bỏ tag bao bọc nếu cần)
            soup = BeautifulSoup(chunk, "html.parser")
            found = soup.find(tag_element.name)
            inner = found.decode_contents() if found else chunk
            wrapped = wrap_in_tag(inner, tag_element.name, attrs)
            wrapped_chunks.append(wrapped)
        return wrapped_chunks

    def merge_chunks(self, chunks: List[str], max_length: int, parent_tag: str = "div") -> List[str]:
        """
        Hợp nhất các chunk HTML đã được tách ra sao cho:
        - Các chunk sau khi gộp vẫn tuân theo thứ tự ban đầu.
        - Tổng độ dài của nội dung (inner HTML, không tính tag bao bọc) của mỗi chunk không vượt quá max_length.
        - Mỗi chunk sau khi ghép được bọc lại trong thẻ parent_tag.
        
        Args:
            chunks (List[str]): Danh sách các chunk HTML ban đầu (mỗi chunk đã được bọc trong parent_tag).
            max_length (int): Giới hạn độ dài tối đa cho nội dung (theo số ký tự hoặc token tùy trường hợp).
            parent_tag (str): Tên tag dùng để bao bọc các chunk, mặc định là "div".
        
        Returns:
            List[str]: Danh sách các chunk sau khi đã được gộp, theo đúng thứ tự ban đầu.
        """
        merged_chunks = []
        current_content = ""  # Nội dung bên trong của chunk đang tích lũy

        # Duyệt qua các chunk theo thứ tự ban đầu
        for chunk in chunks:
            # Sử dụng BeautifulSoup để trích xuất nội dung bên trong (inner HTML) của chunk.
            soup = BeautifulSoup(chunk, "html.parser")
            tag = soup.find(parent_tag)
            if tag:
                inner_html = tag.decode_contents()
            else:
                inner_html = chunk  # Fallback nếu không tìm thấy tag

            # Nếu cộng thêm nội dung mới không vượt quá giới hạn, tiến hành ghép
            if len(current_content) + len(inner_html) <= max_length:
                current_content += inner_html
            else:
                # Đóng gói nội dung đang tích lũy lại thành 1 chunk mới và lưu vào danh sách
                if current_content:
                    merged_chunk = f"<{parent_tag}>{current_content}</{parent_tag}>"
                    merged_chunks.append(merged_chunk)
                # Nếu nội dung mới (inner_html) vượt quá giới hạn riêng lẻ,
                # ta giữ nguyên chunk đó
                if len(inner_html) > max_length:
                    merged_chunks.append(f"<{parent_tag}>{inner_html}</{parent_tag}>")
                    current_content = ""
                else:
                    current_content = inner_html

        # Sau khi duyệt hết, nếu còn dữ liệu tích lũy thì đóng gói và thêm vào kết quả.
        if current_content:
            merged_chunks.append(f"<{parent_tag}>{current_content}</{parent_tag}>")

        return merged_chunks

if __name__ == "__main__":
    # Giả sử đây là danh sách các chunk ban đầu đã được tách theo hàm split_sibling_elements
    chunks = [
        '<div>Phần 1: Lorem ipsum dolor sit amet, </div>',
        '<div>Phần 2: consectetur adipiscing elit, </div>',
        '<div>Phần 3: sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</div>',
        '<div>Phần 4: Ut enim ad minim veniam, </div>',
        '<div>Phần 5: quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</div>',
    ]
    
    max_length = 100  # Giới hạn ví dụ (theo số ký tự)
    splitter = HtmlChunkSplitter(max_length=100)
    merged = splitter.merge_chunks(chunks, max_length, parent_tag="div")
    
    for idx, m_chunk in enumerate(merged):
        print(f"Chunk {idx+1}: {m_chunk}\n")
