import uuid
from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
import base64
from docx.shared import RGBColor
from bs4 import BeautifulSoup
import re
from docx.image.exceptions import UnrecognizedImageError
import logging

logger = logging.getLogger(__name__)

class DocxToHtmlConverter:
    def __init__(self, input_path):
        self.doc = Document(input_path)
        self.soup = BeautifulSoup('<html><head></head><body></body></html>', 'html.parser')
        self.list_stack = []
        self.nsmap = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    def escape_html(self, text):
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

    def get_style_properties(self, run):
        try:
            properties = {}
            font = run.font
            
            properties['font_size'] = font.size.pt if font.size else None
            properties['bold'] = font.bold
            properties['italic'] = font.italic
            properties['underline'] = font.underline
            properties['strikethrough'] = font.strike
            properties['font_name'] = font.name
            # properties['font_family'] = font.family
            properties['small_caps'] = font.small_caps
            properties['all_caps'] = font.all_caps
            properties['superscript'] = font.superscript
            properties['subscript'] = font.subscript

            if font.highlight_color:
                properties['highlight_color'] = font.highlight_color
            else:
                properties['highlight_color'] = None

            if font.color and font.color.rgb:
                try:
                    color = font.color.rgb
                    if isinstance(color, RGBColor) and hasattr(color, 'r') and hasattr(color, 'g') and hasattr(color, 'b'):
                        rgb_int = (color.r << 16) + (color.g << 8) + color.b
                        properties['color'] = rgb_int
                    else:
                        properties['color'] = None
                except AttributeError:
                    properties['color'] = None
            else:
                properties['color'] = None
            return properties
        except Exception as e:
            logger.error(f"An error occurred get_style_properties: {e}")
            return None

    def build_style_str(self, style_dict):
        """
        Từ dictionary mô tả style (font_size, bold, italic,...),
        trả về một chuỗi style hợp lệ (hoặc None nếu không có thuộc tính).
        """
        style_parts = []

        if style_dict.get('font_size'):
            style_parts.append(f'font-size: {style_dict["font_size"]}pt')
        if style_dict.get('bold'):
            style_parts.append('font-weight: bold')
        if style_dict.get('italic'):
            style_parts.append('font-style: italic')
        if style_dict.get('underline'):
            style_parts.append('text-decoration: underline')
        if style_dict.get('color'):
            # color là kiểu int (RGB), format thành hex 6 ký tự
            style_parts.append(f'color: #{style_dict["color"]:06X}')

        # Nếu không có thuộc tính style nào, trả về None
        if style_parts:
            return "; ".join(style_parts)
        return None

    def group_runs_by_style(self, paragraph):
        try:
            runs = paragraph.runs
            groups = []
            if not runs:
                return groups
            
            def clean_text(text):
                """Hàm làm sạch văn bản"""
                try:
                    return (
                        text.replace('…', '...')
                        .replace(' ', ' ')  # Thay khoảng trắng không phải ASCII bằng khoảng trắng chuẩn
                        .replace('. .', '...')
                        .replace('.. ', '...')
                        .replace(' ..', '...')
                        .replace('./.', '...')
                        .replace('/ ..', '...')
                        .replace('/..', '...')
                        .replace('./ ', '...')
                        .replace('/ .', '...')
                        .replace(' ..', '...')
                        # .replace('  ', ' ')  # Loại bỏ khoảng trắng thừa
                        # .strip()  # Xóa khoảng trắng đầu và cuối chuỗi
                    )
                except Exception as e:
                    logger.error(f"An error occurred: {e}")
                    return text

            current_group = {
                'style': self.get_style_properties(runs[0]),
                'text': clean_text(self.escape_html(runs[0].text)),
                # LƯU LẠI RUN ĐỂ DÙNG Ở convert_paragraph
                'run': runs[0]
            }
            
            for run in runs[1:]:
                run_style = self.get_style_properties(run)
                run_text = clean_text(self.escape_html(run.text))
                # print(f"@@@@@@@@@@@{run_text}")
                if run_style == current_group['style']:
                    current_group['text'] += run_text
                else:
                    groups.append(current_group)
                    current_group = {
                        'style': run_style,
                        'text': run_text,
                        'run': run  # Lưu run
                    }
            
            groups.append(current_group)
            
            # for group in groups:
            #     # In ra nội dung để kiểm tra
            #     print(f"@@@@@@@@@@@{group['text']}")
            
            return groups
        except Exception as e:
            logger.error(f"An error occurred group_runs_by_style: {e}")
            return None

    def handle_hyperlinks(self, paragraph, groups):
        try:
            hyperlinks = paragraph._element.findall('.//w:hyperlink', namespaces=self.nsmap)
            for hyperlink in hyperlinks:
                runs = hyperlink.findall('.//w:r', namespaces=self.nsmap)
                text = ''.join([self.escape_html(run.text) for run in runs])
                href = hyperlink.get(qn('r:href'))
                for group in groups:
                    if group['text'] == text:
                        group['text'] = f'<a href="{href}">{text}</a>'
            return groups
        except Exception as e:
            logger.error(f"An error occurred handle_hyperlinks: {e}")
            return None

    def convert_paragraph(self, paragraph):
        try:
            # 1) Gom nhóm runs có cùng style
            groups = self.group_runs_by_style(paragraph)
            # 2) Xử lý hyperlink
            groups = self.handle_hyperlinks(paragraph, groups)

            # Tạo p_tag với text-align
            p_tag = self.soup.new_tag(
                'p',
                style=f'text-align: {paragraph.alignment.name.lower()};'
                if paragraph.alignment else 'text-align: left;'
            )

            for group in groups:
                # Xây dựng style string (GIỮ NGUYÊN LOGIC CŨ)
                style_str = []
                if group['style']['font_size']:
                    style_str.append(f'font-size: {group["style"]["font_size"]}pt')
                if group['style']['bold']:
                    style_str.append('font-weight: bold')
                if group['style']['italic']:
                    style_str.append('font-style: italic')
                if group['style']['underline']:
                    style_str.append('text-decoration: underline')
                if group['style']['color']:
                    style_str.append(f'color: #{group["style"]["color"]:06X}')

                final_style = '; '.join(style_str) if style_str else None

                text = group['text']
                run_element = group.get('run')

                # --- Bắt SHIFT+ENTER (w:br / w:br w:type="textWrapping") ---
                # GIỮ NGUYÊN logic cũ, chỉ bổ sung tìm <w:cr> nếu cần
                br_count = 0
                if run_element is not None:
                    # Lấy tất cả <w:br> (kể cả w:type="textWrapping")
                    br_elements = run_element._element.findall('.//w:br', namespaces=self.nsmap)
                    br_count += len(br_elements)

                    # (Tùy chọn) Bắt thêm <w:cr> (ít gặp, nhưng Word đôi khi lưu SHIFT+ENTER là w:cr)
                    cr_elements = run_element._element.findall('.//w:cr', namespaces=self.nsmap)
                    br_count += len(cr_elements)
                # Giờ br_count = tổng số break (kể cả SHIFT+ENTER)

                # Xử lý regex (\.{3,})
                pattern = r'(\.{3,})'
                matches = list(re.finditer(pattern, text))

                last_end = 0
                # Tạo một <span> cho nhóm này
                main_span = self.soup.new_tag('span')
                if final_style:
                    main_span['style'] = final_style

                for match in matches:
                    start, end = match.span()
                    if start > last_end:
                        sub_text = text[last_end:start]
                        main_span.append(sub_text)

                    dots_sub = self.soup.new_tag('span', id=str(uuid.uuid4()))
                    if final_style:
                        dots_sub['style'] = final_style
                    dots_sub.string = match.group(1)
                    main_span.append(dots_sub)

                    last_end = end

                # Đoạn còn lại sau match cuối
                if last_end < len(text):
                    remaining_text = text[last_end:]
                    main_span.append(remaining_text)

                # Đưa <span> chính vào p_tag
                p_tag.append(main_span)

                # Chèn <br> tương ứng br_count
                # SHIFT+ENTER => br_count++
                for _ in range(br_count):
                    br_tag = self.soup.new_tag('br')
                    p_tag.append(br_tag)

            return p_tag

        except Exception as e:
            logger.error(f"An error occurred convert_paragraph: {e}")
            return None

    
    def is_list_paragraph(self, paragraph):
        try:
            pPr = paragraph._element.pPr
            if pPr is not None and pPr.numPr is not None and pPr.numPr.numId is not None:
                return True
            return False
        except Exception as e:
            logger.error(f"An error occurred is_list_paragraph: {e}")
            return None

    def convert_list_item(self, paragraph):
        try:
            li_tag = self.soup.new_tag('li')
            li_tag.string = paragraph.text
            return li_tag
        except Exception as e:
            logger.error(f"An error occurred convert_list_item: {e}")
            return None

    def handle_list(self, list_item):
        try:
            if not self.list_stack:
                ul_tag = self.soup.new_tag('ul')
                ul_tag.append(list_item)
                self.soup.body.append(ul_tag)
                self.list_stack.append(ul_tag)
            else:
                self.list_stack[-1].append(list_item)
            return list_item
        except Exception as e:
            logger.error(f"An error occurred handle_list: {e}")
            return None

    def convert_headings(self, paragraph):
        try:
            if paragraph.style and paragraph.style.type == WD_STYLE_TYPE.PARAGRAPH and paragraph.style.name.startswith('Heading'):
                level = int(paragraph.style.name.replace('Heading ', ''))
                heading_tag = f'h{level}'
                h_tag = self.soup.new_tag(heading_tag)
                h_tag.string = paragraph.text
                return h_tag
            return None
        except Exception as e:
            logger.error(f"An error occurred convert_headings: {e}")
            return None

    def convert_tables(self, table):
        try:
            # Tạo thẻ <table> trong soup
            table_tag = self.soup.new_tag('table', border='1')

            # NOTE: Lấy tblPr, sau đó dùng getattr(tblPr, 'tblW', None)
            # để tránh lỗi 'CT_TblPr' object has no attribute 'tblW'
            tblPr = table._element.tblPr
            if tblPr is not None:
                from docx.oxml.ns import qn
                tblW = getattr(tblPr, 'tblW', None)
                if tblW is not None:
                    w_val = tblW.get(qn('w:w'))
                    w_type = tblW.get(qn('w:type'))
                    # Nếu kiểu là pct => % width
                    if w_type == 'pct' and w_val:
                        pct_value = int(w_val) / 100  # "5000" => 50%
                        table_tag['style'] = f'width: {pct_value}%;'
                    # Nếu kiểu là dxa => twips => chuyển sang px
                    elif w_type == 'dxa' and w_val:
                        twips_val = int(w_val)
                        px_value = int(twips_val * 96 / 1440)  # xấp xỉ
                        table_tag['style'] = f'width: {px_value}px;'
                    # w_type == 'auto' => không set width => để auto

            # NOTE: Kiểm tra số hàng
            rows = list(table.rows)
            row_count = len(rows)
            if row_count == 0:
                # Bảng không có hàng, trả về table_tag rỗng
                return table_tag

            col_count = len(rows[0].cells)

            # Duyệt từng row => cell
            for i in range(row_count):
                row = rows[i]
                tr_tag = self.soup.new_tag('tr')

                for j in range(col_count):
                    cell = row.cells[j]
                    # NOTE: Kiểm tra merge dọc "tiếp tục"
                    if cell._element.vMerge and cell._element.vMerge.val == 'continue':
                        continue  # Skip merged cells

                    td_tag = self.soup.new_tag('td')

                    # Xử lý colspan (horizontal merge)
                    if cell.grid_span > 1:
                        td_tag['colspan'] = str(cell.grid_span)

                    # Xử lý rowspan (vertical merge)
                    if cell._element.vMerge and cell._element.vMerge.val == 'restart':
                        rowspan = 1
                        for k in range(i + 1, row_count):
                            next_cell = rows[k].cells[j]
                            if next_cell._element.vMerge and next_cell._element.vMerge.val == 'continue':
                                rowspan += 1
                            else:
                                break
                        if rowspan > 1:
                            td_tag['rowspan'] = str(rowspan)

                    # Xử lý nội dung paragraph trong cell
                    for paragraph in cell.paragraphs:
                        p_html = self.convert_paragraph(paragraph)
                        # NOTE: Kiểm tra None
                        if p_html is not None:
                            self.append_elements(td_tag, p_html)

                    # Xử lý bảng lồng bên trong cell
                    for nested_table in cell.tables:
                        table_html = self.convert_tables(nested_table)
                        if table_html is not None:
                            self.append_elements(td_tag, table_html)

                    tr_tag.append(td_tag)
                table_tag.append(tr_tag)

            return table_tag

        except Exception as e:
            logger.error(f"An error occurred convert_tables: {e}")
            return None


    def append_elements(self, parent, elements):
        try:
            if elements is None:
                return  # Không chèn gì nếu elements là None

            if isinstance(elements, list):
                for el in elements:
                    if el is not None:
                        parent.append(el)
            else:
                parent.append(elements)
        except Exception as e:
            logger.error(f"An error occurred append_elements: {e}")
            return None

    def convert_document(self):
        try:
            html = BeautifulSoup('', 'html.parser')
            head = html.new_tag('head')
            style = html.new_tag('style')
            style.string = """
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1, h2, h3, h4, h5, h6 { color: #2e6c80; }
                table { border-collapse: collapse; width: 100%; }
                table, th, td { border: 1px solid #dddddd; padding: 8px; text-align: left; }
                img { max-width: 100%; height: auto; }
                ul, ol { margin: 0; padding-left: 40px; }
                p { margin: 0 0 1em 0; }
            """
            head.append(style)
            html.append(head)
            body = html.new_tag('body')
            html.append(body)

            if self.doc.sections:
                first_section = self.doc.sections[0]
                top_pt = first_section.top_margin.pt
                right_pt = first_section.right_margin.pt
                bottom_pt = first_section.bottom_margin.pt
                left_pt = first_section.left_margin.pt

                # Chuyển points -> px (1 pt ~ 1.3333 px)
                top_px = int(top_pt * 1.3333)
                right_px = int(right_pt * 1.3333)
                bottom_px = int(bottom_pt * 1.3333)
                left_px = int(left_pt * 1.3333)

                # Gán margin vào body style
                margin_style = f"margin: {top_px}px {right_px}px {bottom_px}px {left_px}px;"
                body['style'] = margin_style

            for element in self.doc._element.body.iterchildren():
                if element.tag == f'{{{self.nsmap["w"]}}}p':
                    paragraph = Paragraph(element, self.doc)
                    if self.is_list_paragraph(paragraph):
                        list_item = self.convert_list_item(paragraph)
                        self.handle_list(list_item)
                    else:
                        heading = self.convert_headings(paragraph)
                        if heading:
                            self.append_elements(body, heading)
                        else:
                            p_tags = self.convert_paragraph(paragraph)
                            # print(f"@@@@@@@@@@@{p_tags}\n")
                            # print(f"@@@@@@@@@@@{paragraph.runs.text}\n")
                            self.append_elements(body, p_tags)
                elif element.tag == f'{{{self.nsmap["w"]}}}tbl':
                    table = Table(element, self.doc)
                    table_tag = self.convert_tables(table)
                    self.append_elements(body, table_tag)
                elif element.tag == f'{{{self.nsmap["w"]}}}drawing':
                    for inline in element.findall('.//w:inline', namespaces=self.nsmap):
                        try:
                            image_part = inline.find('.//wp:docPr', namespaces=self.nsmap).get('id')
                            image = self.doc.part.related_parts[image_part]
                            image_data = image.blob
                            image_base64 = base64.b64encode(image_data).decode('utf-8')
                            img_tag = self.soup.new_tag('img', src=f'data:{image.content_type};base64,{image_base64}')
                            self.append_elements(body, img_tag)
                        except UnrecognizedImageError:
                            pass

            # print(f"@@@@@@@@@@@{html}\n")
            return html.prettify()
        except Exception as e:
            logger.error(f"An error occurred convert_document: {e}")
            return None
