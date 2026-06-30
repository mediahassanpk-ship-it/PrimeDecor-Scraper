"""
Utility functions for PrimeDecor Scraper
Helper functions for data processing, logging, and general utilities
"""

import logging
import json
import os
import time
import re
from typing import Any, Dict, List, Optional
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
import hashlib

from config import (
    OUTPUT_DIR, ERROR_LOG_PATH, LOG_LEVEL, LOG_FORMAT,
    RETRY_DELAY, MAX_RETRIES, CLEAN_HTML_CONTENT
)


class MLStripper(HTMLParser):
    """HTML stripper to remove HTML tags from text"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def setup_logging():
    """Setup logging configuration"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    logger = logging.getLogger("PrimeDecor_Scraper")
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(ERROR_LOG_PATH)
    file_handler.setLevel(logging.WARNING)
    file_formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(f"PrimeDecor_Scraper.{name}")


def strip_html(html_text: str) -> str:
    """Remove HTML tags from text"""
    if not html_text:
        return ""
    
    if not CLEAN_HTML_CONTENT:
        return html_text
    
    try:
        stripper = MLStripper()
        stripper.feed(html_text)
        return stripper.get_data().strip()
    except Exception as e:
        get_logger("utils").warning(f"Error stripping HTML: {e}")
        return html_text


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Convert to string if not already
    text = str(text).strip()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove HTML tags if needed
    if '<' in text and '>' in text:
        text = strip_html(text)
    
    return text


def normalize_url(url: str, base_url: str = "") -> str:
    """Normalize and construct full URLs"""
    if not url:
        return ""
    
    url = url.strip()
    
    # Handle relative URLs
    if url.startswith('/'):
        if base_url:
            parsed = urlparse(base_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
        url = urljoin(base_url, url)
    
    return url


def retry_with_backoff(func, *args, max_retries=MAX_RETRIES, delay=RETRY_DELAY, **kwargs):
    """
    Retry a function with exponential backoff
    
    Args:
        func: Function to retry
        *args: Function arguments
        max_retries: Maximum retry attempts
        delay: Initial delay between retries
        **kwargs: Function keyword arguments
    
    Returns:
        Function result or None
    """
    logger = get_logger("utils")
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed after {max_retries} attempts: {str(e)}")
                raise
            
            wait_time = delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time}s...")
            time.sleep(wait_time)


def ensure_output_dir():
    """Ensure output directory exists"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "images"), exist_ok=True)


def save_state(state: Dict[str, Any], filepath: str):
    """Save scraper state for resume functionality"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        get_logger("utils").error(f"Error saving state: {e}")


def load_state(filepath: str) -> Dict[str, Any]:
    """Load previous scraper state"""
    if not os.path.exists(filepath):
        return {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        get_logger("utils").warning(f"Error loading state: {e}")
        return {}


def hash_product(product_data: Dict) -> str:
    """Generate unique hash for product to detect duplicates"""
    try:
        # Use product ID and title for hashing
        unique_str = f"{product_data.get('id', '')}{product_data.get('handle', '')}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    except Exception:
        return ""


def format_price(price: Any) -> Optional[float]:
    """Format price to float"""
    if price is None or price == "":
        return None
    
    try:
        return float(str(price).strip())
    except (ValueError, AttributeError):
        return None


def format_bool(value: Any) -> bool:
    """Convert value to boolean"""
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'on')
    
    return bool(value)


def format_date(date_str: str) -> str:
    """Format ISO date string to readable format"""
    if not date_str:
        return ""
    
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return date_str


def parse_tags(tags_str: str) -> List[str]:
    """Parse comma-separated tags"""
    if not tags_str:
        return []
    
    tags = str(tags_str).split(',')
    return [tag.strip() for tag in tags if tag.strip()]


def parse_collections(collections: List[Dict]) -> str:
    """Parse collections list to comma-separated string"""
    if not collections:
        return ""
    
    try:
        if isinstance(collections, str):
            return collections
        
        collection_titles = [c.get('title', '') for c in collections if isinstance(c, dict)]
        return ", ".join(collection_titles)
    except Exception:
        return ""


def format_inventory_quantity(variants: List[Dict]) -> int:
    """Calculate total inventory quantity from variants"""
    if not variants:
        return 0
    
    total = 0
    try:
        for variant in variants:
            if isinstance(variant, dict):
                inventory_qty = variant.get('inventory_quantity', 0)
                if inventory_qty:
                    total += int(inventory_qty)
    except Exception:
        pass
    
    return total


def format_available(variant: Dict) -> bool:
    """Check if variant is available"""
    if not isinstance(variant, dict):
        return False
    
    # Check if available quantity is greater than 0
    if variant.get('inventory_quantity', 0) > 0:
        return True
    
    # Check available field
    return variant.get('available', False)


def extract_image_urls(images: List[Dict], max_images: int = 10) -> List[str]:
    """Extract image URLs from images list"""
    if not images:
        return []
    
    urls = []
    try:
        for image in images[:max_images]:
            if isinstance(image, dict) and 'src' in image:
                urls.append(image['src'])
    except Exception:
        pass
    
    return urls


def validate_product_data(product: Dict) -> bool:
    """Validate product has required data"""
    required_fields = {'id', 'handle', 'title'}
    return all(field in product for field in required_fields)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for file system"""
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, '_', filename)


def format_variant_name(variant: Dict, product_title: str = "") -> str:
    """Generate readable variant name from options"""
    try:
        options = []
        
        # Collect variant options
        for i in range(1, 4):
            option_key = f"option{i}"
            if option_key in variant and variant[option_key]:
                options.append(variant[option_key])
        
        if options:
            return " - ".join(options)
        
        # Fallback to variant title or product title
        return variant.get('title', product_title)
    except Exception:
        return ""


def format_weight_unit(weight_unit: str) -> str:
    """Normalize weight unit"""
    if not weight_unit:
        return "kg"
    
    unit = str(weight_unit).lower().strip()
    
    if unit in ('kilogram', 'kg', 'kilogrammes'):
        return 'kg'
    elif unit in ('gram', 'g', 'grams'):
        return 'g'
    elif unit in ('pound', 'lb', 'lbs', 'pounds'):
        return 'lb'
    elif unit in ('ounce', 'oz', 'ounces'):
        return 'oz'
    
    return unit


def detect_charset(response_text: str) -> str:
    """Detect charset from response"""
    # Look for charset in meta tags
    match = re.search(r'charset=([a-z0-9\-]+)', response_text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return 'utf-8'


def is_valid_url(url: str) -> bool:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None


def merge_product_variants(products: List[Dict]) -> List[Dict]:
    """
    Merge products with multiple variants into individual rows
    
    Args:
        products: List of product dictionaries
    
    Returns:
        List of product rows with each variant as separate row
    """
    rows = []
    
    try:
        for product in products:
            variants = product.get('variants', [])
            
            if not variants:
                # Product with no variants - create single row
                rows.append(product)
                continue
            
            # Create row for each variant
            for variant in variants:
                row = product.copy()
                row['variant'] = variant
                rows.append(row)
    
    except Exception as e:
        get_logger("utils").error(f"Error merging variants: {e}")
    
    return rows


def get_time_estimate(total_items: int, items_per_second: float = 0.5) -> str:
    """Estimate time needed to scrape"""
    if items_per_second <= 0:
        return "Unknown"
    
    seconds = total_items / items_per_second
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def print_summary(stats: Dict[str, Any]):
    """Print scraping summary"""
    logger = get_logger("utils")
    
    logger.info("=" * 60)
    logger.info("SCRAPING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total Products: {stats.get('total_products', 0)}")
    logger.info(f"Total Variants: {stats.get('total_variants', 0)}")
    logger.info(f"Errors: {stats.get('errors', 0)}")
    logger.info(f"Duration: {stats.get('duration', 'Unknown')}")
    logger.info(f"Output File: {stats.get('output_file', 'Unknown')}")
    logger.info("=" * 60)
