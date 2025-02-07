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
from app.helpers.table_helper import TableHelper
from lxml import etree

logger = logging.getLogger(__name__)

def twips_to_pixels(twips):
    """
    Chuyển đổi từ đơn vị twips (dxa) sang pixel.
    1 twip = 1/20 điểm, và 1 điểm = 1.333 pixel (cho 96 DPI).
    Công thức:
    pixels = twips * (1 / 20) * 1.333
    """
    return twips * (1 / 20) * 1.333

def is_header_row(row):
    """
    Kiểm tra <w:tblHeader> trong XML của row.
    Nếu row có <w:tblHeader>, ta coi row này là header.
    """
    tr_element = row._element
    trPr = tr_element.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}trPr')
    if trPr is not None:
        tblHeader = trPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tblHeader')
        if tblHeader is not None:
            return True
    return False

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
                        .replace('\t', '...')
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
                # Debug tùy ý
                run_style = self.get_style_properties(run)
                run_text = clean_text(self.escape_html(run.text))

                # So sánh style cũ với run_style mới
                # Nếu cùng style và run_text không chứa \n => gộp
                # Ngược lại => tách group
                if (run_style == current_group['style']
                    and '\n' not in run_text
                    and '\r' not in run_text
                    ):
                    current_group['text'] += run_text
                    current_group['text'] = clean_text(current_group['text'])
                else:
                    groups.append(current_group)
                    current_group = {
                        'style': run_style,
                        'text': run_text,
                        'run': run
                    }

            # Append group cuối
            groups.append(current_group)

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
                if group['text'].strip() == '':
                    # Nếu nhóm có text trống, chèn <br/>
                    br_tag = self.soup.new_tag('br')
                    p_tag.append(br_tag)
                    continue  # Bỏ qua phần xử lý text
                # -- Build style_str (giữ nguyên logic cũ) --
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

                # if group['text'].strip() == '':
                #     group['text'] = "\n"

                # text ở đây có thể chứa \n hoặc \r (xuống dòng mềm)
                text = group['text']

                # Tách text theo dòng (khi SHIFT+ENTER => Word gộp vào .text có ký tự \n)
                # splitlines(keepends=False) -> cắt \n, \r\n ra
                lines = text.splitlines()

                # Duyệt từng dòng, với logic regex(\.{3,}) cũ
                for idx, line_content in enumerate(lines):
                    # --- Áp regex tìm '...' ---
                    pattern = r'(\.{3,})'
                    matches = list(re.finditer(pattern, line_content))

                    last_end = 0

                    # Tạo 1 <span> cho dòng này
                    line_span = self.soup.new_tag('span')
                    if final_style:
                        line_span['style'] = final_style

                    for match in matches:
                        start, end = match.span()
                        if start > last_end:
                            sub_text = line_content[last_end:start]
                            line_span.append(sub_text)

                        dots_sub = self.soup.new_tag('span', id=str(uuid.uuid4()))
                        if final_style:
                            dots_sub['style'] = final_style
                        dots_sub.string = match.group(1)
                        line_span.append(dots_sub)
                        last_end = end

                    # Đoạn còn lại sau match cuối
                    if last_end < len(line_content):
                        remaining_text = line_content[last_end:]
                        line_span.append(remaining_text)

                    # Đưa line_span vào p_tag
                    p_tag.append(line_span)

                    # Nếu chưa phải dòng cuối => chèn <br> để xuống dòng
                    # (vì SHIFT+ENTER => "xuống dòng mềm" trong cùng paragraph)
                    if idx < len(lines) - 1:
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
        """
        Chuyển docx.table.Table -> <table> HTML
        Tích hợp logic chia thead/tbody (is_header_row),
        in ra tblPr, cell attrs, ...
        """
        try:
            table_tag = self.soup.new_tag('table')

            # 1) Extract table properties using TableHelper logic
            helper = TableHelper(table)
            table_props = helper.get_all_properties()
            # print("##########$$$$$$$$$$$$$$$############\n", table_props)

            # Table properties
            alignment = table_props['alignment']
            # print("##########$$$$$$$$$$$$$$$############alignment\n", alignment)
            allow_autofit = table_props['allow_autofit']
            # print("##########!!!!!!!!!!!!!!!############allow_autofit\n", allow_autofit)
            table_width_info = table_props['table_width']
            # print("##########@@@@@@@@@@@@@@@############table_width_info\n", table_width_info)
            table_borders = table_props['borders']
            # print("##########***************############table_borders\n", table_borders)
            table_look = table_props['table_look']
            # print("##########!!!!!!!!!!!!!!!############table_look\n", table_look)
            columns_width = table_props['columns_width']
            # print("##########@@@@@@@@@@@@@@@############columns_width\n", columns_width)
            rows_height = table_props['rows_height']
            # print("##########***************############\n", rows_height)
            cells_properties = table_props['cells_properties']
            # print("##########!!!!!!!!!!!!!!!############cells_properties\n", cells_properties)

            # 2) Table width
            table_width_type = table_width_info.get('type')
            table_width_value = table_width_info.get('width')

            if table_width_type == 'dxa' and table_width_value is not None:
                table_width_px = twips_to_pixels(table_width_value)
                table_tag['style'] = f'width: {table_width_px}px;'
            elif table_width_type == 'pct' and table_width_value is not None:
                # pct = table_width_value / 50  # vì w:w="5000" tương đương 100%
                # table_tag['style'] = f'width: {pct}%;'
                table_tag['style'] = 'width: 100%;'
            elif table_width_type == 'auto':
                table_tag['style'] = 'width: auto;'
            else:
                table_tag['style'] = 'width: 100%;'  # Mặc định nếu không xác định

            # 3) Table alignment
            if alignment == 'center':
                table_tag['style'] += ' margin-left: auto; margin-right: auto;'
            elif alignment in ['right', 'end']:
                table_tag['style'] += ' margin-left: auto;'
            # Left or None: không cần thêm style margin

            # 4) Table borders
            if table_borders:
                border_styles = []
                for side, props in table_borders.items():
                    sz = props.get("sz")
                    if props["val"] != "none" and sz is not None:
                        try:
                            sz_pt = int(sz) / 8  # w:sz là đơn vị e-1/8 point
                            color = props["color"] if props["color"] != "auto" else "000000"
                            border_styles.append(f'{side}-border: {sz_pt}pt {props["val"]} #{color};')
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid border size for {side}: sz={sz}")
                            continue
                if border_styles:
                    border_style_str = ' '.join(border_styles)
                    print("##########$$$$$$$$$$$$$$$############border_style_str\n", border_style_str)
                    table_tag['style'] += f' border-collapse: collapse; {border_style_str}'
            
            # 6) Xử lý columns_width
            if not allow_autofit and columns_width and len(columns_width) > 0:
                # Tính tổng chiều rộng các cột
                total_width_px = sum(columns_width)
                if total_width_px > 0:
                    # Tính tỷ lệ phần trăm cho mỗi cột
                    columns_pct = [(width / total_width_px) * 100 for width in columns_width]
                    # Tạo colgroup
                    colgroup_tag = self.soup.new_tag('colgroup')
                    for pct in columns_pct:
                        col_tag = self.soup.new_tag('col')
                        col_tag['style'] = f'width: {pct:.2f}%;'
                        colgroup_tag.append(col_tag)
                    table_tag.insert(0, colgroup_tag)  # Chèn colgroup vào đầu bảng
            else:
                # Nếu allow_autofit là True hoặc không có columns_width, không thiết lập width cho cột
                pass

            # 5) Tách thead/tbody
            rows = list(table.rows)
            row_count = len(rows)
            logger.debug(f"Number of rows in table: {row_count}")
            if row_count == 0:
                logger.debug("Table has no rows => return <table> empty")
                return table_tag

            col_count = len(rows[0].cells)
            logger.debug(f"Number of columns in table: {col_count}")

            head_rows = []
            body_rows = []
            for row in rows:
                if is_header_row(row):
                    head_rows.append(row)
                else:
                    body_rows.append(row)

            # Tạo thead
            if head_rows:
                thead = self.soup.new_tag('thead')
                for row in head_rows:
                    tr_html = self._convert_row(row, table, cells_properties, rows_height, is_header=True)
                    thead.append(tr_html)
                table_tag.append(thead)

            # Tạo tbody
            if body_rows:
                tbody = self.soup.new_tag('tbody')
                for row in body_rows:
                    tr_html = self._convert_row(row, table, cells_properties, rows_height, is_header=False)
                    tbody.append(tr_html)
                table_tag.append(tbody)

            # 7) Áp dụng table_look nếu cần (ví dụ: thêm class hoặc data attributes)
            if table_look:
                # Ví dụ: thêm class dựa trên table_look['val']
                look_val = table_look.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                if look_val:
                    table_tag['class'] = f'table-look-{look_val}'
                # Bạn có thể mở rộng thêm các thuộc tính khác từ table_look nếu cần

            return table_tag

        except Exception as e:
            logger.error(f"An error occurred convert_tables: {str(e)}")
            return None



    def _convert_row(self, row, table, cells_properties, rows_height, is_header=False):
        """
        row: docx.table._Row
        is_header: True => <th>, False => <td>
        """
        tr_tag = self.soup.new_tag('tr')

        # Xử lý chiều cao của hàng
        trPr = row._element.find(qn('w:trPr'))
        if trPr is not None:
            trHeight = trPr.find(qn('w:trHeight'))
            if trHeight is not None:
                val = trHeight.get(qn('w:val'))
                w = trHeight.get(qn('w:w'))
                if w and val in ['exact', 'atLeast']:
                    try:
                        height_twips = int(w)
                        height_px = twips_to_pixels(height_twips)
                        tr_tag['style'] = f'height: {height_px}px;'
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid row height: w={w}, val={val}")
                        pass  # Có thể đặt một giá trị mặc định hoặc bỏ qua

        # **Bước 1: Thu thập và chuẩn hóa chiều rộng của tất cả các ô trong hàng**
        total_width_units = 0
        cell_width_units = []

        for col_idx, cell in enumerate(row.cells):
            cell_info = cells_properties[row._index][col_idx]
            width_info = cell_info.get('width')
            cell_width = 0  # Khởi tạo với 0

            if width_info:
                width_type = width_info.get('type')
                width_value = width_info.get('width')

                if width_type == 'dxa' and width_value is not None:
                    # Chuyển đổi từ dxa (twips) sang đơn vị tiêu chuẩn (ví dụ: pixel)
                    cell_width = twips_to_pixels(int(width_value))
                elif width_type == 'pct' and width_value is not None:
                    # Chuyển đổi phần trăm sang đơn vị tiêu chuẩn (giả sử 100% = 1000 units)
                    # Bạn có thể chọn đơn vị chuẩn khác tùy thuộc vào yêu cầu
                    cell_width = float(width_value)  # Giữ nguyên giá trị phần trăm
                else:
                    # Xử lý các loại width khác nếu cần hoặc đặt giá trị mặc định
                    cell_width = 0

            # Nếu không có thông tin width, đặt giá trị mặc định
            if width_info is None or width_value is None:
                cell_width = 0  # Bạn có thể thay đổi giá trị mặc định này nếu cần

            cell_width_units.append(cell_width)
            total_width_units += cell_width

        # **Bước 2: Tính tổng chiều rộng nếu tất cả các ô không có thông tin width**
        # Nếu tổng width_units bằng 0, chúng ta sẽ chia đều 100% cho tất cả các ô
        if total_width_units == 0:
            num_cells = len(row.cells)
            cell_percentages = [100 / num_cells] * num_cells
        else:
            # **Bước 3: Tính tỷ lệ phần trăm cho từng ô dựa trên tổng chiều rộng**
            cell_percentages = [
                (width / total_width_units) * 100 if total_width_units > 0 else 0
                for width in cell_width_units
            ]

        # **Bước 4: Lặp qua các ô và gán chiều rộng theo tỷ lệ phần trăm**
        for col_idx, cell in enumerate(row.cells):
            cell_info = cells_properties[row._index][col_idx]
            tag_name = 'th' if is_header else 'td'
            td_tag = self.soup.new_tag(tag_name)

            # Xử lý colspan
            colspan = cell_info.get('grid_span', 1)
            if colspan > 1:
                td_tag['colspan'] = str(colspan)

            # Xử lý rowspan
            v_merge = cell_info.get('v_merge')
            rowspan = 1
            if v_merge == 'restart':
                # Đếm số hàng tiếp theo có v_merge == 'continue'
                span_count = 1
                for next_row in table.rows[row._index + 1:]:
                    if next_row._index >= len(cells_properties):
                        break
                    next_cell = next_row.cells[col_idx]
                    next_cell_info = cells_properties[next_row._index][col_idx]
                    if next_cell_info.get('v_merge') == 'continue':
                        span_count += 1
                    else:
                        break
                rowspan = span_count
                if rowspan > 1:
                    td_tag['rowspan'] = str(rowspan)

            # **Gán chiều rộng theo tỷ lệ phần trăm**
            pct = cell_percentages[col_idx]
            td_tag['style'] = f'width: {pct:.2f}%;'  # Định dạng với 2 chữ số thập phân

            # Xử lý căn chỉnh dọc
            vertical_alignment = cell_info.get('vertical_alignment')
            if vertical_alignment:
                if vertical_alignment.lower() == 'center':
                    valign_style = 'vertical-align: middle;'
                elif vertical_alignment.lower() == 'bottom':
                    valign_style = 'vertical-align: bottom;'
                elif vertical_alignment.lower() == 'top':
                    valign_style = 'vertical-align: top;'
                else:
                    valign_style = ''
                if 'style' in td_tag.attrs:
                    td_tag['style'] += f' {valign_style}'
                else:
                    td_tag['style'] = f'{valign_style}'
            else:
                # Mặc định vertical-align: top;
                td_tag['style'] += ' vertical-align: top;'

            # Xử lý borders ô nếu có
            borders = cell_info.get('borders', {})
            if borders:
                cell_border_styles = []
                for side, props in borders.items():
                    sz = props.get("sz")
                    val = props.get("val")
                    if (val not in ["none", "nil"]) and sz is not None:
                        try:
                            color = props.get("color", "000000") if props.get("color") != "auto" else "000000"
                            sz_pt = int(sz) / 8  # w:sz là đơn vị e-1/8 point
                            cell_border_styles.append(f'{side}-border: {sz_pt}pt {val} #{color};')
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid border size for {side}: sz={sz}")
                            continue
                if cell_border_styles:
                    border_style_str = ' '.join(cell_border_styles)
                    if 'style' in td_tag.attrs:
                        td_tag['style'] += f' {border_style_str}'
                    else:
                        td_tag['style'] = f'{border_style_str}'
            else:
                # Nếu không có viền nào được thiết lập cho ô, thêm viền mặc định
                td_tag['style'] += ' border: 1px solid black;'

            # Xử lý nội dung của ô
            for paragraph in cell.paragraphs:
                p_html = self.convert_paragraph(paragraph)
                self.append_elements(td_tag, p_html)

            for nested_table in cell.tables:
                nested_html = self.convert_tables(nested_table)
                self.append_elements(td_tag, nested_html)

            tr_tag.append(td_tag)

        return tr_tag

        
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
                table, th, td { padding: 20px; text-align: left; }
                img { max-width: 100%; height: auto; }
                ul, ol { margin: 0; padding-left: 40px; }
                td {vertical-align: top;}
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

            return html.prettify()
        except Exception as e:
            logger.error(f"An error occurred convert_document: {e}")
            return None
