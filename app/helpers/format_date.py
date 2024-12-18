from datetime import datetime

def format_birthdate(birthdate_str: str) -> str:
    """
    Chuyển đổi ngày sinh từ định dạng ddmmyyyy thành dd/mm/yyyy.
    """
    try:
        # Chuyển đổi chuỗi sang đối tượng datetime
        date_obj = datetime.strptime(birthdate_str, "%d%m%Y")
        # Định dạng lại theo dd/mm/yyyy
        formatted_date = date_obj.strftime("%d/%m/%Y")
        return formatted_date
    except ValueError:
        raise ValueError(f"Invalid date format: {birthdate_str}")
