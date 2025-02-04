# table_converter_helper.py

import uuid
from docx.oxml.ns import qn
import logging
from lxml import etree  # Để in/inspect toàn bộ XML

logger = logging.getLogger(__name__)

def twips_to_pixels(twips):
    return int(twips * (96 / 1440))  # 96 DPI is standard for screens

def inspect_tblPr_all_attrs(tblPr):
    """
    In ra toàn bộ thông tin của tblPr (bảng),
    bao gồm XML đầy đủ và các phần tử con, attr Python-level.
    """
    try:

        tblPr_xml = etree.tostring(tblPr, pretty_print=True, encoding='unicode')

        for child in tblPr.iterchildren():
            child_xml = etree.tostring(child, pretty_print=True, encoding='unicode')

    except Exception as e:
        logger.error(f"Error in inspect_tblPr_all_attrs: {str(e)}")


def inspect_all_cell_attributes(table):
    """
    In ra toàn bộ thông tin (XML) của từng cell trong bảng,
    đặc biệt là phần tcPr để xem có attr gì.
    """
    try:
        for row_idx, row in enumerate(table.rows):
            for col_idx, cell in enumerate(row.cells):
                cellPr = cell._element.find(qn('w:tcPr'))
                if cellPr is not None:
                    cellPr_xml = etree.tostring(cellPr, pretty_print=True, encoding='unicode')

    except Exception as e:
        logger.error(f"Error in inspect_all_cell_attributes: {str(e)}")

def extract_borders(tblBorders, is_table=True):
    """
    Trích xuất và chuyển đổi các thuộc tính đường viền từ tblBorders sang CSS.
    """
    try:
        borders_css = []
        if tblBorders is None:
            logger.debug("tblBorders is None. No borders to extract.")
            return ''
        
        border_types = {
            'top': 'border-top',
            'left': 'border-left',
            'bottom': 'border-bottom',
            'right': 'border-right',
            'insideH': 'border-top',
            'insideV': 'border-left'
        }

        for border_type, css_prop in border_types.items():
            border = tblBorders.find(qn(f'w:{border_type}'))
            if border is not None:
                val = border.get(qn('w:val'))
                sz = border.get(qn('w:sz'))
                color = border.get(qn('w:color'))
                space = border.get(qn('w:space'))

                logger.debug(f"Processing border_type={border_type}, val={val}, sz={sz}, color={color}, space={space}")

                # Kiểm tra "nil"/"none"/"hidden" => skip
                if val in ('nil','none','hidden') or (sz is not None and int(sz) == 0):
                    logger.debug(f"Skipping border: {border_type} => no border (val={val}, sz={sz})")
                    continue

                # Nếu có val, sz, color => convert
                if val and sz and color:
                    try:
                        if color.lower() == 'auto':
                            border_color = '#000000'
                            logger.debug(f"Border color='auto' => using black (#000000)")
                        else:
                            border_color = f'#{color}'

                        border_width_px = int(int(sz) / 20 * 1.333)  # sz là đơn vị thước, chuyển đổi sang px

                        css_border_style = {
                            'single': 'solid',
                            'double': 'double',
                            'dotted': 'dotted',
                            'dashed': 'dashed',
                            'dotDash': 'dashdot',
                            'dotDotDash': 'dashdot',
                            'nil': 'none',
                            'none': 'none',
                            'hidden': 'none'
                        }.get(val, 'solid')

                        border_css = f'{css_prop}: {border_width_px}px {css_border_style} {border_color};'
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
        logger.debug("Start extract_table_styles")
        styles_css = []
        if tblPr is None:
            logger.debug("tblPr is None => no table styles.")
            return ''

        # 1) Table alignment
        tblJc = tblPr.find(qn('w:jc'))
        if tblJc is not None:
            alignment = tblJc.get(qn('w:val'))
            if alignment:
                if alignment in ['left', 'start']:
                    styles_css.append('margin-left: 0; margin-right: auto;')
                elif alignment in ['right', 'end']:
                    styles_css.append('margin-left: auto; margin-right: 0;')
                elif alignment == 'center':
                    styles_css.append('margin-left: auto; margin-right: auto;')

        # 2) Background color
        tblShd = tblPr.find(qn('w:shd'))
        if tblShd is not None:
            fill = tblShd.get(qn('w:fill'))
            if fill:
                styles_css.append(f'background-color: #{fill};')

        # 3) Table Layout (fixed or autofit)
        tblLayout = tblPr.find(qn('w:tblLayout'))
        if tblLayout is not None:
            layout_type = tblLayout.get(qn('w:type'))
            if layout_type == 'fixed':
                styles_css.append('table-layout: fixed;')
            elif layout_type == 'autofit':
                styles_css.append('table-layout: auto;')
        else:
            # Nếu không có tblLayout, mặc định là autofit
            styles_css.append('table-layout: auto;')

        return ' '.join(styles_css)
    except Exception as e:
        logger.error(f"Error in extract_table_styles: {str(e)}")
        raise

def calculate_total_column_width(table):
    """
    Tính tổng độ rộng từ các cột trong bảng để thiết lập độ rộng của bảng.
    """
    try:
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
        logger.debug("Start apply_table_styles")
        if tblPr is not None:
            # Áp dụng các style khác như alignment, layout
            table_styles_css = extract_table_styles(tblPr)
            if table_styles_css:
                if 'style' in table_tag.attrs:
                    table_tag['style'] += ' ' + table_styles_css
                else:
                    table_tag['style'] = table_styles_css
            
            # Áp dụng đường viền cho bảng
            tblBorders = tblPr.find(qn('w:tblBorders'))
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
        cellPr = cell._element.find(qn('w:tcPr'))
        if cellPr is not None:
            # Áp dụng đường viền cho cell
            tcBorders = cellPr.find(qn('w:tcBorders'))
            if tcBorders is not None:
                cell_borders_css = extract_borders(tcBorders, is_table=False)
                if cell_borders_css:
                    if 'style' in td_tag.attrs:
                        td_tag['style'] += ' ' + cell_borders_css
                    else:
                        td_tag['style'] = cell_borders_css
            
            # Áp dụng background color cho cell
            tblShd = cellPr.find(qn('w:shd'))
            if tblShd is not None:
                fill = tblShd.get(qn('w:fill'))
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
        tblPr = table._element.find(qn('w:tblPr'))
        style = ''
        
        if tblPr is not None:
            tblW = tblPr.find(qn('w:tblW'))
            if tblW is not None:
                w_val = tblW.get(qn('w:w'))
                w_type = tblW.get(qn('w:type'))
                logger.debug(f"Table width: val={w_val}, type={w_type}")
                if w_type == 'pct' and w_val:
                    pct_value = int(w_val) / 50  # "5000" => 100%
                    style += f'width: {pct_value}%;'
                elif w_type == 'dxa' and w_val:
                    twips_val = int(w_val)
                    px_value = twips_to_pixels(twips_val)  # Chuyển đổi từ twips sang pixels
                    style += f'width: {px_value}px;'
                elif w_type == 'auto':
                    style += 'width: auto;'
                elif w_type == 'nil':
                    style += 'width: auto;'
            else:
                logger.debug("tblW is None. Setting width to auto.")
                style += 'width: auto;'
        else:
            logger.debug("tblPr is None. Setting width to auto.")
            style += 'width: auto;'
        
        return style
    except Exception as e:
        logger.error(f"Error in convert_table_width: {str(e)}")
        raise
