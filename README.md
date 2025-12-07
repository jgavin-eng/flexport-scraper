# Flexport Tariff API Client

A Python client for programmatically interacting with [tariffs.flexport.com](https://tariffs.flexport.com) to calculate HTS codes, duties, and tariffs for import shipments.

## Overview

This tool provides a Python interface to Flexport's Tariff Simulator, which calculates US import duties and tariffs. Since tariffs.flexport.com does not offer a public API, this client uses browser automation (Playwright) to interact with the website.

## Features

- **Calculate tariffs** for specific HTS codes with country of origin and shipment value
- **Search HTS codes** using plain English product descriptions
- **Compare tariffs** across different countries or time periods
- **Automated browser interaction** with headless or visible browser modes
- **Context manager support** for easy resource management

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd flexport-scraper
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

## Initial Setup

Before using the client, you need to inspect the website structure to discover the correct form field selectors:

```bash
python inspect_page.py
```

This will:
- Open tariffs.flexport.com in a visible browser
- Analyze the page structure
- Capture network requests to discover any internal APIs
- Save findings to `page_inspection.json`

**Important:** After running the inspector, you'll need to update the selectors in `flexport_tariff_client.py` based on the actual page structure discovered.

## Usage

### Basic Example

```python
from flexport_tariff_client import FlexportTariffClient

# Use context manager for automatic resource cleanup
with FlexportTariffClient(headless=True) as client:
    result = client.calculate_tariff(
        hts_code="6203.42.4015",  # Men's trousers of cotton
        country_of_origin="CN",    # China
        shipment_value=10000.00,   # $10,000 USD
        entry_date="2025-01-15"    # January 15, 2025
    )

    print(f"Duty Rate: {result['duty_rate']}")
    print(f"Duty Amount: {result['duty_amount']}")
    print(f"Total Landed Cost: {result['total_landed_cost']}")
```

### Search for HTS Codes

```python
with FlexportTariffClient(headless=False) as client:
    results = client.search_hts_code("laptop computer")

    for result in results:
        print(f"{result['hts_code']}: {result['description']}")
```

### Compare Tariffs from Different Countries

```python
countries = ["CN", "MX", "VN", "IN"]  # China, Mexico, Vietnam, India

with FlexportTariffClient(headless=True) as client:
    for country in countries:
        result = client.calculate_tariff(
            hts_code="8517.62.0050",  # Smartphones
            country_of_origin=country,
            shipment_value=50000.00
        )
        print(f"{country}: {result['duty_amount']}")
```

### Manual Browser Control

```python
# Create client without context manager for more control
client = FlexportTariffClient(headless=False)
client.start()

try:
    result = client.calculate_tariff(
        hts_code="8471.30.0100",
        country_of_origin="CN",
        shipment_value=25000.00
    )
    print(result)
finally:
    client.close()
```

## API Reference

### FlexportTariffClient

#### Constructor Parameters

- `headless` (bool, default=True): Run browser in headless mode
- `timeout` (int, default=30000): Page timeout in milliseconds

#### Methods

##### `calculate_tariff(hts_code, country_of_origin, shipment_value, entry_date=None, quantity=None, unit=None)`

Calculate tariff for a given HTS code and parameters.

**Parameters:**
- `hts_code` (str): The 10-digit HTS (Harmonized Tariff Schedule) code
- `country_of_origin` (str): Country code (e.g., 'CN', 'MX', 'VN')
- `shipment_value` (float): Total value of the shipment in USD
- `entry_date` (str, optional): Date of entry in YYYY-MM-DD format (defaults to today)
- `quantity` (float, optional): Quantity of goods
- `unit` (str, optional): Unit of measure

**Returns:** Dictionary containing:
- `duty_rate`: The duty rate percentage
- `duty_amount`: The calculated duty amount in USD
- `total_landed_cost`: Total cost including duties
- `applicable_tariffs`: List of applicable tariff sections
- `hts_description`: Description of the HTS code

##### `search_hts_code(product_description)`

Search for HTS codes based on a product description.

**Parameters:**
- `product_description` (str): Plain English description of the product

**Returns:** List of dictionaries with `hts_code` and `description`

## Example Scripts

The repository includes several example scripts:

- `example_usage.py`: Comprehensive examples of all features
- `inspect_page.py`: Page structure inspector for discovering selectors

Run examples:
```bash
python example_usage.py
```

## Important Notes

### No Public API

tariffs.flexport.com does not have a public API. This tool uses browser automation to interact with the website. This means:

1. **Page structure changes**: If Flexport updates their website, the selectors may need updating
2. **Rate limiting**: Be respectful and don't make excessive requests
3. **Terms of Service**: Review Flexport's terms before using this tool extensively

### Updating Selectors

The page selectors in `flexport_tariff_client.py` are placeholders. After running `inspect_page.py`, update the selectors in the `_extract_results()` and `calculate_tariff()` methods based on the actual page structure.

### Browser Automation

This tool uses Playwright, which requires downloading browser binaries. The first installation will download Chromium (~100MB).

## Troubleshooting

### Selector Not Found Errors

If you encounter "Could not find..." errors:
1. Run `inspect_page.py` to analyze the current page structure
2. Update the selectors in `flexport_tariff_client.py`
3. Try running with `headless=False` to see what's happening

### Timeout Errors

If calculations are timing out:
- Increase the timeout: `FlexportTariffClient(timeout=60000)`  # 60 seconds
- Check your internet connection
- The website might be experiencing issues

### Installation Issues

If Playwright installation fails:
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2
```

## Contributing

Contributions are welcome! Please:
1. Update the README if you change functionality
2. Test your changes with both headless and visible browser modes
3. Keep the code compatible with the website's current structure

## License

This project is for educational and research purposes. Please review Flexport's terms of service before using this tool.

## Disclaimer

This tool is not officially affiliated with or endorsed by Flexport. It is an independent project that interacts with a publicly available website. Users are responsible for ensuring their usage complies with Flexport's terms of service and applicable laws.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Run `inspect_page.py` to verify the current page structure
3. Open an issue in this repository

## Useful Resources

- [Flexport Tariff Simulator](https://tariffs.flexport.com/)
- [HTS Code Search](https://hts.usitc.gov/)
- [US International Trade Commission](https://www.usitc.gov/)
- [Playwright Documentation](https://playwright.dev/python/)
