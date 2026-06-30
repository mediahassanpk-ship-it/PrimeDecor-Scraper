"""
Configuration module for PrimeDecor Scraper
Centralized settings for the scraper
"""

import os
from datetime import datetime

# Store Configuration
STORE_URL = "https://primedecor.pk"
STORE_NAME = "primedecor"

# API Configuration
API_ENDPOINTS = {
    "products": f"{STORE_URL}/products.json",
    "collections": f"{STORE_URL}/collections.json",
}

# Scraping Configuration
BATCH_SIZE = 250  # Products per request (Shopify API limit)
MAX_RETRIES = 3  # Maximum retry attempts
RETRY_DELAY = 2  # Seconds between retries
TIMEOUT = 30  # Request timeout in seconds
REQUEST_DELAY = 0.5  # Delay between requests (seconds)

# Pagination
CURSOR_PAGINATION = True  # Use cursor-based pagination
LIMIT_PER_PAGE = 250  # Max products per page

# Output Configuration
OUTPUT_DIR = "output"
OUTPUT_FILENAME = f"PrimeDecor_Products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
ERROR_LOG_PATH = os.path.join(OUTPUT_DIR, "errors.log")
RESUME_STATE_PATH = os.path.join(OUTPUT_DIR, "scrape_state.json")

# Download Configuration
DOWNLOAD_IMAGES = False  # Set to True to download images locally
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
MAX_IMAGES_PER_PRODUCT = 10

# Browser Configuration (for Playwright fallback)
PLAYWRIGHT_TIMEOUT = 60000  # milliseconds
HEADLESS = True
BROWSER_TYPE = "chromium"  # chromium, firefox, webkit

# Headers for requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

# Excel Columns (Order matters)
EXCEL_COLUMNS = [
    "Product ID",
    "Product Handle",
    "Product URL",
    "Product Name",
    "Vendor",
    "Category (Product Type)",
    "Collections",
    "Tags",
    "Description (Plain Text)",
    "Published",
    "Status",
    "Variant ID",
    "Variant Name",
    "Option1",
    "Option2",
    "Option3",
    "SKU",
    "Barcode",
    "Price",
    "Compare At Price",
    "Available",
    "Inventory Quantity",
    "Weight",
    "Weight Unit",
    "Taxable",
    "Requires Shipping",
    "Featured Image",
    "All Image URLs",
    "SEO Title",
    "SEO Description",
]

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Performance Configuration
USE_MULTITHREADING = False  # Set to True for concurrent requests (use carefully)
MAX_WORKERS = 4  # Number of threads if multithreading is enabled

# Scraping Strategy Priority
SCRAPING_STRATEGY_PRIORITY = [
    "shopify_api",  # Try Shopify Products JSON API first
    "cursor_pagination",  # Use cursor-based pagination
    "html_scrape",  # HTML fallback
    "playwright",  # Playwright fallback
]

# Data Validation
MIN_PRODUCT_DATA = {
    "id",
    "handle",
    "title",
    "variants",
}

# Export Configuration
EXPORT_FORMAT = "xlsx"  # xlsx or csv
INCLUDE_EMPTY_VARIANTS = False  # Include products with no variants
CLEAN_HTML_CONTENT = True  # Remove HTML tags from description
