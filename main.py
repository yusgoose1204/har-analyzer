from har_parser import load_har_file, extract_requests
from rule_engine import analyze_request
from visualizer import plot_top_slowest_requests, show_dashboard

# Define severity ranking
SEVERITY_ORDER = {
    "critical": 0,
    "warning": 1,
    "info": 2
}

def print_flagged_requests(requests):
    print("\n🚩 Rule-Based Issues Found:\n")
    any_issues = False

    for req in requests:
        results = analyze_request(req)
        if results:
            any_issues = True
            print(f"🔍 {req['method']} {req['url']}")

            # Sort rule results by severity
            sorted_results = sorted(
                results,
                key=lambda r: SEVERITY_ORDER.get(r['severity'], 99)
            )

            for r in sorted_results:
                print(f"   [{r['severity'].upper()}] {r['message']}")
            print("-" * 70)

    if not any_issues:
        print("✅ No rule violations found in this HAR file.")


# filepath = "./sample.har"
# har_data = load_har_file(filepath)
# requests = extract_requests(har_data)
# show_dashboard(requests)