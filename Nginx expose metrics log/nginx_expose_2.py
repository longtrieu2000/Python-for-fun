# -*- coding: utf-8 -*-
import time
import re
from datetime import datetime
from prometheus_client import start_http_server, Counter, Gauge
from threading import Thread

# Biểu thức chính quy để phân tích log
log_regex = re.compile(
    r'^(?P<remote>[^ ]*) (?P<host>[^ ]*) (?P<user>[^ ]*) \[(?P<timestamp>[^\]]*)\] "(?P<method>\w+)(?:\s+(?P<path>[^\"]*?)(?:\s+\S*)?)?" '
    r'(?P<status_code>\d+) (?P<size>\d+)(?:\s"(?P<referer>[^\"]*)") "(?P<agent>[^\"]*)" "(?P<forwarded_for>[^\"]*)" (?P<request_time>[0-9.]+) (?P<upstream_time>[0-9.]+)'
)

# Định nghĩa các metrics với label "source" để phân biệt giữa các file log
log_request_count_total = Counter(
    'log_request_count_total', 'Total number of requests', ['method', 'path', 'status_code', 'source']
)
status_2xx_count = Gauge('status_2xx_count', 'Total count of 2xx status codes', ['source'])
status_4xx_count = Gauge('status_4xx_count', 'Total count of 4xx status codes', ['source'])
status_5xx_count = Gauge('status_5xx_count', 'Total count of 5xx status codes', ['source'])
avg_request_time = Gauge('avg_request_time_seconds', 'Average request time by date and source', ['date', 'source'])
logee = "api"
slow_request_metric = Counter('slow_request_count', 'Requests with request_time > 5s', ['method', 'path', 'status_code', 'source'])
# Lưu dữ liệu thời gian request theo ngày cho từng file log
daily_request_times = {}

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
            # Lấy thông tin từ log
            timestamp = match.group('timestamp')
            method = match.group('method')
            path = match.group('path')
            status_code = match.group('status_code')
            request_time = float(match.group('request_time'))

            # Chuyển timestamp thành định dạng ngày
            #log_date = datetime.strptime(timestamp.split()[0], '%d/%b/%Y').strftime('%d/%b')
            log_datetime = datetime.strptime(timestamp, '%d/%b/%Y:%H:%M:%S %z')
            log_date = log_datetime.strftime('%d/%b')            # Lưu thời gian request theo ngày
            #daily_request_times[log_date] += 1
            key_request_time = log_date + "-request_time"
            #key_response_time = log_date + "-response_time"

            if daily_request_times.get(key_request_time) is None:
                daily_request_times[key_request_time] = [0,0]

            daily_request_times[key_request_time][0] += request_time
            daily_request_times[key_request_time][1] += 1
            sum_avg_request_time = daily_request_times[key_request_time][0] / daily_request_times[key_request_time][1]


            # Lưu thời gian request theo ngày
            #daily_request_times[source_label] = {}
            #if log_date not in daily_request_times[source_label]:
            #    daily_request_times[source_label][log_date] = []

            #daily_request_times[source_label][log_date].append(request_time)

            # Tính trung bình thời gian request và cập nhật metric
            #avg_time = (
            #    sum(daily_request_times[source_label][log_date])
             #   / len(daily_request_times[source_label][log_date])
            #)
            avg_request_time.labels(date=log_date, source=source_label).set(sum_avg_request_time)
            if request_time > 5.0:
                slow_request_metric.labels(
                    method=method, path=path, status_code=status_code, source=source_label
                ).inc()
            # Tính tổng các trạng thái
            if status_code.startswith('2') and path is not None and logee in path:
                total_2xx += 1
            elif status_code.startswith('4') and path is not None and logee in path:
                total_4xx += 1
                log_request_count_total.labels(
                    method=method, path=path, status_code=status_code, source=source_label
                ).inc()
            elif status_code.startswith('5') and path is not None and logee in path:
                total_5xx += 1
                log_request_count_total.labels(
                    method=method, path=path, status_code=status_code, source=source_label
                ).inc()

            # Cập nhật các metrics tổng
            status_2xx_count.labels(source=source_label).set(total_2xx)
            status_4xx_count.labels(source=source_label).set(total_4xx)
            status_5xx_count.labels(source=source_label).set(total_5xx)

# Chạy server Prometheus và bắt đầu đọc log
if __name__ == '__main__':
    start_http_server(8021)  # Khởi động server Prometheus tại port 8021

    # Tạo các thread để xử lý từng file log riêng biệt

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
