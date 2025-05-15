import json
import os

def load_har_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as file:
        contents = file.read()
        if not contents.strip():
            raise ValueError("HAR file is empty.")
        return json.loads(contents)

def extract_requests(har_data):
    entries = har_data.get('log', {}).get('entries', [])
    requests = []

    for entry in entries:
        request = entry.get('request', {})
        response = entry.get('response', {})
        timings = entry.get('timings', {})
        content = response.get('content', {})
        headers = request.get('headers', [])
        cache = entry.get('cache', {})

        # Extract values safely
        url = request.get('url', '')
        method = request.get('method', '')
        status = response.get('status', 0)
        start_time = entry.get('startedDateTime', '')
        mime_type = content.get('mimeType', '')
        response_size = response.get('bodySize', -1)  # -1 = unknown
        time_ms = entry.get('time', 0)

        # Timing breakdown (can be -1 if not captured)
        wait_time = timings.get('wait', -1)
        blocked_time = timings.get('blocked', -1)
        connect_time = timings.get('connect', -1)
        dns_time = timings.get('dns', -1)
        ssl_time = timings.get('ssl', -1)
        redirect_time = timings.get('redirect', -1)

        # Extra metadata
        server_ip = entry.get('serverIPAddress', '')
        priority = entry.get('_priority', '')  # Chrome-only
        referer = next((h['value'] for h in headers if h.get('name', '').lower() == 'referer'), '')

        requests.append({
            'url': url,
            'method': method,
            'status': status,
            'start_time': start_time,
            'time_ms': time_ms,
            'mime_type': mime_type,
            'response_size': response_size,
            'wait_time': wait_time,
            'blocked_time': blocked_time,
            'connect_time': connect_time,
            'dns_time': dns_time,
            'ssl_time': ssl_time,
            'redirect_time': redirect_time,
            'server_ip': server_ip,
            'priority': priority,
            'referer': referer,
            'request_headers': headers,
            "startedDateTime": start_time,
            'cache': cache,
        })

    return requests