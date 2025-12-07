"""
Example usage of the Flexport Tariff Client

This script demonstrates how to use the FlexportTariffClient to:
1. Calculate tariffs for a specific HTS code
2. Search for HTS codes by product description
"""

import json
from datetime import datetime
from flexport_tariff_client import FlexportTariffClient


def example_calculate_tariff():
    """
    Example: Calculate tariff for importing men's trousers from China
    """
    print("=" * 60)
    print("Example 1: Calculate Tariff for Men's Trousers from China")
    print("=" * 60)

    # Use context manager to automatically handle browser lifecycle
    with FlexportTariffClient(headless=False) as client:
        result = client.calculate_tariff(
            hts_code="6203.42.4015",  # Men's trousers of cotton
            country_of_origin="CN",  # China
            shipment_value=10000.00,  # $10,000 USD
            entry_date="2025-01-15"  # January 15, 2025
        )

        print("\nResults:")
        print(json.dumps(result, indent=2))


def example_multiple_countries():
    """
    Example: Compare tariffs from different countries for the same product
    """
    print("\n" + "=" * 60)
    print("Example 2: Compare Tariffs from Different Countries")
    print("=" * 60)

    countries = {
        "CN": "China",
        "MX": "Mexico",
        "VN": "Vietnam",
        "IN": "India"
    }

    hts_code = "8517.62.0050"  # Smartphones
    shipment_value = 50000.00

    with FlexportTariffClient(headless=True) as client:
        for country_code, country_name in countries.items():
            print(f"\n--- Calculating for {country_name} ({country_code}) ---")

            result = client.calculate_tariff(
                hts_code=hts_code,
                country_of_origin=country_code,
                shipment_value=shipment_value,
                entry_date=datetime.now().strftime("%Y-%m-%d")
            )

            print(f"Duty Rate: {result.get('duty_rate', 'N/A')}")
            print(f"Duty Amount: {result.get('duty_amount', 'N/A')}")
            print(f"Total Landed Cost: {result.get('total_landed_cost', 'N/A')}")


def example_search_hts():
    """
    Example: Search for HTS codes using a product description
    """
    print("\n" + "=" * 60)
    print("Example 3: Search for HTS Codes")
    print("=" * 60)

    product_descriptions = [
        "laptop computer",
        "men's cotton shirt",
        "wooden furniture"
    ]

    with FlexportTariffClient(headless=False) as client:
        for description in product_descriptions:
            print(f"\nSearching for: '{description}'")

            results = client.search_hts_code(description)

            print(f"Found {len(results)} results:")
            for i, result in enumerate(results[:5], 1):  # Show top 5 results
                print(f"  {i}. {result.get('hts_code', 'N/A')}: {result.get('description', 'N/A')[:100]}")


def example_time_comparison():
    """
    Example: Compare tariffs for the same product at different dates
    """
    print("\n" + "=" * 60)
    print("Example 4: Compare Tariffs at Different Dates")
    print("=" * 60)

    hts_code = "8471.30.0100"  # Portable computers
    country = "CN"
    value = 25000.00

    dates = [
        "2024-01-01",
        "2024-06-01",
        "2025-01-01"
    ]

    with FlexportTariffClient(headless=True) as client:
        for entry_date in dates:
            print(f"\n--- Entry Date: {entry_date} ---")

            result = client.calculate_tariff(
                hts_code=hts_code,
                country_of_origin=country,
                shipment_value=value,
                entry_date=entry_date
            )

            print(f"Duty Rate: {result.get('duty_rate', 'N/A')}")
            print(f"Applicable Tariffs: {', '.join(result.get('applicable_tariffs', []))}")


def main():
    """
    Run all examples.

    Note: Set headless=False in any example to see the browser in action.
    """
    print("\n" + "=" * 60)
    print("Flexport Tariff Client - Example Usage")
    print("=" * 60)
    print("\nNOTE: These examples require the actual page structure to be")
    print("analyzed first. Run 'inspect_page.py' to discover the correct")
    print("selectors, then update 'flexport_tariff_client.py' accordingly.\n")

    try:
        # Run example 1 - basic tariff calculation
        example_calculate_tariff()

        # Uncomment to run other examples:
        # example_multiple_countries()
        # example_search_hts()
        # example_time_comparison()

    except Exception as e:
        print(f"\nError: {e}")
        print("\nThis error likely occurred because the page selectors need to be updated.")
        print("Please run 'inspect_page.py' first to discover the actual page structure.")


if __name__ == "__main__":
    main()
