# table_converter_helper.py

import uuid
from docx.oxml.ns import qn
import logging
from lxml import etree  # Để in/inspect toàn bộ XML

logger = logging.getLogger(__name__)


def inspect_tblPr_all_attrs(tblPr):
    """
    In ra toàn bộ thông tin của tblPr (bảng),
    bao gồm XML đầy đủ và các phần tử con, attr Python-level.
    """
    try:
        print("\n[inspect_tblPr_all_attrs] Start inspecting tblPr...")

        tblPr_xml = etree.tostring(tblPr, pretty_print=True, encoding='unicode')
        print("Full tblPr XML:")
        print(tblPr_xml)

        print("\n[inspect_tblPr_all_attrs] Dir(tblPr) => Tất cả attr, method:")
        for name in dir(tblPr):
            print(f" - {name} => {getattr(tblPr, name, None)}")

        print("\n[inspect_tblPr_all_attrs] Iterate children:")
        for child in tblPr.iterchildren():
            child_xml = etree.tostring(child, pretty_print=True, encoding='unicode')
            print(f"Child tag: {child.tag}\nXML: {child_xml}")

        print("[inspect_tblPr_all_attrs] Done.\n")

    except Exception as e:
        logger.error(f"Error in inspect_tblPr_all_attrs: {str(e)}")


def inspect_all_cell_attributes(table):
    """
    In ra toàn bộ thông tin (XML) của từng cell trong bảng,
    đặc biệt là phần tcPr để xem có attr gì.
    """
    try:
        print("\n[inspect_all_cell_attributes] Start inspecting cell attributes:")
        for row_idx, row in enumerate(table.rows):
            for col_idx, cell in enumerate(row.cells):
                cellPr = cell._element.find(qn('w:tcPr'))
                if cellPr is not None:
                    cellPr_xml = etree.tostring(cellPr, pretty_print=True, encoding='unicode')
                    print(f"\nCell ({row_idx}, {col_idx}) tcPr XML:\n{cellPr_xml}")

                else:
                    print(f"\nCell ({row_idx}, {col_idx}) has NO <w:tcPr> defined.")
        print("[inspect_all_cell_attributes] Done.\n")

    except Exception as e:
        logger.error(f"Error in inspect_all_cell_attributes: {str(e)}")

def extract_borders(tblBorders, is_table=True):
    """
    Trích xuất và chuyển đổi các thuộc tính đường viền từ tblBorders sang CSS.
    Giữ nguyên logic cũ, chỉ debug in ra nếu cần.
    """
    try:
        print(f"tblBorders: {tblBorders}")
        print("start extract_borders")
        borders_css = []
        if tblBorders is None:
            logger.debug("tblBorders is None. No borders to extract.")
            return ''
        
        border_types = ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']
        for border_type in border_types:
            border = getattr(tblBorders, border_type, None)
            print(f"border_type: {border_type}, border: {border}")
            if border is not None:
                val = getattr(border, 'val', None)
                sz = getattr(border, 'sz', None)
                color = getattr(border, 'color', None)
                space = getattr(border, 'space', None)

                logger.debug(f"Processing border_type={border_type}, val={val}, sz={sz}, color={color}")

                # Kiểm tra "nil"/"none"/"hidden" => skip
                if val in ('nil','none','hidden') or (sz is not None and int(sz) == 0):
                    logger.debug(f"Skipping border: {border_type} => no border (val={val}, sz={sz})")
                    continue

                # Nếu có val, sz, color => convert
                if val and sz and color:
                    try:
                        if color is None:
                            logger.debug(f"Border color is None => skip border {border_type}")
                            continue

                        if color.lower() == 'auto':
                            border_color = '#000000'
                            logger.debug(f"Border color='auto' => using black (#000000)")
                        else:
                            border_color = f'#{color}'

                        border_width_px = int(int(sz) / 20 * 1.333)

                        css_border_style = {
                            'single': 'solid',
                            'double': 'double',
                            'dotted': 'dotted',
                            'dashed': 'dashed',
                            'dotDash': 'dashdot',
                            'dotDotDash': 'dashdot',
                        }.get(val, 'solid')

                        if border_type in ['insideH', 'insideV']:
                            css_border_type = 'border-bottom' if border_type == 'insideH' else 'border-right'
                        else:
                            css_border_type = f'border-{border_type}'

                        border_css = f'{css_border_type}: {border_width_px}px {css_border_style} {border_color};'
                        borders_css.append(border_css)
                        logger.debug(f"Added border CSS: {border_css}")

                    except Exception as e:
                        logger.error(f"Error processing border_type={border_type}: {str(e)}")
                        continue
                else:
                    logger.debug(f"Skipping border {border_type}: missing val/sz/color => val={val}, sz={sz}, color={color}")
        
        return ' '.join(borders_css)

    except Exception as e:
        logger.error(f"Error in extract_borders: {str(e)}")
        raise


def extract_table_styles(tblPr):
    """
    Trích xuất các thuộc tính style khác từ tblPr (căn lề, background, ...).
    """
    try:
        logger.debug("start extract_table_styles")
        styles_css = []
        if tblPr is None:
            logger.debug("tblPr is None => no table styles.")
            return ''
        
        # 1) Table alignment
        tblJc = getattr(tblPr, 'jc', None)
        if tblJc is not None:
            alignment = getattr(tblJc, 'val', None)
            if alignment:
                styles_css.append(f'text-align: {alignment};')

        # 2) Background color
        tblShd = getattr(tblPr, 'tblShd', None)
        if tblShd is not None:
            fill = getattr(tblShd, 'val', None)
            if fill:
                styles_css.append(f'background-color: #{fill};')

        return ' '.join(styles_css)
    except Exception as e:
        logger.error(f"Error in extract_table_styles: {str(e)}")
        raise

def calculate_total_column_width(table):
    """
    Tính tổng độ rộng từ các cột trong bảng để thiết lập độ rộng của bảng.
    """
    try:
        print(f"table: {table}")
        print("start calculate_total_column_width")
        total_width_px = 0
        for column in table.columns:
            if column.width is not None:
                column_width_px = column.width / 914400 * 96
                logger.debug(f"Column width in EMU: {column.width}, in px: {column_width_px}")
                total_width_px += column_width_px
            else:
                logger.debug("Column width is None.")
        if total_width_px > 0:
            logger.debug(f"Total column width in px: {total_width_px}")
            return f'width: {int(total_width_px)}px;'
        logger.debug("Total column width is 0. Setting width to auto.")
        return 'width: auto;'
    except Exception as e:
        logger.error(f"Error in calculate_total_column_width: {str(e)}")
        raise


def apply_table_styles(table_tag, tblPr):
    """
    Áp dụng style + borders cho <table>.
    """
    try:
        logger.debug("start apply_table_styles")
        if tblPr is not None:
            table_styles_css = extract_table_styles(tblPr)
            if table_styles_css:
                if 'style' in table_tag.attrs:
                    table_tag['style'] += ' ' + table_styles_css
                else:
                    table_tag['style'] = table_styles_css
            
            tblBorders = getattr(tblPr, 'tblBorders', None)
            if tblBorders is not None:
                table_borders_css = extract_borders(tblBorders, is_table=True)
                if table_borders_css:
                    if 'style' in table_tag.attrs:
                        table_tag['style'] += ' ' + table_borders_css
                    else:
                        table_tag['style'] = table_borders_css
            else:
                logger.debug("tblBorders is None => no table borders.")
    except Exception as e:
        logger.error(f"Error in apply_table_styles: {str(e)}")
        raise

def apply_cell_styles(td_tag, cell):
    """
    Áp dụng style + borders cho <td> hoặc <th>.
    """
    try:
        cellPr = getattr(cell._element, 'tcPr', None)
        if cellPr is not None:
            tcBorders = getattr(cellPr, 'tcBorders', None)
            if tcBorders is not None:
                cell_borders_css = extract_borders(tcBorders, is_table=False)
                if cell_borders_css:
                    if 'style' in td_tag.attrs:
                        td_tag['style'] += ' ' + cell_borders_css
                    else:
                        td_tag['style'] = cell_borders_css
            
            tblShd = getattr(cellPr, 'tblShd', None)
            if tblShd is not None:
                fill = getattr(tblShd, 'val', None)
                if fill:
                    background_color = f'background-color: #{fill};'
                    if 'style' in td_tag.attrs:
                        td_tag['style'] += ' ' + background_color
                    else:
                        td_tag['style'] = background_color
    except Exception as e:
        logger.error(f"Error in apply_cell_styles: {str(e)}")
        raise

def convert_table_width(table):
    """
    Chuyển đổi độ rộng bảng từ DOCX sang CSS.
    """
    try:
        print(f"table: {table}")
        print("start convert_table_width")
        tblPr = getattr(table._element, 'tblPr', None)
        style = ''
        
        if tblPr is not None:
            tblW = getattr(tblPr, 'tblW', None)
            if tblW is not None:
                w_val = tblW.get(qn('w:w'))
                w_type = tblW.get(qn('w:type'))
                logger.debug(f"Table width: val={w_val}, type={w_type}")
                if w_type == 'pct' and w_val:
                    pct_value = int(w_val) / 100  # "5000" => 50%
                    style += f'width: {pct_value}%;'
                elif w_type == 'dxa' and w_val:
                    twips_val = int(w_val)
                    px_value = int(twips_val * 96 / 1440)  # xấp xỉ
                    style += f'width: {px_value}px;'
                elif w_type == 'auto':
                    style += 'width: auto; margin-left: auto; margin-right: auto;'
            else:
                logger.debug("tblW is None. Setting width to auto and centering table.")
                style += 'width: auto; margin-left: auto; margin-right: auto;'
        else:
            logger.debug("tblPr is None. Setting width to auto and centering table.")
            style += 'width: auto; margin-left: auto; margin-right: auto;'
        
        logger.debug(f"Table width CSS: {style}")
        return style
    except Exception as e:
        logger.error(f"Error in convert_table_width: {str(e)}")
        raise