# -*- coding: utf-8 -*-
import re
import time
from prometheus_client import start_http_server, Counter, Histogram
from prometheus_client.core import CollectorRegistry
from collections import defaultdict

# Khởi tạo biểu thức regex
log_pattern = re.compile(r'^(?P<remote>[^ ]*) (?P<host>[^ ]*) (?P<user>[^ ]*) \[(?P<time>[^\]]*)\] \"(?P<method>\w+)(?:\s+(?P<path>[^\"]*?)(?:\s+\S*)?)?\" (?P<status_code>[^ ]*) (?P<size>[^ ]*)(?:\s"(?P<referer>[^\"]*)") "(?P<agent>[^\"]*)"')

# Khởi tạo metrics
request_count = Counter('log_request_count', 'Number of requests', ['method', 'status_code', 'path'])
request_size = Histogram('log_request_size', 'Size of requests', ['method', 'path'])

def parse_log_line(line):
    match = log_pattern.match(line)
    if match:
        data = match.groupdict()
        method = data['method']
        path = data['path'] or '/'
        status_code = data['status_code']
        size = int(data['size']) if data['size'].isdigit() else 0
       
        # Cập nhật metrics
        request_count.labels(method=method, status_code=status_code, path=path).inc()
        request_size.labels(method=method, path=path).observe(size)
    else:
        print("Không khớp:", line)

def tail_log(file_path):
    with open(file_path, 'r') as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            parse_log_line(line)

if __name__ == "__main__":
    log_file_path = '/u01/deployments/nginx/log/test.log'
    start_http_server(20165)  # Prometheus sẽ scrape tại port 8000
    tail_log(log_file_path)
