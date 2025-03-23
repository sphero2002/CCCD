import json

class JsonConverterService:
    def create_input_field_html(self, field):
        """
        Hàm chuyển đổi 1 field (dict) thành HTML input theo kiểu field.
        """
        html = '<div class="form-group">\n'
        html += f'  <label for="{field["id"]}">{field["label"]}</label>\n'
        field_type = field.get("type", "text-input")
        
        if field_type == "text-input":
            html += f'  <input type="text" id="{field["id"]}" name="{field["id"]}" value="{field["value"]}" />\n'
        
        elif field_type == "date-picker":
            html += f'  <input type="date" id="{field["id"]}" name="{field["id"]}" value="{field["value"]}" />\n'
        
        elif field_type == "radio-box":
            # Nếu có options, tạo các input radio
            if "options" in field and field["options"]:
                html += '  <div class="option-group">\n'
                for option in field["options"]:
                    option_id = f'{field["id"]}-{option}'
                    html += f'    <input type="radio" id="{option_id}" name="{field["id"]}" value="{option}" />\n'
                    html += f'    <label for="{option_id}">{option}</label>\n'
                html += '  </div>\n'
        
        elif field_type == "check-box":
            # Nếu có options, tạo các input checkbox
            if "options" in field and field["options"]:
                html += '  <div class="option-group">\n'
                for option in field["options"]:
                    option_id = f'{field["id"]}-{option}'
                    html += f'    <input type="checkbox" id="{option_id}" name="{field["id"]}" value="{option}" />\n'
                    html += f'    <label for="{option_id}">{option}</label>\n'
                html += '  </div>\n'
        
        elif field_type == "select-box":
            html += f'  <select id="{field["id"]}" name="{field["id"]}">\n'
            if "options" in field and field["options"]:
                for option in field["options"]:
                    html += f'    <option value="{option}">{option}</option>\n'
            html += '  </select>\n'
        
        elif field_type == "table":
            html += '  <table>\n'
            if "fields" in field and field["fields"]:
                for subfield in field["fields"]:
                    html += '    <tr>\n'
                    html += f'      <td>{subfield["label"]}</td>\n'
                    html += f'      <td><input type="text" id="{subfield["id"]}" name="{subfield["id"]}" value="{subfield["value"]}" /></td>\n'
                    html += '    </tr>\n'
            html += '  </table>\n'
        
        else:
            # Mặc định là text-input nếu không xác định type
            html += f'  <input type="text" id="{field["id"]}" name="{field["id"]}" value="{field["value"]}" />\n'
        
        html += '</div>\n'
        return html

    def convert_json_to_html(self, title, json_content):
        """
        Hàm nhận đầu vào là chuỗi JSON theo cấu trúc:
        [
            [ { field1 }, { field2 }, ... ],
            [ { field3 }, { field4 }, ... ],
            ...
        ]
        và trả về chuỗi HTML tương ứng.
        """
        try:
            data = json.loads(json_content)
        except json.JSONDecodeError as e:
            return f"JSON decode error: {e}"

        html_output = ""
        # Giả sử JSON là mảng các nhóm (mỗi nhóm là list các field)
        for group in data:
            for field in group:
                html_output += self.create_input_field_html(field)
        html_full = self.return_full_html(title, html_output)
        return html_full

    def return_full_html(self, title, html_result):
        full_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
    .form-group {{
      margin-bottom: 1rem;
    }}
    .form-group label {{
      display: block;
      margin-bottom: 0.3rem;
      font-weight: bold;
    }}
    .option-group {{
      margin-left: 1rem;
    }}
    table {{
      border-collapse: collapse;
      margin-top: 0.5rem;
    }}
    table, th, td {{
      border: 1px solid #ccc;
      padding: 0.3rem;
    }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  {html_result}
</body>
</html>
"""
        return full_html


# if __name__ == "__main__":
#     json_content = '''
#     [
#         [
#             {
#                 "id": "61005dd2-c275-4983-bb22-9c6fd798bfe2",
#                 "value": "",
#                 "label": "...",
#                 "type": "text-input"
#             },
#             {
#                 "id": "12b4f997-ce99-4a0e-9ab2-c24b808c7b73",
#                 "value": "",
#                 "label": "Ngày",
#                 "type": "text-input"
#             }
#         ]
#     ]
#     '''
#     title = "My Form"
#     converter = JsonConverterService()
#     html_result = converter.convert_json_to_html(title, json_content)
#     print(html_result)
