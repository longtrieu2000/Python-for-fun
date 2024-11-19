# -*- coding: utf-8 -*-

import time
import re
from prometheus_client import start_http_server, Counter, Gauge

# Định nghĩa các metrics với label "source" để phân biệt giữa các file log
log_request_count_total = Counter('log_request_count_total', 'Total number of requests', ['method', 'path', 'status_code', 'source'])
status_2xx_count = Gauge('status_2xx_count', 'Total count of 2xx status codes', ['source'])
status_4xx_count = Gauge('status_4xx_count', 'Total count of 4xx status codes', ['source'])
status_5xx_count = Gauge('status_5xx_count', 'Total count of 5xx status codes', ['source'])

# Biểu thức chính quy để phân tích log
log_regex = re.compile(r'^(?P<remote>[^ ]*) (?P<host>[^ ]*) (?P<user>[^ ]*) \[(?P<time>[^\]]*)\] "(?P<method>\w+)(?:\s+(?P<path>[^\"]*?)(?:\s+\S*)?)?" (?P<status_code>[^ ]*) (?P<size>[^ ]*)(?:\s"(?P<referer>[^\"]*)") "(?P<agent>[^\"]*)"')

logee = "api"

# Hàm xử lý log mới
def process_new_logs(log_file, source_label):
    total_2xx = 0
    total_4xx = 0
    total_5xx = 0

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
            size = match.group('size')

            # Xử lý trường hợp `size` không hợp lệ
            try:
                size = int(size)
            except ValueError:
                size = 0

            # Tính tổng các trạng thái
            if status_code.startswith('2') and path is not None and logee in path:
                total_2xx += 1
            elif status_code.startswith('4') and path is not None and logee in path:
                total_4xx += 1
                log_request_count_total.labels(method=method, path=path, status_code=status_code, source=source_label).inc()  # Xuất metric 4xx
            elif status_code.startswith('5') and path is not None and logee in path:
                total_5xx += 1
                log_request_count_total.labels(method=method, path=path, status_code=status_code, source=source_label).inc()  # Xuất metric 5xx

        # Cập nhật các metrics tổng
        status_2xx_count.labels(source=source_label).set(total_2xx)
        status_4xx_count.labels(source=source_label).set(total_4xx)
        status_5xx_count.labels(source=source_label).set(total_5xx)

# Chạy server Prometheus và bắt đầu đọc log
if __name__ == '__main__':
    start_http_server(8021)  # Khởi động server Prometheus tại port 8020

    # Tạo các thread để xử lý từng file log riêng biệt
    from threading import Thread

    # File log 1
    log_file_path_1 = '/home/test/mysafe.vietteltelcybersecurity.com.access.log.1'
    log_file_1 = open(log_file_path_1, 'r')
    thread_1 = Thread(target=process_new_logs, args=(log_file_1, "api_1"))
    thread_1.daemon = True
    thread_1.start()

    # File log 2
    log_file_path_2 = '/home/test/mysafe.vietteltelcybersecurity.com.access.log.2'
    log_file_2 = open(log_file_path_2, 'r')
    thread_2 = Thread(target=process_new_logs, args=(log_file_2, "api_2"))
    thread_2.daemon = True
    thread_2.start()

    # Giữ chương trình chạy
    while True:
        time.sleep(1)
