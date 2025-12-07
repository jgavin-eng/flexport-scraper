"""
Flexport Tariff API Client

This client provides programmatic access to tariffs.flexport.com
to calculate HTS codes, duties, and tariffs for import shipments.

Note: tariffs.flexport.com does not have a public API, so this client
uses browser automation to interact with the website.
"""

import json
import time
from datetime import datetime
from typing import Dict, Optional, Any
from playwright.sync_api import sync_playwright, Page, Browser, Playwright


class FlexportTariffClient:
    """
    Client for interacting with Flexport's Tariff Simulator.

    This client uses browser automation to interact with tariffs.flexport.com
    since no public API is available.
    """

    BASE_URL = "https://tariffs.flexport.com"

    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Initialize the Flexport Tariff Client.

        Args:
            headless: Whether to run the browser in headless mode
            timeout: Page timeout in milliseconds (default: 30 seconds)
        """
        self.headless = headless
        self.timeout = timeout
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def start(self):
        """Start the browser session."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        self.page.set_default_timeout(self.timeout)

    def close(self):
        """Close the browser session."""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def calculate_tariff(
        self,
        hts_code: str,
        country_of_origin: str,
        shipment_value: float,
        entry_date: Optional[str] = None,
        quantity: Optional[float] = None,
        unit: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate tariff for a given HTS code and parameters.

        Args:
            hts_code: The 10-digit HTS (Harmonized Tariff Schedule) code
            country_of_origin: Country code (e.g., 'CN' for China, 'MX' for Mexico)
            shipment_value: Total value of the shipment in USD
            entry_date: Date of entry in YYYY-MM-DD format (defaults to today)
            quantity: Quantity of goods (optional, depends on HTS code)
            unit: Unit of measure (optional, depends on HTS code)

        Returns:
            Dictionary containing tariff calculation results including:
            - duty_rate: The duty rate percentage
            - duty_amount: The calculated duty amount in USD
            - total_landed_cost: Total cost including duties
            - applicable_tariffs: List of applicable tariff sections
            - hts_description: Description of the HTS code
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first or use context manager.")

        # Set default entry date to today if not provided
        if not entry_date:
            entry_date = datetime.now().strftime("%Y-%m-%d")

        # Navigate to the calculator
        self.page.goto(self.BASE_URL)

        # Wait for the page to load
        self.page.wait_for_load_state("networkidle")

        # Input HTS code
        # Note: The actual selector will need to be updated based on the website's structure
        try:
            # Try to find the HTS code input field
            hts_input = self.page.wait_for_selector(
                'input[placeholder*="HTS"], input[name*="hts"], input[id*="hts"]',
                timeout=5000
            )
            if hts_input:
                hts_input.fill(hts_code)
        except Exception as e:
            # If we can't find it automatically, we may need to inspect the page
            raise Exception(f"Could not find HTS code input field. Error: {e}")

        # Select country of origin
        try:
            country_selector = self.page.wait_for_selector(
                'select[name*="country"], select[id*="country"], input[placeholder*="country"]',
                timeout=5000
            )
            if country_selector:
                # Check if it's a select dropdown or an autocomplete input
                if country_selector.evaluate("el => el.tagName") == "SELECT":
                    country_selector.select_option(label=country_of_origin)
                else:
                    country_selector.fill(country_of_origin)
                    # Wait for autocomplete and select
                    time.sleep(0.5)
                    self.page.keyboard.press("ArrowDown")
                    self.page.keyboard.press("Enter")
        except Exception as e:
            raise Exception(f"Could not find country selector. Error: {e}")

        # Input shipment value
        try:
            value_input = self.page.wait_for_selector(
                'input[placeholder*="value"], input[name*="value"], input[type="number"]',
                timeout=5000
            )
            if value_input:
                value_input.fill(str(shipment_value))
        except Exception as e:
            raise Exception(f"Could not find shipment value input. Error: {e}")

        # Input entry date if field exists
        try:
            date_input = self.page.query_selector(
                'input[type="date"], input[placeholder*="date"], input[name*="date"]'
            )
            if date_input:
                date_input.fill(entry_date)
        except Exception:
            # Date field might not always be present
            pass

        # Click calculate button
        try:
            calculate_button = self.page.wait_for_selector(
                'button:has-text("Calculate"), button[type="submit"], input[type="submit"]',
                timeout=5000
            )
            if calculate_button:
                calculate_button.click()
        except Exception as e:
            raise Exception(f"Could not find calculate button. Error: {e}")

        # Wait for results
        self.page.wait_for_load_state("networkidle")
        time.sleep(2)  # Additional wait for dynamic content

        # Extract results
        # Note: These selectors will need to be updated based on the actual page structure
        results = self._extract_results()

        return results

    def _extract_results(self) -> Dict[str, Any]:
        """
        Extract tariff calculation results from the page.

        Returns:
            Dictionary containing the extracted results
        """
        results = {
            "hts_code": None,
            "hts_description": None,
            "country_of_origin": None,
            "duty_rate": None,
            "duty_amount": None,
            "total_landed_cost": None,
            "applicable_tariffs": [],
            "raw_html": None
        }

        # Try to extract results from the page
        # This will need to be customized based on the actual page structure
        try:
            # Get the entire page content for debugging
            results["raw_html"] = self.page.content()

            # Try to find result elements
            # These are example selectors - they need to be updated based on actual page structure

            # Look for duty rate
            duty_rate_element = self.page.query_selector(
                '[class*="duty"], [class*="rate"], [id*="duty"]'
            )
            if duty_rate_element:
                results["duty_rate"] = duty_rate_element.inner_text()

            # Look for total cost
            total_element = self.page.query_selector(
                '[class*="total"], [class*="landed"], [id*="total"]'
            )
            if total_element:
                results["total_landed_cost"] = total_element.inner_text()

            # Look for HTS description
            description_element = self.page.query_selector(
                '[class*="description"], [class*="hts-desc"]'
            )
            if description_element:
                results["hts_description"] = description_element.inner_text()

        except Exception as e:
            results["error"] = f"Error extracting results: {e}"

        return results

    def search_hts_code(self, product_description: str) -> list:
        """
        Search for HTS codes based on a product description.

        Args:
            product_description: Plain English description of the product

        Returns:
            List of potential HTS codes with descriptions
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first or use context manager.")

        self.page.goto(self.BASE_URL)
        self.page.wait_for_load_state("networkidle")

        # Find search box and enter description
        try:
            search_input = self.page.wait_for_selector(
                'input[placeholder*="search"], input[placeholder*="product"]',
                timeout=5000
            )
            if search_input:
                search_input.fill(product_description)
                self.page.keyboard.press("Enter")

            # Wait for results
            self.page.wait_for_load_state("networkidle")
            time.sleep(1)

            # Extract search results
            results = []
            # This selector needs to be updated based on actual page structure
            result_elements = self.page.query_selector_all('[class*="search-result"], [class*="hts-result"]')

            for element in result_elements:
                results.append({
                    "hts_code": element.query_selector('[class*="code"]').inner_text() if element.query_selector('[class*="code"]') else None,
                    "description": element.inner_text()
                })

            return results

        except Exception as e:
            raise Exception(f"Error searching for HTS codes: {e}")


def main():
    """Example usage of the FlexportTariffClient."""

    # Example: Calculate tariff for a product from China
    with FlexportTariffClient(headless=False) as client:
        result = client.calculate_tariff(
            hts_code="6203.42.4015",  # Example HTS code for men's trousers
            country_of_origin="CN",  # China
            shipment_value=10000.00,  # $10,000 USD
            entry_date="2025-01-15"  # January 15, 2025
        )

        print("Tariff Calculation Results:")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
