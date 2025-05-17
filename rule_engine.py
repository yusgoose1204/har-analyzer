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
            "rule_id": "Slow TTFB",
            "severity": "warning",
            "message": f"⚠️ Slow TTFB: {wait_time} ms",
            "suggestion": "High TTFB usually means backend slowness, cold starts, or overloaded compute nodes.",
            "sf_context": "May indicate long Apex execution time, slow SOQL queries, unindexed fields, "
                          "or cold container starts on Hyperforce pods. "
                          "Also observed during large transaction commits or lock contention.",
            "next_step": "Check Apex execution time in debug logs\nInvestigate DB query plans\n"
                         "Use Trust pod metrics or Apex CPU Time alerts",
        })

    # Rule 2: Large Payload (> 1MB)
    response_size = request.get('response_size', -1)
    if response_size > 1048576:
        size_mb = round(response_size / (1024 * 1024), 2)
        results.append({
            "rule": "Large Payload",
            "rule_id": "Large Payload",
            "severity": "warning",
            "message": f"⚠️ Large Payload: {size_mb} MB",
            "suggestion": "Consider compressing or lazy-loading large assets to improve initial load time.",
            "sf_context": "Common with large JSON responses from SOQL joins or unfiltered queries. "
                          "Also caused by LWC/Aura components sending full record data "
                          "or excessive static resource loads.",
            "next_step": "Inspect payload via Dev Tools → Network\nEnable debug logs for SOQL optimization\n"
                         "Audit component usage for lazy loading",
        })

    # Rule 3: Error Response
    status = request.get('status', 0)
    if 500 <= status < 600:
        severity = "critical"
        rule_id = "5xx Error"
        suggestion = "Server-side failure. Could be due to app crash, dependency timeout, or server overload."
        sf_context = ("Usually indicates unhandled Apex exceptions, "
                      "timeouts in chained processes (e.g., Platform Events), or infrastructure faults.")
        next_step = ("Review debug logs and exception traces\nCheck Splunk for backend service failures\n"
                     "Review recent deployments or Flow changes")

    elif 400 <= status < 500:
        severity = "warning"
        rule_id = "4xx Error"
        suggestion = "Client-side issue. Could be malformed request, missing auth token, or bad URL."
        sf_context = ("Often seen when expired session tokens, incorrect REST API version, "
                      "or missing headers (like Authorization) are involved. "
                      "Also happens during LWR/Aura misrouting or CORS issues.")
        next_step = ("Re-authenticate and retry\nEnsure correct endpoint structure and headers\n"
                     "Check browser console for CORS or redirect loops")

    else:
        severity = None
        rule_id = None
        suggestion = None
        sf_context = None
        next_step = None

    if severity:
        results.append({
            "rule": "Error Response",
            "rule_id": rule_id,
            "severity": severity,
            "message": f"❌ Error Response: HTTP {status}",
            "suggestion": suggestion,
            "sf_context": sf_context,
            "next_step": next_step,
        })

    # Rule 4: Redirects
    redirect_time = request.get('redirect_time', 0)
    if redirect_time > 0:
        results.append({
            "rule": "Redirect Chain",
            "rule_id": "Redirect Chain",
            "severity": "info",
            "message": f"🔁 Redirected: {redirect_time} ms",
            "suggestion": "Excessive redirects can degrade performance. Consider reducing hops or caching redirect results.",
            "sf_context": "Seen in Experience Cloud (Sites/Communities) with login redirects, custom domain misconfigurations, "
                          "or nested Visualforce → LWR transitions. Sometimes caused by identity providers (SSO).",
            "next_step": "Use browser Dev Tools to trace redirect chain\nReview domain setup and My Domain routing\n"
                         "Test behavior with incognito or different auth flow",
        })

    # Rule 5: High Connect Time
    connect = request.get('connect_time', -1)
    if connect > 500:
        results.append({
            "rule": "High Connect Time",
            "rule_id": "High Connect Time",
            "severity": "medium",
            "message": f"Connect Time High: {connect} ms",
            "suggestion": "May indicate poor client network or proxy interference. Check endpoint proximity and routing.",
            "sf_context": "Common for users connecting from distant regions to a mismatched Hyperforce pod "
                          "(e.g., EMEA to US-West). Also seen when customers use Zscaler or strict firewall policies.",
            "next_step": "Compare performance across regions/IPs\nAsk customer to test without VPN or proxy"
        })

    # Rule 6: High DNS Time
    dns = request.get('dns_time', -1)
    if dns > 300:
        results.append({
            "rule": "High DNS Time",
            "rule_id": "High DNS Time",
            "severity": "low",
            "message": f"DNS Lookup Slow: {dns} ms",
            "suggestion": "Slow DNS resolution can result from custom resolvers or misrouted traffic.",
            "sf_context": "Often indicates stale or poorly resolving DNS routes for custom domains. "
                          "Can also happen with misconfigured vanity URLs or regional failover during Trust incident.",
            "next_step": "Flush DNS and retry\nVerify domain TTL and propagation\nCompare with default Salesforce domain behavior"
        })

    return results
