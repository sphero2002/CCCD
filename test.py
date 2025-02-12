from bs4 import BeautifulSoup

# Mẫu HTML hoàn chỉnh để bọc nội dung mỗi chunk
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; }}
    h1, h2, h3, h4, h5, h6 {{ color: #2e6c80; }}
    table, th, td {{ padding: 20px; text-align: left; }}
    img {{ max-width: 100%; height: auto; }}
    ul, ol {{ margin: 0; padding-left: 40px; }}
    td {{ vertical-align: top; }}
    p {{ margin: 0 0 1em 0; }}
  </style>
</head>
<body style="margin: 75px 75px 75px 113px;">
  {content}
</body>
</html>
"""

def split_body_into_chunks(html, max_length=3000):
    """
    Chia nội dung trong thẻ body của HTML thành các chunk không vượt quá max_length ký tự.
    Nếu một phần tử đơn lẻ vượt quá max_length thì sẽ được chia nhỏ.
    """
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.body
    if body is None:
        raise ValueError("Không tìm thấy thẻ <body> trong HTML.")
    
    # Lấy danh sách các phần tử con trực tiếp của body
    children = list(body.children)
    chunks = []
    current_chunk = ""
    
    for child in children:
        # Chuyển đổi phần tử sang chuỗi HTML
        child_str = str(child)
        # Nếu thêm child này sẽ vượt quá max_length:
        if len(current_chunk) + len(child_str) > max_length:
            # Nếu current_chunk không rỗng, lưu chunk hiện tại lại
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            
            # Nếu child_str đơn lẻ vượt quá max_length, cần tách nó thành các phần nhỏ hơn.
            if len(child_str) > max_length:
                for i in range(0, len(child_str), max_length):
                    sub_chunk = child_str[i:i+max_length]
                    chunks.append(sub_chunk)
            else:
                # Nếu child_str không vượt quá max_length, gán nó cho current_chunk (khởi đầu chunk mới)
                current_chunk = child_str
        else:
            # Nếu không vượt quá, thêm child_str vào current_chunk
            current_chunk += child_str
    
    # Sau vòng lặp, nếu còn dư thì thêm vào danh sách chunks
    if current_chunk:
        chunks.append(current_chunk)
    
    # Bọc mỗi chunk vào mẫu HTML hoàn chỉnh
    final_pages = [HTML_TEMPLATE.format(content=chunk) for chunk in chunks]
    return final_pages

# Ví dụ sử dụng:
if __name__ == "__main__":
    # Giả sử html_content là chuỗi HTML của bạn
    html_content = """
    <head>
 <meta charset="utf-8"/>
 <style>
  body { font-family: Arial, sans-serif; margin: 20px; }
                h1, h2, h3, h4, h5, h6 { color: #2e6c80; }
                table, th, td { padding: 20px; text-align: left; }
                img { max-width: 100%; height: auto; }
                ul, ol { margin: 0; padding-left: 40px; }
                td {vertical-align: top;}
                p { margin: 0 0 1em 0; }
 </style>
</head>
<body style="margin: 67px 67px 67px 115px;">
 <p style="text-align: justify;">
  <span style="font-size: 13.0pt; font-weight: bold">
   Mẫu số 01. Phiếu khai báo nhân viên bức xạ
  </span>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
  </span>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   Độc lập - Tự do - Hạnh phúc
  </span>
 </p>
 <p style="text-align: center;">
  <br/>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   PHIẾU KHAI BÁO NHÂN VIÊN BỨC XẠ
  </span>
 </p>
 <p style="text-align: center;">
 </p>
 <p style="text-align: left;">
  <span>
   I. THÔNG TIN TỔ CHỨC, CÁ NHÂN KHAI BÁO
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   1. Tên tổ chức, cá nhân:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   2. Địa chỉ liên lạc:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   3. Số điện thoại:
   <span id="c7c2d003-aefc-4b31-9d29-cfea0b1d4bdb">
    ...
   </span>
   4. Số Fax:
   <span id="428866ca-7bac-44f5-bf6b-0643b33b39e2">
    ............
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   5. E-mail:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   II. NGƯỜI PHỤ TRÁCH AN TOÀN
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   1. Họ và tên:
   <span id="3ec04ccf-a1b2-4b61-a2f0-6ac558f1a47d">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   2. Ngày tháng năm sinh:
   <span id="8ba44741-1a40-4571-ada0-aa2c13fe570a">
    ...
   </span>
   3. Giới tính:
   <span id="2027154a-635d-4e10-9708-cee24c74cb5a">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   4. Số CMND/CCCD/Hộ chiếu:
   <span id="64ef3fd3-b45a-4a7c-bed7-660b13143976">
    ...
   </span>
   Ngày cấp:
   <span id="fa70ab28-c23c-483d-a340-850797655c93">
    ...
   </span>
   Cơ quan cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   5.  Chuyên ngành đào tạo:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   6. Phòng/khoa/phân xưởng đang làm việc:
   <span id="a827f2ab-98f0-42c4-b028-4ead39c2f018">
    ...............
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   Số điện thoại:
   <span id="37b1dd90-2003-4e19-bc19-5d845324f7d9">
    .........
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   7. Số quyết định bổ nhiệm phụ trách an toàn:
   <span id="fa9926b7-104c-47fb-8e81-47619a3918ef">
    ....
   </span>
   Ký ngày:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   8. Giấy chứng nhận đào tạo về an toàn bức xạ:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Số giấy chứng nhận:
   <span id="13f8f5fe-6c29-4f4e-a2a6-d4b600228472">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Ngày cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Tổ chức cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   9. Chứng chỉ nhân viên bức xạ:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Số Chứng chỉ:
   <span id="7b7adcee-ab77-46d2-bf29-39322db10e32">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Ngày cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Cơ quan cấp:
  </span>
 </p>
 <p style="text-align: left;">
 </p>
 <p style="text-align: left;">
  <br/>
  <span>
   III. NHÂN VIÊN BỨC XẠ KHÁC
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   Tổng số:
   <span id="9e4a4282-4ab5-422b-95c8-10cebda9d352">
    .........
   </span>
   nhân viên
  </span>
 </p>
 <table class="table-look-04A0" style="table-layout: auto; border-top: 0px solid #000000; border-left: 0px solid #000000; border-bottom: 0px solid #000000; border-right: 0px solid #000000; border-top: 0px solid #000000; border-left: 0px solid #000000; width: 100%;">
  <tbody>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       TT
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Họ và tên
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Năm sinh
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Giới tính
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chứng nhận đào tạo an toàn
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       bức xạ
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chứng chỉ
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       nhân viên
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       bức xạ
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chuyên ngành đào tạo
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Công việc
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       đảm nhiệm
      </span>
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       1
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Số chứng nhận:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Ngày cấp:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Tổ chức cấp :
      </span>
     </p>
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Số chứng chỉ:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Ngày cấp:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Cơ quan cấp
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       2
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       3
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
  </tbody>
 </table>
 <p style="text-align: left;">
 </p>
 <p style="text-align: right;">
  <span style="font-style: italic">
   <span id="8cbbbccc-3aa7-4818-8c94-28dc373ad72f" style="font-style: italic">
    ....
   </span>
   , ngày
   <span id="df707ebc-a36c-4338-a496-f5f1c03c2484" style="font-style: italic">
    .....
   </span>
   tháng
   <span id="6ae4e2ab-58fc-4614-8730-c6ecb195c4b9" style="font-style: italic">
    ....
   </span>
   năm
   <span id="f7d33acf-6135-4ba0-b3c2-973b885cfd91" style="font-style: italic">
    ....
   </span>
  </span>
 </p>
 <table class="table-look-04A0" style="table-layout: auto; width: 100%;">
  <tbody>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span>
       NGƯỜI LẬP PHIẾU
      </span>
     </p>
     <p style="text-align: center;">
      <span style="font-size: 11.0pt; font-style: italic">
       (Ký, ghi rõ họ tên)
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span>
       NGƯỜI ĐỨNG ĐẦU TỔ CHỨC/
      </span>
     </p>
     <p style="text-align: center;">
      <span>
       CÁ  NHÂN KHAI BÁO
      </span>
     </p>
     <p style="text-align: center;">
      <span style="font-size: 11.0pt; font-style: italic">
       (Ký, ghi rõ họ tên và đóng dấu)
      </span>
     </p>
    </td>
   </tr>
  </tbody>
 </table>
 <p style="text-align: left;">
  <br/>
 </p>
 <p style="text-align: left;">
 </p>
 <p style="text-align: left;">
 </p>
 <p style="text-align: left;">
 </p>
 <p style="text-align: justify;">
  <span style="font-size: 13.0pt; font-weight: bold">
   Mẫu số 01. Phiếu khai báo nhân viên bức xạ
  </span>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
  </span>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   Độc lập - Tự do - Hạnh phúc
  </span>
 </p>
 <p style="text-align: center;">
  <br/>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   PHIẾU KHAI BÁO NHÂN VIÊN BỨC XẠ
  </span>
 </p>
 <p style="text-align: center;">
 </p>
 <p style="text-align: left;">
  <span>
   I. THÔNG TIN TỔ CHỨC, CÁ NHÂN KHAI BÁO
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   1. Tên tổ chức, cá nhân:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   2. Địa chỉ liên lạc:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   3. Số điện thoại:
   <span id="f2c2500a-3644-4870-b0f8-5d11f9f7ca67">
    ...
   </span>
   4. Số Fax:
   <span id="5d17fdaa-921d-4f19-95f6-95f2f654e7b9">
    ............
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   5. E-mail:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   II. NGƯỜI PHỤ TRÁCH AN TOÀN
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   1. Họ và tên:
   <span id="3e230a8e-61fb-40bb-845d-b4b4962c7d85">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   2. Ngày tháng năm sinh:
   <span id="4eb27318-f27a-496b-a140-94218945c25a">
    ...
   </span>
   3. Giới tính:
   <span id="bf5cb9f8-7dc7-4006-97dc-a303173f280a">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   4. Số CMND/CCCD/Hộ chiếu:
   <span id="a85b5bb1-e1c6-46a5-b1c7-de6c9affc78c">
    ...
   </span>
   Ngày cấp:
   <span id="82cdfa88-5d67-4be7-b919-3f56e6ef8c9a">
    ...
   </span>
   Cơ quan cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   5.  Chuyên ngành đào tạo:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   6. Phòng/khoa/phân xưởng đang làm việc:
   <span id="7c5e10a0-20b2-4875-aad2-69910b854512">
    ...............
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   Số điện thoại:
   <span id="aca0b63e-ab38-45c5-8d98-393df8548362">
    .........
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   7. Số quyết định bổ nhiệm phụ trách an toàn:
   <span id="9b46725d-fa54-4ad2-aa5e-272e369562dc">
    ....
   </span>
   Ký ngày:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   8. Giấy chứng nhận đào tạo về an toàn bức xạ:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Số giấy chứng nhận:
   <span id="d7df8a2a-6851-45a4-b672-acf1bb0c082d">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Ngày cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Tổ chức cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   9. Chứng chỉ nhân viên bức xạ:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Số Chứng chỉ:
   <span id="8525139b-d768-4ac1-be76-30ffa7e6c7f8">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Ngày cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Cơ quan cấp:
  </span>
 </p>
 <p style="text-align: left;">
 </p>
 <p style="text-align: left;">
  <br/>
  <span>
   III. NHÂN VIÊN BỨC XẠ KHÁC
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   Tổng số:
   <span id="efd20f67-24fb-4271-8cf6-4406d5f31143">
    .........
   </span>
   nhân viên
  </span>
 </p>
 <table class="table-look-04A0" style="table-layout: auto; border-top: 0px solid #000000; border-left: 0px solid #000000; border-bottom: 0px solid #000000; border-right: 0px solid #000000; border-top: 0px solid #000000; border-left: 0px solid #000000; width: 100%;">
  <tbody>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       TT
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Họ và tên
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Năm sinh
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Giới tính
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chứng nhận đào tạo an toàn
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       bức xạ
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chứng chỉ
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       nhân viên
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       bức xạ
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chuyên ngành đào tạo
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Công việc
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       đảm nhiệm
      </span>
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       1
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Số chứng nhận:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Ngày cấp:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Tổ chức cấp :
      </span>
     </p>
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Số chứng chỉ:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Ngày cấp:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Cơ quan cấp
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       2
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       3
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
  </tbody>
 </table>
 <p style="text-align: left;">
 </p>
 <p style="text-align: right;">
  <span style="font-style: italic">
   <span id="2afe9c03-623a-4e2e-a4a9-01ecb76e650f" style="font-style: italic">
    ....
   </span>
   , ngày
   <span id="26efe7ef-c7a4-4e3a-8239-80ef543357c0" style="font-style: italic">
    .....
   </span>
   tháng
   <span id="10faa155-f3ab-44e0-9997-8a53f3536473" style="font-style: italic">
    ....
   </span>
   năm
   <span id="e5bf100d-c06a-4f9e-81e4-f9552904b729" style="font-style: italic">
    ....
   </span>
  </span>
 </p>
 <table class="table-look-04A0" style="table-layout: auto; width: 100%;">
  <tbody>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span>
       NGƯỜI LẬP PHIẾU
      </span>
     </p>
     <p style="text-align: center;">
      <span style="font-size: 11.0pt; font-style: italic">
       (Ký, ghi rõ họ tên)
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span>
       NGƯỜI ĐỨNG ĐẦU TỔ CHỨC/
      </span>
     </p>
     <p style="text-align: center;">
      <span>
       CÁ  NHÂN KHAI BÁO
      </span>
     </p>
     <p style="text-align: center;">
      <span style="font-size: 11.0pt; font-style: italic">
       (Ký, ghi rõ họ tên và đóng dấu)
      </span>
     </p>
    </td>
   </tr>
  </tbody>
 </table>
 <p style="text-align: left;">
  <br/>
 </p>
 <p style="text-align: left;">
 </p>
 <p style="text-align: justify;">
  <span style="font-size: 13.0pt; font-weight: bold">
   Mẫu số 01. Phiếu khai báo nhân viên bức xạ
  </span>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
  </span>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   Độc lập - Tự do - Hạnh phúc
  </span>
 </p>
 <p style="text-align: center;">
  <br/>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   PHIẾU KHAI BÁO NHÂN VIÊN BỨC XẠ
  </span>
 </p>
 <p style="text-align: center;">
 </p>
 <p style="text-align: left;">
  <span>
   I. THÔNG TIN TỔ CHỨC, CÁ NHÂN KHAI BÁO
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   1. Tên tổ chức, cá nhân:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   2. Địa chỉ liên lạc:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   3. Số điện thoại:
   <span id="c1481589-12c0-462c-a291-1b3b377d7e76">
    ...
   </span>
   4. Số Fax:
   <span id="aea8b6ee-ba93-4f30-8112-eeaf83a8933c">
    ............
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   5. E-mail:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   II. NGƯỜI PHỤ TRÁCH AN TOÀN
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   1. Họ và tên:
   <span id="62221bb8-cc31-44db-81ec-fe4eceed7e65">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   2. Ngày tháng năm sinh:
   <span id="3d341d0a-b7f2-4e42-b07a-8233dffa01d2">
    ...
   </span>
   3. Giới tính:
   <span id="19bd4e29-0737-4196-894d-1a5d916d6663">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   4. Số CMND/CCCD/Hộ chiếu:
   <span id="5dc53a07-9d83-491e-83e6-e1f882589f29">
    ...
   </span>
   Ngày cấp:
   <span id="451cfb32-fbe5-4ed5-a63f-4f2d6c8f4082">
    ...
   </span>
   Cơ quan cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   5.  Chuyên ngành đào tạo:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   6. Phòng/khoa/phân xưởng đang làm việc:
   <span id="a0c81c7f-9c06-4add-a189-da45eca0581c">
    ...............
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   Số điện thoại:
   <span id="2c063a75-6aaf-46c8-a210-a9c30302d9c7">
    .........
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   7. Số quyết định bổ nhiệm phụ trách an toàn:
   <span id="8b6721fd-ebb8-42a9-8376-288e2d2eec90">
    ....
   </span>
   Ký ngày:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   8. Giấy chứng nhận đào tạo về an toàn bức xạ:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Số giấy chứng nhận:
   <span id="37584c69-abff-4233-a402-fe00152ac9f5">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Ngày cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Tổ chức cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   9. Chứng chỉ nhân viên bức xạ:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Số Chứng chỉ:
   <span id="a9b1d69d-0387-4483-81f8-625ead0ecc0a">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Ngày cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Cơ quan cấp:
  </span>
 </p>
 <p style="text-align: left;">
 </p>
 <p style="text-align: left;">
  <br/>
  <span>
   III. NHÂN VIÊN BỨC XẠ KHÁC
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   Tổng số:
   <span id="f6969f9a-f54c-4c25-904f-434e4803357b">
    .........
   </span>
   nhân viên
  </span>
 </p>
 <table class="table-look-04A0" style="table-layout: auto; border-top: 0px solid #000000; border-left: 0px solid #000000; border-bottom: 0px solid #000000; border-right: 0px solid #000000; border-top: 0px solid #000000; border-left: 0px solid #000000; width: 100%;">
  <tbody>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       TT
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Họ và tên
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Năm sinh
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Giới tính
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chứng nhận đào tạo an toàn
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       bức xạ
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chứng chỉ
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       nhân viên
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       bức xạ
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chuyên ngành đào tạo
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Công việc
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       đảm nhiệm
      </span>
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       1
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Số chứng nhận:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Ngày cấp:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Tổ chức cấp :
      </span>
     </p>
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Số chứng chỉ:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Ngày cấp:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Cơ quan cấp
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       2
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       3
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
  </tbody>
 </table>
 <p style="text-align: left;">
 </p>
 <p style="text-align: right;">
  <span style="font-style: italic">
   <span id="a1a5f951-e431-47f0-9a93-23ff93f49b05" style="font-style: italic">
    ....
   </span>
   , ngày
   <span id="0db5aed9-6757-424f-8a23-72a8f8d4ef3a" style="font-style: italic">
    .....
   </span>
   tháng
   <span id="35cb10c7-c370-413a-be1b-3b37cf5d13e1" style="font-style: italic">
    ....
   </span>
   năm
   <span id="6fdd12b0-cf74-48cf-848b-0dccb33060e2" style="font-style: italic">
    ....
   </span>
  </span>
 </p>
 <table class="table-look-04A0" style="table-layout: auto; width: 100%;">
  <tbody>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span>
       NGƯỜI LẬP PHIẾU
      </span>
     </p>
     <p style="text-align: center;">
      <span style="font-size: 11.0pt; font-style: italic">
       (Ký, ghi rõ họ tên)
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span>
       NGƯỜI ĐỨNG ĐẦU TỔ CHỨC/
      </span>
     </p>
     <p style="text-align: center;">
      <span>
       CÁ  NHÂN KHAI BÁO
      </span>
     </p>
     <p style="text-align: center;">
      <span style="font-size: 11.0pt; font-style: italic">
       (Ký, ghi rõ họ tên và đóng dấu)
      </span>
     </p>
    </td>
   </tr>
  </tbody>
 </table>
 <p style="text-align: left;">
  <br/>
 </p>
 <p style="text-align: left;">
 </p>
 <p style="text-align: justify;">
  <span style="font-size: 13.0pt; font-weight: bold">
   Mẫu số 01. Phiếu khai báo nhân viên bức xạ
  </span>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
  </span>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   Độc lập - Tự do - Hạnh phúc
  </span>
 </p>
 <p style="text-align: center;">
  <br/>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   PHIẾU KHAI BÁO NHÂN VIÊN BỨC XẠ
  </span>
 </p>
 <p style="text-align: center;">
 </p>
 <p style="text-align: left;">
  <span>
   I. THÔNG TIN TỔ CHỨC, CÁ NHÂN KHAI BÁO
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   1. Tên tổ chức, cá nhân:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   2. Địa chỉ liên lạc:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   3. Số điện thoại:
   <span id="375ba435-d3d4-4247-917a-502f8e53537a">
    ...
   </span>
   4. Số Fax:
   <span id="690a1e36-f6b7-46a7-bd47-85064a631d0c">
    ............
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   5. E-mail:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   II. NGƯỜI PHỤ TRÁCH AN TOÀN
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   1. Họ và tên:
   <span id="db494296-7054-4d9e-bf17-c4fea3b5f8f3">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   2. Ngày tháng năm sinh:
   <span id="dbcb7131-c2f5-4e1c-ba37-4e08609ce535">
    ...
   </span>
   3. Giới tính:
   <span id="250c32c1-5690-48bb-a6b1-d197bed3f74c">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   4. Số CMND/CCCD/Hộ chiếu:
   <span id="917f2b16-15a2-4e15-8b82-4194518e1c82">
    ...
   </span>
   Ngày cấp:
   <span id="bb4c1aa6-2ddf-452d-94fd-74262782a126">
    ...
   </span>
   Cơ quan cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   5.  Chuyên ngành đào tạo:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   6. Phòng/khoa/phân xưởng đang làm việc:
   <span id="b68210b9-8129-4122-9a70-b32781de90d9">
    ...............
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   Số điện thoại:
   <span id="153a1f14-ad88-40e9-8ff0-acedfadd6905">
    .........
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   7. Số quyết định bổ nhiệm phụ trách an toàn:
   <span id="dfb6a803-0e68-4c18-9164-5ae76dd5ca71">
    ....
   </span>
   Ký ngày:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   8. Giấy chứng nhận đào tạo về an toàn bức xạ:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Số giấy chứng nhận:
   <span id="ed8dc5a6-40f6-4267-b9d3-ee91c1b73ae6">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Ngày cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Tổ chức cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   9. Chứng chỉ nhân viên bức xạ:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Số Chứng chỉ:
   <span id="022052ed-ae85-4b05-a0b7-e30761ef098e">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Ngày cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Cơ quan cấp:
  </span>
 </p>
 <p style="text-align: left;">
 </p>
 <p style="text-align: left;">
  <br/>
  <span>
   III. NHÂN VIÊN BỨC XẠ KHÁC
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   Tổng số:
   <span id="6d374d0c-7759-4212-baf5-a86cc899363b">
    .........
   </span>
   nhân viên
  </span>
 </p>
 <table class="table-look-04A0" style="table-layout: auto; border-top: 0px solid #000000; border-left: 0px solid #000000; border-bottom: 0px solid #000000; border-right: 0px solid #000000; border-top: 0px solid #000000; border-left: 0px solid #000000; width: 100%;">
  <tbody>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       TT
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Họ và tên
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Năm sinh
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Giới tính
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chứng nhận đào tạo an toàn
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       bức xạ
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chứng chỉ
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       nhân viên
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       bức xạ
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chuyên ngành đào tạo
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Công việc
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       đảm nhiệm
      </span>
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       1
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Số chứng nhận:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Ngày cấp:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Tổ chức cấp :
      </span>
     </p>
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Số chứng chỉ:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Ngày cấp:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Cơ quan cấp
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       2
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       3
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
  </tbody>
 </table>
 <p style="text-align: left;">
 </p>
 <p style="text-align: right;">
  <span style="font-style: italic">
   <span id="e25264a7-6a17-4f1d-b5db-de7e469d3f1f" style="font-style: italic">
    ....
   </span>
   , ngày
   <span id="659e8082-5f06-4db6-a736-ba94ad8ec468" style="font-style: italic">
    .....
   </span>
   tháng
   <span id="efb8a258-0c76-484d-ac88-a182827b2e5c" style="font-style: italic">
    ....
   </span>
   năm
   <span id="28d6b3f6-53e0-4fb4-b81a-5075d67b0a20" style="font-style: italic">
    ....
   </span>
  </span>
 </p>
 <table class="table-look-04A0" style="table-layout: auto; width: 100%;">
  <tbody>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span>
       NGƯỜI LẬP PHIẾU
      </span>
     </p>
     <p style="text-align: center;">
      <span style="font-size: 11.0pt; font-style: italic">
       (Ký, ghi rõ họ tên)
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span>
       NGƯỜI ĐỨNG ĐẦU TỔ CHỨC/
      </span>
     </p>
     <p style="text-align: center;">
      <span>
       CÁ  NHÂN KHAI BÁO
      </span>
     </p>
     <p style="text-align: center;">
      <span style="font-size: 11.0pt; font-style: italic">
       (Ký, ghi rõ họ tên và đóng dấu)
      </span>
     </p>
    </td>
   </tr>
  </tbody>
 </table>
 <p style="text-align: left;">
  <br/>
 </p>
 <p style="text-align: left;">
 </p>
 <p style="text-align: justify;">
  <span style="font-size: 13.0pt; font-weight: bold">
   Mẫu số 01. Phiếu khai báo nhân viên bức xạ
  </span>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
  </span>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   Độc lập - Tự do - Hạnh phúc
  </span>
 </p>
 <p style="text-align: center;">
  <br/>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   PHIẾU KHAI BÁO NHÂN VIÊN BỨC XẠ
  </span>
 </p>
 <p style="text-align: center;">
 </p>
 <p style="text-align: left;">
  <span>
   I. THÔNG TIN TỔ CHỨC, CÁ NHÂN KHAI BÁO
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   1. Tên tổ chức, cá nhân:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   2. Địa chỉ liên lạc:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   3. Số điện thoại:
   <span id="34a9d7e0-b983-4411-979b-b18c10d768ab">
    ...
   </span>
   4. Số Fax:
   <span id="8d08dea6-ff70-4704-bfcd-4dbeb7126953">
    ............
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   5. E-mail:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   II. NGƯỜI PHỤ TRÁCH AN TOÀN
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   1. Họ và tên:
   <span id="1711a677-7d7d-42f3-a4ba-a6ce8d97ea1e">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   2. Ngày tháng năm sinh:
   <span id="c1cbec73-7b41-4f75-ad39-d70c7b663f03">
    ...
   </span>
   3. Giới tính:
   <span id="fbabc028-f6e5-4bee-8dbd-9335828ca718">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   4. Số CMND/CCCD/Hộ chiếu:
   <span id="7e8f0f76-49d8-4ef0-bf38-c8fa96376790">
    ...
   </span>
   Ngày cấp:
   <span id="02973725-20c7-4716-a94f-67b9c659d00f">
    ...
   </span>
   Cơ quan cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   5.  Chuyên ngành đào tạo:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   6. Phòng/khoa/phân xưởng đang làm việc:
   <span id="c0f7f856-e2c4-4262-bdd3-46c120158709">
    ...............
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   Số điện thoại:
   <span id="4568a08c-9a2c-4f97-a6fe-2fa4be21794a">
    .........
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   7. Số quyết định bổ nhiệm phụ trách an toàn:
   <span id="d81ff030-252f-4618-835a-176f67e2da1d">
    ....
   </span>
   Ký ngày:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   8. Giấy chứng nhận đào tạo về an toàn bức xạ:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Số giấy chứng nhận:
   <span id="a0136e58-ee13-4ba4-b69c-e5e9a4cc440f">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Ngày cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Tổ chức cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   9. Chứng chỉ nhân viên bức xạ:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Số Chứng chỉ:
   <span id="9731f69e-d689-4746-b0c1-33e61fca581e">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Ngày cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Cơ quan cấp:
  </span>
 </p>
 <p style="text-align: left;">
 </p>
 <p style="text-align: left;">
  <br/>
  <span>
   III. NHÂN VIÊN BỨC XẠ KHÁC
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   Tổng số:
   <span id="dad8bde4-3ca7-4d6d-b1c7-2974d78b01c9">
    .........
   </span>
   nhân viên
  </span>
 </p>
 <table class="table-look-04A0" style="table-layout: auto; border-top: 0px solid #000000; border-left: 0px solid #000000; border-bottom: 0px solid #000000; border-right: 0px solid #000000; border-top: 0px solid #000000; border-left: 0px solid #000000; width: 100%;">
  <tbody>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       TT
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Họ và tên
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Năm sinh
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Giới tính
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chứng nhận đào tạo an toàn
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       bức xạ
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chứng chỉ
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       nhân viên
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       bức xạ
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chuyên ngành đào tạo
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Công việc
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       đảm nhiệm
      </span>
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       1
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Số chứng nhận:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Ngày cấp:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Tổ chức cấp :
      </span>
     </p>
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Số chứng chỉ:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Ngày cấp:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Cơ quan cấp
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       2
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       3
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
  </tbody>
 </table>
 <p style="text-align: left;">
 </p>
 <p style="text-align: right;">
  <span style="font-style: italic">
   <span id="65d403ec-53f0-451c-92b0-758749d0ecda" style="font-style: italic">
    ....
   </span>
   , ngày
   <span id="e97269cd-991a-4d52-8afe-3319861e6127" style="font-style: italic">
    .....
   </span>
   tháng
   <span id="bc5283fa-3531-416f-8aa9-985e8d44be32" style="font-style: italic">
    ....
   </span>
   năm
   <span id="78b9530b-4923-4d17-b558-04e5859c8a4f" style="font-style: italic">
    ....
   </span>
  </span>
 </p>
 <table class="table-look-04A0" style="table-layout: auto; width: 100%;">
  <tbody>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span>
       NGƯỜI LẬP PHIẾU
      </span>
     </p>
     <p style="text-align: center;">
      <span style="font-size: 11.0pt; font-style: italic">
       (Ký, ghi rõ họ tên)
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span>
       NGƯỜI ĐỨNG ĐẦU TỔ CHỨC/
      </span>
     </p>
     <p style="text-align: center;">
      <span>
       CÁ  NHÂN KHAI BÁO
      </span>
     </p>
     <p style="text-align: center;">
      <span style="font-size: 11.0pt; font-style: italic">
       (Ký, ghi rõ họ tên và đóng dấu)
      </span>
     </p>
    </td>
   </tr>
  </tbody>
 </table>
 <p style="text-align: left;">
  <br/>
 </p>
 <p style="text-align: left;">
 </p>
 <p style="text-align: justify;">
  <span style="font-size: 13.0pt; font-weight: bold">
   Mẫu số 01. Phiếu khai báo nhân viên bức xạ
  </span>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
  </span>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   Độc lập - Tự do - Hạnh phúc
  </span>
 </p>
 <p style="text-align: center;">
  <br/>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   PHIẾU KHAI BÁO NHÂN VIÊN BỨC XẠ
  </span>
 </p>
 <p style="text-align: center;">
 </p>
 <p style="text-align: left;">
  <span>
   I. THÔNG TIN TỔ CHỨC, CÁ NHÂN KHAI BÁO
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   1. Tên tổ chức, cá nhân:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   2. Địa chỉ liên lạc:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   3. Số điện thoại:
   <span id="707f8135-5554-4341-910a-43d6c7b03ce5">
    ...
   </span>
   4. Số Fax:
   <span id="317f1a87-ae22-4ada-b658-a9509124c6ab">
    ............
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   5. E-mail:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   II. NGƯỜI PHỤ TRÁCH AN TOÀN
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   1. Họ và tên:
   <span id="9db0162d-0123-48d0-89fb-8b4f66053877">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   2. Ngày tháng năm sinh:
   <span id="b28527ec-7204-4f04-8c1c-b9804835e7f9">
    ...
   </span>
   3. Giới tính:
   <span id="76585b8a-0964-4008-bc9a-c8a044341f49">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   4. Số CMND/CCCD/Hộ chiếu:
   <span id="03805743-0aa2-4a28-ad5b-a5af87018f4f">
    ...
   </span>
   Ngày cấp:
   <span id="8f525e5c-a828-49ac-b518-c88f955da8d7">
    ...
   </span>
   Cơ quan cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   5.  Chuyên ngành đào tạo:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   6. Phòng/khoa/phân xưởng đang làm việc:
   <span id="b5baac03-ef04-4d88-96ba-ed28b087631d">
    ...............
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   Số điện thoại:
   <span id="d2b972e2-d790-48aa-b525-0248844780dd">
    .........
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   7. Số quyết định bổ nhiệm phụ trách an toàn:
   <span id="bac42266-3f08-4dcd-8443-170cced4c848">
    ....
   </span>
   Ký ngày:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   8. Giấy chứng nhận đào tạo về an toàn bức xạ:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Số giấy chứng nhận:
   <span id="e8d36a5f-f16d-4122-b968-41e56917be83">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Ngày cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Tổ chức cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   9. Chứng chỉ nhân viên bức xạ:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Số Chứng chỉ:
   <span id="ab230b39-9672-46af-81d1-d8d3e1041ee0">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Ngày cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Cơ quan cấp:
  </span>
 </p>
 <p style="text-align: left;">
 </p>
 <p style="text-align: left;">
  <br/>
  <span>
   III. NHÂN VIÊN BỨC XẠ KHÁC
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   Tổng số:
   <span id="2bdeb9b0-502e-410f-9752-f818e2a35b17">
    .........
   </span>
   nhân viên
  </span>
 </p>
 <table class="table-look-04A0" style="table-layout: auto; border-top: 0px solid #000000; border-left: 0px solid #000000; border-bottom: 0px solid #000000; border-right: 0px solid #000000; border-top: 0px solid #000000; border-left: 0px solid #000000; width: 100%;">
  <tbody>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       TT
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Họ và tên
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Năm sinh
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Giới tính
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chứng nhận đào tạo an toàn
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       bức xạ
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chứng chỉ
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       nhân viên
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       bức xạ
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chuyên ngành đào tạo
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Công việc
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       đảm nhiệm
      </span>
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       1
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Số chứng nhận:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Ngày cấp:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Tổ chức cấp :
      </span>
     </p>
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Số chứng chỉ:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Ngày cấp:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Cơ quan cấp
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       2
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       3
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
  </tbody>
 </table>
 <p style="text-align: left;">
 </p>
 <p style="text-align: right;">
  <span style="font-style: italic">
   <span id="9f203c5e-e169-48f1-a0d1-cd432b47f960" style="font-style: italic">
    ....
   </span>
   , ngày
   <span id="552d03a3-6a69-4a5e-9556-a5bae336a781" style="font-style: italic">
    .....
   </span>
   tháng
   <span id="a69fe295-c4bf-41c7-a4f6-0db24b8ab61a" style="font-style: italic">
    ....
   </span>
   năm
   <span id="198f10d5-17ce-4009-a583-095af73212a1" style="font-style: italic">
    ....
   </span>
  </span>
 </p>
 <table class="table-look-04A0" style="table-layout: auto; width: 100%;">
  <tbody>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span>
       NGƯỜI LẬP PHIẾU
      </span>
     </p>
     <p style="text-align: center;">
      <span style="font-size: 11.0pt; font-style: italic">
       (Ký, ghi rõ họ tên)
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span>
       NGƯỜI ĐỨNG ĐẦU TỔ CHỨC/
      </span>
     </p>
     <p style="text-align: center;">
      <span>
       CÁ  NHÂN KHAI BÁO
      </span>
     </p>
     <p style="text-align: center;">
      <span style="font-size: 11.0pt; font-style: italic">
       (Ký, ghi rõ họ tên và đóng dấu)
      </span>
     </p>
    </td>
   </tr>
  </tbody>
 </table>
 <p style="text-align: left;">
  <br/>
 </p>
 <p style="text-align: left;">
 </p>
 <p style="text-align: justify;">
  <span style="font-size: 13.0pt; font-weight: bold">
   Mẫu số 01. Phiếu khai báo nhân viên bức xạ
  </span>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
  </span>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   Độc lập - Tự do - Hạnh phúc
  </span>
 </p>
 <p style="text-align: center;">
  <br/>
 </p>
 <p style="text-align: center;">
  <span style="font-size: 13.0pt; font-weight: bold">
   PHIẾU KHAI BÁO NHÂN VIÊN BỨC XẠ
  </span>
 </p>
 <p style="text-align: center;">
 </p>
 <p style="text-align: left;">
  <span>
   I. THÔNG TIN TỔ CHỨC, CÁ NHÂN KHAI BÁO
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   1. Tên tổ chức, cá nhân:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   2. Địa chỉ liên lạc:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   3. Số điện thoại:
   <span id="09399404-c8ca-43ff-9f17-3452966eb81e">
    ...
   </span>
   4. Số Fax:
   <span id="91c919f6-2f42-4d28-8e0e-a5dd8844662a">
    ............
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   5. E-mail:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   II. NGƯỜI PHỤ TRÁCH AN TOÀN
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   1. Họ và tên:
   <span id="e6a7277c-741b-4012-87ef-1bbb5419fbba">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   2. Ngày tháng năm sinh:
   <span id="7734ae36-ae5b-4150-adce-c0f291417d53">
    ...
   </span>
   3. Giới tính:
   <span id="ca34e320-410c-45a9-a5d9-5fd35f115081">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   4. Số CMND/CCCD/Hộ chiếu:
   <span id="1b1a2758-e4e0-4ac4-9722-6a4d09e82e23">
    ...
   </span>
   Ngày cấp:
   <span id="a820a98e-e889-4520-a33e-b1ecf9d8bd84">
    ...
   </span>
   Cơ quan cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   5.  Chuyên ngành đào tạo:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   6. Phòng/khoa/phân xưởng đang làm việc:
   <span id="a471974c-3561-4a48-8d52-ecac97471d14">
    ...............
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   Số điện thoại:
   <span id="e47c768b-8405-45e8-b6e3-8f2d07d6d4ce">
    .........
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   7. Số quyết định bổ nhiệm phụ trách an toàn:
   <span id="f87c72f0-b8fd-4d2c-83af-51225858d7a3">
    ....
   </span>
   Ký ngày:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   8. Giấy chứng nhận đào tạo về an toàn bức xạ:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Số giấy chứng nhận:
   <span id="8c008aa6-dcb1-477b-9aed-f15d90728569">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Ngày cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Tổ chức cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   9. Chứng chỉ nhân viên bức xạ:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Số Chứng chỉ:
   <span id="08d4c7a3-b0be-4946-9c36-f8178aa133f8">
    ...
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Ngày cấp:
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Cơ quan cấp:
  </span>
 </p>
 <p style="text-align: left;">
 </p>
 <p style="text-align: left;">
  <br/>
  <span>
   III. NHÂN VIÊN BỨC XẠ KHÁC
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   Tổng số:
   <span id="b7470e05-b308-4c29-bc0f-2973f38db0f6">
    .........
   </span>
   nhân viên
  </span>
 </p>
 <table class="table-look-04A0" style="table-layout: auto; border-top: 0px solid #000000; border-left: 0px solid #000000; border-bottom: 0px solid #000000; border-right: 0px solid #000000; border-top: 0px solid #000000; border-left: 0px solid #000000; width: 100%;">
  <tbody>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       TT
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Họ và tên
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Năm sinh
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Giới tính
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chứng nhận đào tạo an toàn
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       bức xạ
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chứng chỉ
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       nhân viên
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       bức xạ
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chuyên ngành đào tạo
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Công việc
      </span>
      <span style="font-size: 11.0pt">
      </span>
      <br/>
      <span style="font-size: 11.0pt">
       đảm nhiệm
      </span>
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       1
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Số chứng nhận:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Ngày cấp:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Tổ chức cấp :
      </span>
     </p>
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Số chứng chỉ:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Ngày cấp:
      </span>
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Cơ quan cấp
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       2
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       3
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: left;">
     </p>
    </td>
   </tr>
  </tbody>
 </table>
 <p style="text-align: left;">
 </p>
 <p style="text-align: right;">
  <span style="font-style: italic">
   <span id="020c850a-203a-4e56-860c-1dc1efa31a7b" style="font-style: italic">
    ....
   </span>
   , ngày
   <span id="4ce3b3fc-dfb3-4a68-90ac-45f49f771bac" style="font-style: italic">
    .....
   </span>
   tháng
   <span id="d119665b-ff66-40f8-b446-a032aef23ed8" style="font-style: italic">
    ....
   </span>
   năm
   <span id="5f7abaa8-429f-4040-bd3d-85e6ee70b1a1" style="font-style: italic">
    ....
   </span>
  </span>
 </p>
 <table class="table-look-04A0" style="table-layout: auto; width: 100%;">
  <tbody>
   <tr>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span>
       NGƯỜI LẬP PHIẾU
      </span>
     </p>
     <p style="text-align: center;">
      <span style="font-size: 11.0pt; font-style: italic">
       (Ký, ghi rõ họ tên)
      </span>
     </p>
    </td>
    <td style=" border: 1px solid black;">
     <p style="text-align: center;">
      <span>
       NGƯỜI ĐỨNG ĐẦU TỔ CHỨC/
      </span>
     </p>
     <p style="text-align: center;">
      <span>
       CÁ  NHÂN KHAI BÁO
      </span>
     </p>
     <p style="text-align: center;">
      <span style="font-size: 11.0pt; font-style: italic">
       (Ký, ghi rõ họ tên và đóng dấu)
      </span>
     </p>
    </td>
   </tr>
  </tbody>
 </table>
 <p style="text-align: left;">
  <br/>
 </p>
 <p style="text-align: left;">
 </p>
</body>
    """
    pages = split_body_into_chunks(html_content, max_length=50000)
    
    # Lưu mỗi trang HTML ra file riêng (ví dụ)
    for idx, page in enumerate(pages):
        filename = f"page_{idx+1}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(page)
        print(f"Đã lưu {filename}")
