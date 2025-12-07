"""
Page Inspector for tariffs.flexport.com

This script opens the tariffs.flexport.com website in a browser
and helps discover the actual page structure, form fields, and
API endpoints used by the site.
"""

import json
from playwright.sync_api import sync_playwright


def inspect_tariff_page():
    """
    Inspect the tariffs.flexport.com page structure.

    This function:
    1. Opens the website in a visible browser
    2. Captures network requests to find API endpoints
    3. Analyzes the page structure
    4. Saves findings to a JSON file
    """

    with sync_playwright() as p:
        # Launch browser in non-headless mode so we can see what's happening
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Store network requests
        api_requests = []
        api_responses = []

        def handle_request(request):
            """Capture all network requests."""
            if 'api' in request.url.lower() or 'graphql' in request.url.lower():
                api_requests.append({
                    'url': request.url,
                    'method': request.method,
                    'headers': dict(request.headers),
                    'post_data': request.post_data
                })
                print(f"[REQUEST] {request.method} {request.url}")

        def handle_response(response):
            """Capture API responses."""
            if 'api' in response.url.lower() or 'graphql' in response.url.lower():
                try:
                    api_responses.append({
                        'url': response.url,
                        'status': response.status,
                        'headers': dict(response.headers)
                    })
                    print(f"[RESPONSE] {response.status} {response.url}")
                except Exception as e:
                    print(f"Error capturing response: {e}")

        # Set up network monitoring
        page.on("request", handle_request)
        page.on("response", handle_response)

        # Navigate to the page
        print("Navigating to tariffs.flexport.com...")
        page.goto("https://tariffs.flexport.com")
        page.wait_for_load_state("networkidle")

        # Analyze page structure
        print("\n=== Analyzing page structure ===\n")

        # Find all input fields
        inputs = page.query_selector_all("input")
        print(f"Found {len(inputs)} input fields:")
        input_info = []
        for i, inp in enumerate(inputs):
            info = {
                'index': i,
                'type': inp.get_attribute('type'),
                'name': inp.get_attribute('name'),
                'id': inp.get_attribute('id'),
                'placeholder': inp.get_attribute('placeholder'),
                'class': inp.get_attribute('class')
            }
            input_info.append(info)
            print(f"  Input {i}: {info}")

        # Find all select dropdowns
        selects = page.query_selector_all("select")
        print(f"\nFound {len(selects)} select dropdowns:")
        select_info = []
        for i, sel in enumerate(selects):
            info = {
                'index': i,
                'name': sel.get_attribute('name'),
                'id': sel.get_attribute('id'),
                'class': sel.get_attribute('class')
            }
            select_info.append(info)
            print(f"  Select {i}: {info}")

        # Find all buttons
        buttons = page.query_selector_all("button")
        print(f"\nFound {len(buttons)} buttons:")
        button_info = []
        for i, btn in enumerate(buttons):
            info = {
                'index': i,
                'type': btn.get_attribute('type'),
                'text': btn.inner_text()[:50] if btn.inner_text() else None,
                'class': btn.get_attribute('class')
            }
            button_info.append(info)
            print(f"  Button {i}: {info}")

        # Check for React or Vue components
        print("\n=== Checking for JavaScript frameworks ===")
        has_react = page.evaluate("() => !!window.React || !!document.querySelector('[data-reactroot]')")
        has_vue = page.evaluate("() => !!window.Vue || !!document.querySelector('[data-v-]')")
        print(f"React detected: {has_react}")
        print(f"Vue detected: {has_vue}")

        # Save all findings
        findings = {
            'url': 'https://tariffs.flexport.com',
            'timestamp': page.evaluate('() => new Date().toISOString()'),
            'page_title': page.title(),
            'inputs': input_info,
            'selects': select_info,
            'buttons': button_info,
            'api_requests': api_requests,
            'api_responses': api_responses,
            'has_react': has_react,
            'has_vue': has_vue
        }

        # Save to file
        with open('page_inspection.json', 'w') as f:
            json.dump(findings, indent=2, fp=f)

        print(f"\n=== Inspection complete ===")
        print(f"Findings saved to page_inspection.json")
        print(f"Captured {len(api_requests)} API requests")
        print(f"Captured {len(api_responses)} API responses")

        # Keep browser open for manual inspection
        print("\nBrowser will stay open for manual inspection.")
        print("You can now interact with the page to see network requests.")
        print("Press Enter when done to close the browser...")
        input()

        browser.close()


if __name__ == "__main__":
    inspect_tariff_page()
