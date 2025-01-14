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
            properties['font_size'] = run.font.size.pt if run.font.size else None
            properties['bold'] = run.font.bold
            properties['italic'] = run.font.italic
            properties['underline'] = run.font.underline
            if run.font.color and run.font.color.rgb:
                try:
                    color = run.font.color.rgb
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

    def group_runs_by_style(self, paragraph):
        try:
            try:
                runs = paragraph.runs
                groups = []
                if not runs:
                    return groups
            except Exception as e:
                logger.error(f"An error occurred: {e}")
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
                'text': clean_text(self.escape_html(runs[0].text))
            }
            
            for run in runs[1:]:
                run_style = self.get_style_properties(run)
                run_text = clean_text(self.escape_html(run.text))
                # print(f"@@@@@@@@@@@{run_text}")
                if run_style == current_group['style']:
                    current_group['text'] += run_text
                    current_group['text'] = clean_text(current_group['text'])
                else:
                    groups.append(current_group)
                    current_group = {'style': run_style, 'text': run_text}
            
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
            groups = self.group_runs_by_style(paragraph)
            groups = self.handle_hyperlinks(paragraph, groups)

            p_tag = self.soup.new_tag('p', style=f'text-align: {paragraph.alignment.name.lower()};' if paragraph.alignment else 'text-align: left;')

            for group in groups:
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

                text = group['text']

                # Regex tìm các chuỗi có dấu '.' liên tiếp từ 3 lần trở lên
                pattern = r'(\.{3,})'
                matches = list(re.finditer(pattern, text))
                
                last_end = 0
                for match in matches:
                    start = match.start()
                    end = match.end()

                    # Thêm đoạn văn bản trước match (nếu có)
                    if start > last_end:
                        remaining_text = text[last_end:start]
                        if remaining_text.strip():
                            span_tag = self.soup.new_tag('span', style='; '.join(style_str))
                            span_tag.string = remaining_text
                            p_tag.append(span_tag)

                    # Thêm chuỗi dấu '.' liên tiếp thành một span riêng với id
                    dots_segment = match.group(1)
                    span_tag = self.soup.new_tag('span', style='; '.join(style_str), id=str(uuid.uuid4()))
                    span_tag.string = dots_segment
                    p_tag.append(span_tag)

                    last_end = end

                # Thêm đoạn văn bản sau match cuối cùng (nếu có)
                if last_end < len(text):
                    remaining_text = text[last_end:]
                    if remaining_text.strip():
                        span_tag = self.soup.new_tag('span', style='; '.join(style_str))
                        span_tag.string = remaining_text
                        p_tag.append(span_tag)

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
            table_tag = self.soup.new_tag('table', border='1')
            rows = list(table.rows)
            row_count = len(rows)
            col_count = len(rows[0].cells) if row_count > 0 else 0

            for i in range(row_count):
                row = rows[i]
                tr_tag = self.soup.new_tag('tr')
                for j in range(col_count):
                    cell = row.cells[j]
                    # Check if this cell is already part of a merge
                    if cell._element.vMerge and cell._element.vMerge.val == 'continue':
                        continue  # Skip merged cells
                    td_tag = self.soup.new_tag('td')
                    # Handle colspan
                    if cell.grid_span > 1:
                        td_tag['colspan'] = str(cell.grid_span)
                    # Handle rowspan
                    if cell._element.vMerge and cell._element.vMerge.val == 'restart':
                        # Count how many rows this cell spans
                        rowspan = 1
                        for k in range(i + 1, row_count):
                            next_cell = rows[k].cells[j]
                            if next_cell._element.vMerge and next_cell._element.vMerge.val == 'continue':
                                rowspan += 1
                            else:
                                break
                        if rowspan > 1:
                            td_tag['rowspan'] = str(rowspan)
                    # Process cell content
                    for paragraph in cell.paragraphs:
                        p_html = self.convert_paragraph(paragraph)
                        self.append_elements(td_tag, p_html)
                    # Handle nested tables
                    for nested_table in cell.tables:
                        table_html = self.convert_tables(nested_table)
                        self.append_elements(td_tag, table_html)
                    tr_tag.append(td_tag)
                table_tag.append(tr_tag)
            return table_tag
        except Exception as e:
            logger.error(f"An error occurred convert_tables: {e}")
            return None

    def append_elements(self, parent, elements):
        try:
            if isinstance(elements, list):
                for el in elements:
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

            print(f"@@@@@@@@@@@{html}\n")
            return html.prettify()
        except Exception as e:
            logger.error(f"An error occurred convert_document: {e}")
            return None
