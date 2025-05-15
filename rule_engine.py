def analyze_request(request):
    """
    Applies rule-based checks to a single request.
    Returns a list of triggered rule dicts, each with:
      - rule: name of the rule
      - severity: info | warning | critical
      - message: human-readable explanation
    """
    results = []

    # Rule 1: Slow TTFB (> 500ms)
    wait_time = request.get('wait_time', -1)
    if wait_time > 500:
        results.append({
            "rule": "Slow TTFB",
            "severity": "warning",
            "message": f"⚠️ Slow TTFB: {wait_time} ms"
        })

    # Rule 2: Large Payload (> 1MB)
    response_size = request.get('response_size', -1)
    if response_size > 1048576:
        size_mb = round(response_size / (1024 * 1024), 2)
        results.append({
            "rule": "Large Payload",
            "severity": "warning",
            "message": f"⚠️ Large Payload: {size_mb} MB"
        })

    # Rule 3: Error Response
    status = request.get('status', 0)
    if 500 <= status < 600:
        severity = "critical"
    elif 400 <= status < 500:
        severity = "warning"
    else:
        severity = None

    if severity:
        results.append({
            "rule": "Error Response",
            "severity": severity,
            "message": f"❌ Error Response: HTTP {status}"
        })

    # Rule 4: Redirects
    redirect_time = request.get('redirect_time', 0)
    if redirect_time > 0:
        results.append({
            "rule": "Redirect Chain",
            "severity": "info",
            "message": f"🔁 Redirected: {redirect_time} ms"
        })

    return results
