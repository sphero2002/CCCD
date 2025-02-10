from bs4 import BeautifulSoup

def flatten_id_spans(html_str):
    """
    Hàm này nhận vào một chuỗi HTML và xử lý các thẻ <span> có thuộc tính id lồng nhau.
    Nếu một thẻ <span> có id chứa các thẻ <span> con cũng có id, 
    thì nội dung của các thẻ con sẽ được gộp lại thành nội dung của thẻ cha và 
    các thẻ con sẽ bị loại bỏ.
    """
    soup = BeautifulSoup(html_str, 'html.parser')
    
    # Duyệt qua tất cả các thẻ <span> có thuộc tính id
    for span in soup.find_all('span', id=True):
        # Tìm tất cả các thẻ <span> con (trong mọi cấp) có thuộc tính id
        descendant_spans = span.find_all('span', id=True)
        if descendant_spans:
            # Lấy nội dung (text) của các thẻ con, loại bỏ khoảng trắng thừa
            combined_text = ''.join([desc.get_text(strip=True) for desc in descendant_spans])
            # Xóa sạch nội dung con của thẻ cha
            span.clear()
            # Thêm nội dung đã gộp vào thẻ cha
            span.append(combined_text)
    
    return soup.prettify()

# Ví dụ sử dụng:
if __name__ == "__main__":
    html_input = """
    <head>
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
   1. Tên tổ chức, cá nhân: <span id="a1b2c3d4-e5f6-7890-1234-567890abcdef">...</span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   2. Địa chỉ liên lạc: <span id="f0e9d8c7-b6a5-4321-9876-543210fedcba">...</span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   3. Số điện thoại:
   <span id="4e3fed9f-914e-4dbe-b3c4-054590fafc8e">
    <span id="077166a3-3682-44df-86ad-ca67a6485492">...</span>
   </span>
   4. Số Fax:
   <span id="dc796ccd-3faa-4b74-94b0-fc326a43f382">
    <span id="32b0c84d-4e5a-45cb-b4a0-f75f766a4e1f">...</span>
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   5. E-mail: <span id="67543210-fedc-ba98-7654-3210fedcba98">...</span>
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
   <span id="c57857f0-7cad-42a1-a936-bf04ed16e72b">
    <span id="87bd51dd-ea82-40a6-bbb8-cbd1b3f82daf">...</span>
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   2. Ngày tháng năm sinh:
   <span id="5ce50288-46e8-4044-bcbf-eb37d379043c">
    <span id="f4e82f0c-56b9-4d0b-b2bd-1123dd876780">...</span>
   </span>
   3. Giới tính:
   <span id="ee979542-3ffb-4167-ab64-0f26b35a89b2">
    <span id="1de3efea-daea-46a0-a670-f3de38abfcc9">...</span>
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   4. Số CMND/CCCD/Hộ chiếu:
   <span id="7aa69fe1-ccdf-4bf1-b176-15567af217a5">
    <span id="ca3b2a07-6194-45dd-a328-fd616538e393">...</span>
   </span>
   Ngày cấp:
   <span id="f1f40a69-0b20-4c10-848d-15b4e170a528">
    <span id="3ec69ca7-46ca-4fe4-b92e-d838147376ee">...</span>
   </span>
   Cơ quan cấp: <span id="b9a7c8d6-f3e2-468a-9f1e-5c7d29e9c777">...</span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   5.  Chuyên ngành đào tạo: <span id="e8d7c6b5-a493-4821-8765-43210fedcba98">...</span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   6. Phòng/khoa/phân xưởng đang làm việc:
   <span id="019da9b8-0c13-405e-9289-5e832cd8a8b5">
    <span id="1de9aada-7921-49d4-ace8-7fba356d48e9">...</span>
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   Số điện thoại:
   <span id="839d0131-3f15-4782-8670-824ce28d0e60">
    <span id="dade34d7-2778-49e1-a5c7-65b6dd9a6dcb">...</span>
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   7. Số quyết định bổ nhiệm phụ trách an toàn:
   <span id="9e572e50-d6fb-472f-8c4b-b0ea0b1e8378">
    <span id="50f3b4bb-eea7-4de5-b6bd-0fdc3769ea2d">...</span>
   </span>
   Ký ngày: <span id="5278a1b9-34c5-418d-b765-a32f1d4e7c89">...</span>
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
   <span id="d1c67987-2740-4836-99de-83501e653918">
    <span id="d635777e-6dbf-4764-8e89-f7762ebc4f02">...</span>
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Ngày cấp: <span id="23e1f4d7-904b-4583-9a5d-350d78136a02">...</span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Tổ chức cấp: <span id="8a2c1d5e-f71c-49e8-b58d-268d0e5f0e44">...</span>
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
   <span id="84ef3a78-47f1-4f96-a538-46a5164ab68f">
    <span id="185fd30f-0b7b-42df-a1b8-3a7d8171f656">...</span>
   </span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Ngày cấp: <span id="1f2e3d4c-a7b8-4156-9c3d-e12f5a78b0c1">...</span>
  </span>
 </p>
 <p style="text-align: left;">
  <span>
   - Cơ quan cấp: <span id="76a9b2c8-3e45-471b-a987-6f1e23c750b4">...</span>
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
   <span id="68035e1d-fa0a-4602-85db-ae943ae9bbf0">
    <span id="fef6a373-e966-4510-89e5-99c6d4cbf43b">...</span>
   </span>
   nhân viên
  </span>
 </p>
 <table class="table-look-04A0" style="width: 100%; border-collapse: collapse; top-border: 0.5pt single #000000; left-border: 0.5pt single #000000; bottom-border: 0.5pt single #000000; right-border: 0.5pt single #000000; insideH-border: 0.5pt single #000000; insideV-border: 0.5pt single #000000;">
  <tbody>
   <tr>
    <td style="width: 5.17%; vertical-align: middle; border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       TT
      </span>
     </p>
    </td>
    <td style="width: 14.89%; vertical-align: middle; border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Họ và tên
      </span>
     </p>
    </td>
    <td style="width: 6.99%; vertical-align: middle; border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Năm sinh
      </span>
     </p>
    </td>
    <td style="width: 6.69%; vertical-align: middle; border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Giới tính
      </span>
     </p>
    </td>
    <td style="width: 18.24%; vertical-align: middle; border: 1px solid black;">
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
    <td style="width: 15.81%; vertical-align: middle; border: 1px solid black;">
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
    <td style="width: 9.73%; vertical-align: middle; border: 1px solid black;">
     <p style="text-align: center;">
      <span style="font-size: 11.0pt">
       Chuyên ngành đào tạo
      </span>
     </p>
    </td>
    <td style="width: 22.49%; vertical-align: middle; border: 1px solid black;">
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
    <td style="width: 5.17%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       1
      </span>
     </p>
    </td>
    <td style="width: 14.89%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="87654321-fedc-ba98-7654-3210fedcba98">...</span>
     </p>
    </td>
    <td style="width: 6.99%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="43210fed-cba9-8765-4321-0fedcba98765">...</span>
     </p>
    </td>
    <td style="width: 6.69%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="fedcba98-7654-3210-fedc-ba9876543210">...</span>
     </p>
    </td>
    <td style="width: 18.24%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Số chứng nhận: <span id="567890ab-cdef-1234-5678-90abcdef1234">...</span>
      </span>
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Ngày cấp: <span id="90abcdef-1234-5678-90ab-cdef12345678">...</span>
      </span>
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Tổ chức cấp : <span id="abcdef12-3456-7890-abcdef-1234567890ab">...</span>
      </span>
     </p>
    </td>
    <td style="width: 15.81%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Số chứng chỉ: <span id="12345678-90ab-cdef-1234-567890abcdef">...</span>
      </span>
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Ngày cấp: <span id="abcdef12-3456-7890-abcdef-1234567890ab">...</span>
      </span>
     </p>
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       Cơ quan cấp <span id="7890abcdef-1234-5678-90ab-cdef12345678">...</span>
      </span>
     </p>
    </td>
    <td style="width: 9.73%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="09876543-21fe-dcba-9876-543210fedcba">...</span>
     </p>
    </td>
    <td style="width: 22.49%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="dcba9876-5432-10fe-dcba-9876543210fe">...</span>
     </p>
    </td>
   </tr>
   <tr>
    <td style="width: 5.17%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       2
      </span>
     </p>
    </td>
    <td style="width: 14.89%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="1a2b3c4d-5e6f-7890-1234-567890abcdef">...</span>
     </p>
    </td>
    <td style="width: 6.99%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="6a7b8c9d-0e1f-2345-6789-0abcdef12345">...</span>
     </p>
    </td>
    <td style="width: 6.69%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="ba987654-3210-fedc-ba98-76543210fedc">...</span>
     </p>
    </td>
    <td style="width: 18.24%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="543210fe-dcba-9876-5432-10fedcba9876">...</span>
     </p>
    </td>
    <td style="width: 15.81%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="3210fedc-ba98-7654-3210-fedcba987654">...</span>
     </p>
    </td>
    <td style="width: 9.73%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="21fe4dc-ba98-7654-3210-fedcba98765">...</span>
     </p>
    </td>
    <td style="width: 22.49%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="fedcba98-7654-3210-fedc-ba987654321">...</span>
     </p>
    </td>
   </tr>
   <tr>
    <td style="width: 5.17%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span style="font-size: 11.0pt">
       3
      </span>
     </p>
    </td>
    <td style="width: 14.89%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="d5c4b3a2-9876-5432-10fe-dcba98765432">...</span>
     </p>
    </td>
    <td style="width: 6.99%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="e6f5d4c3-b1a0-9876-5432-10fedcba9876">...</span>
     </p>
    </td>
    <td style="width: 6.69%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="f7e6d5c4-a2b1-c3d4-e5f6-789012345678">...</span>
     </p>
    </td>
    <td style="width: 18.24%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="89012345-6789-0abc-def1-234567890123">...</span>
     </p>
    </td>
    <td style="width: 15.81%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="01234567-890a-bcde-f123-4567890abcdef">...</span>
     </p>
    </td>
    <td style="width: 9.73%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="13579bdf-2468-0ace-1357-9bdf24680ace">...</span>
     </p>
    </td>
    <td style="width: 22.49%; vertical-align: top; border: 1px solid black;">
     <p style="text-align: left;">
      <span id="24680ace-1357-9bdf-2468-0ace13579bdf">...</span>
     </p>
    </td>
   </tr>
  </tbody>
 </table>
 <p style="text-align: left;">
 </p>
 <p style="text-align: right;">
  <span style="font-style: italic">
   <span id="126a9823-37e8-4a13-aa42-0aabddd1bb1a" style="font-style: italic">
    <span id="03559675-bb5e-416e-a453-e582ebb8c38e">...</span>
   </span>
   , ngày
   <span id="9a69c464-092d-4472-8be9-e11b0004f4e5" style="font-style: italic">
    <span id="e94b1cdd-770c-464d-a2ab-787884f6a6b7">...</span>
   </span>
   tháng
   <span id="4cd39df2-2093-4d30-8797-e0f1fd511963" style="font-style: italic">
    <span id="82b043c5-90f7-447c-b32c-bc78408f44ce">...</span>
   </span>
   năm
   <span id="53867c5b-4ec9-43dc-913b-26675992ca28" style="font-style: italic">
    <span id="eeadc547-5cb3-4600-af93-0c8cafff1474">...</span>
   </span>
  </span>
 </p>
 <table class="table-look-04A0" style="width: 100%;">
  <tbody>
   <tr>
    <td style="width: 50.00%; vertical-align: top; border: 1px solid black;">
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
    <td style="width: 50.00%; vertical-align: top; border: 1px solid black;">
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
</body>
    """
    
    flattened_html = flatten_id_spans(html_input)
    print(flattened_html)
