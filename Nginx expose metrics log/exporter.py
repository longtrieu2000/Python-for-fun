import time
import re
from prometheus_client import start_http_server, Counter, Histogram

# Định nghĩa các metrics
log_request_count = Counter('log_request_count', 'Number of requests', ['method', 'status_code', 'path'])
log_request_size = Histogram('log_request_size', 'Size of requests', ['method', 'path'])

# Biểu thức chính quy để phân tích log
log_regex = re.compile(r'^(?P<remote>[^ ]*) (?P<host>[^ ]*) (?P<user>[^ ]*) \[(?P<time>[^\]]*)\] "(?P<method>\w+)(?:\s+(?P<path>[^\"]*?)(?:\s+\S*)?)?" (?P<status_code>[^ ]*) (?P<size>[^ ]*)(?:\s"(?P<referer>[^\"]*)") "(?P<agent>[^\"]*)"')

# Hàm xử lý log mới
def process_new_logs(log_file):
    log_file.seek(0, 2)  # Di chuyển đến cuối file
    while True:
        line = log_file.readline()
        if not line:
            time.sleep(0.1)  # Chờ một chút nếu không có log mới
            continue

        match = log_regex.match(line)
        if match:
            method = match.group('method')
            status_code = match.group('status_code')
            path = match.group('path')
            size = int(match.group('size'))

            # Cập nhật metrics
            log_request_count.labels(method=method, status_code=status_code, path=path).inc()
            log_request_size.labels(method=method, path=path).observe(size)

# Chạy server Prometheus và bắt đầu đọc log
if __name__ == '__main__':
    start_http_server(8000)  # Khởi động server Prometheus tại port 8000
    with open('/path/to/your/logfile.log', 'r') as log_file:
        process_new_logs(log_file)
