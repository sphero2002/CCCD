import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Cấu hình Chrome Options và thêm logging preferences
options = Options()
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

# Nếu cần chạy ẩn (headless) thì có thể bỏ comment dòng dưới:
# options.add_argument("--headless")

# Khởi tạo ChromeDriver với options đã cấu hình
driver = webdriver.Chrome(options=options)

# Mở trang web cần truy cập
driver.get("https://tongyi.aliyun.com/")  # Thay URL này bằng trang bạn muốn tương tác

# Cho phép bạn tương tác thủ công (đăng nhập, điều hướng, ...)
input("Hãy tương tác với trang và nhấn Enter khi hoàn thành...")

# Sau khi tương tác xong, thu thập log network
logs = driver.get_log("performance")

# Phân tích log để tìm các fetch API calls (ví dụ, chứa '/api/' trong URL)
api_requests = []
for entry in logs:
    try:
        message = json.loads(entry["message"])["message"]
        if message.get("method") == "Network.requestWillBeSent":
            request = message.get("params", {}).get("request", {})
            url = request.get("url", "")
            if "/api/" in url:  # Lọc các URL chứa '/api/'
                api_requests.append(url)
    except Exception as e:
        print(f"Lỗi khi xử lý log: {e}")

# In ra các API endpoint đã bắt được
print("\nCác API endpoint fetch được:")
for api in api_requests:
    print(api)

# Lưu kết quả vào file JSON
with open("api_requests.json", "w", encoding="utf-8") as f:
    json.dump(api_requests, f, ensure_ascii=False, indent=4)
print("\nKết quả đã được lưu vào file 'api_requests.json'.")

# Đóng trình duyệt
driver.quit()
