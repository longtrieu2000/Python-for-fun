import re
import time
from prometheus_client import start_http_server, Counter, Histogram

# Định nghĩa các metrics
REQUEST_COUNT = Counter('log_request_count', 'Number of requests', ['method', 'status_code', 'path'])
REQUEST_SIZE = Histogram('log_request_size', 'Size of requests', ['method', 'path'])

# Đường dẫn tới file log
LOG_FILE_PATH = '/path/to/your/logfile.log'

# Regular expression để phân tích log
LOG_REGEX = r'^(?P<remote>[^ ]*) (?P<host>[^ ]*) (?P<user>[^ ]*) \[(?P<time>[^\]]*)\] "(?P<method>\w+)(?:\s+(?P<path>[^\"]*?)(?:\s+\S*)?)?" (?P<status_code>[^ ]*) (?P<size>[^ ]*)(?:\s"(?P<referer>[^\"]*)") "(?P<agent>[^\"]*)"'

def parse_log_line(line):
    match = re.match(LOG_REGEX, line)
    if match:
        # Lấy các nhóm từ match
        method = match.group('method')
        status_code = match.group('status_code')
        path = match.group('path') or ''
        size = int(match.group('size'))
        
        # Cập nhật metrics
        REQUEST_COUNT.labels(method=method, status_code=status_code, path=path).inc()
        REQUEST_SIZE.labels(method=method, path=path).observe(size)

def main():
    # Bắt đầu HTTP server trên port 8000
    start_http_server(20164)
    
    # Đọc file log và phân tích
    with open(LOG_FILE_PATH, 'r') as log_file:
        # Đọc log từ cuối file
        log_file.seek(0, 2)  # Move to the end of the file
        while True:
            line = log_file.readline()
            if not line:
                time.sleep(1)  # Sleep if no new line
                continue
            parse_log_line(line)

if __name__ == '__main__':
    main()
