from har_parser import sanitize_headers

test_headers = [
    {"name": "Authorization", "value": "Bearer abc123"},
    {"name": "Cookie", "value": "session=abcd"},
    {"name": "X-User-Id", "value": "user123"},
    {"name": "Content-Type", "value": "application/json"}
]

sanitized = sanitize_headers(test_headers)
for h in sanitized:
    print(h)
