#!/usr/bin/env python3
"""
Example usage of the Satellite Detection API
Demonstrates how to use the API programmatically
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.nasa_api import fetch_satellite_image, validate_coordinates
from utils.web_scraper import NASAWorldviewScraper


async def example_1_basic_image_fetch():
    """Example 1: Fetch a satellite image"""
    print("=" * 60)
    print("Example 1: Fetch Satellite Image")
    print("=" * 60)
    
    # Define parameters
    coordinates = [35.0, -110.0]  # [latitude, longitude]
    date = "2024-01-15"
    
    # Validate coordinates
    if not validate_coordinates(coordinates):
        print(f"Invalid coordinates: {coordinates}")
        return
    
    print(f"Fetching satellite image for:")
    print(f"  Coordinates: {coordinates}")
    print(f"  Date: {date}")
    print()
    
    # Fetch image
    image = await fetch_satellite_image(
        satellite="MODIS",
        product="MOD09GA",
        date=date,
        coordinates=coordinates,
        radius_km=50.0
    )
    
    if image is not None:
        print(f"✓ Successfully fetched image")
        print(f"  Image shape: {image.shape}")
        print(f"  Image dtype: {image.dtype}")
    else:
        print("✗ Failed to fetch image (likely network issue)")
    print()


async def example_2_web_scraper_direct():
    """Example 2: Use web scraper directly"""
    print("=" * 60)
    print("Example 2: Direct Web Scraper Usage")
    print("=" * 60)
    
    scraper = NASAWorldviewScraper()
    
    print("Getting available layers:")
    layers = scraper.get_available_layers()
    for i, layer in enumerate(layers, 1):
        print(f"  {i}. {layer}")
    print()
    
    print("Getting image metadata:")
    coordinates = [35.0, -110.0]
    date = "2024-01-15"
    metadata = scraper.get_image_metadata(coordinates, date)
    print(f"  Source: {metadata['source']}")
    print(f"  Coordinates: {metadata['coordinates']}")
    print(f"  Date: {metadata['date']}")
    print(f"  Timestamp: {metadata['timestamp']}")
    print()


async def example_3_multiple_locations():
    """Example 3: Fetch images for multiple locations"""
    print("=" * 60)
    print("Example 3: Multiple Locations")
    print("=" * 60)
    
    # Define multiple locations
    locations = [
        {"name": "Arizona", "coords": [35.0, -110.0]},
        {"name": "California", "coords": [37.7749, -122.4194]},
        {"name": "Colorado", "coords": [39.0, -105.0]},
    ]
    
    print(f"Fetching images for {len(locations)} locations:")
    print()
    
    for location in locations:
        print(f"  {location['name']}: {location['coords']}")
        
        # Fetch image
        image = await fetch_satellite_image(
            satellite="MODIS",
            product="MOD09GA",
            date="2024-01-15",
            coordinates=location['coords'],
            radius_km=50.0
        )
        
        if image is not None:
            print(f"    ✓ Fetched successfully (shape: {image.shape})")
        else:
            print(f"    ✗ Failed to fetch (network or image not available)")
    print()


async def example_4_different_products():
    """Example 4: Fetch from different satellite products"""
    print("=" * 60)
    print("Example 4: Different Satellite Products")
    print("=" * 60)
    
    products = [
        ("MODIS", "MOD09GA"),
        ("VIIRS", "VNP09"),
        ("GOES", "ABI"),
    ]
    
    coordinates = [35.0, -110.0]
    date = "2024-01-15"
    
    print(f"Fetching image from different products:")
    print()
    
    for satellite, product in products:
        print(f"  {satellite} - {product}:")
        
        image = await fetch_satellite_image(
            satellite=satellite,
            product=product,
            date=date,
            coordinates=coordinates,
            radius_km=50.0
        )
        
        if image is not None:
            print(f"    ✓ Success (shape: {image.shape})")
        else:
            print(f"    ✗ Failed (network or not available)")
    print()


async def example_5_coordinate_validation():
    """Example 5: Validate coordinates"""
    print("=" * 60)
    print("Example 5: Coordinate Validation")
    print("=" * 60)
    
    test_coords = [
        ([35.0, -110.0], True, "Valid US coordinates"),
        ([0.0, 0.0], True, "Valid equator coordinates"),
        ([90.0, 180.0], True, "Valid pole/dateline"),
        ([91.0, -110.0], False, "Invalid latitude (>90)"),
        ([35.0, -181.0], False, "Invalid longitude (<-180)"),
        ([35.0], False, "Missing longitude"),
        ([35.0, -110.0, 0.0], False, "Too many values"),
    ]
    
    print("Testing coordinate validation:")
    print()
    
    for coords, expected, description in test_coords:
        result = validate_coordinates(coords)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {description}")
        print(f"     Input: {coords}")
        print(f"     Result: {result}")
    print()


async def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  Satellite Detection API - Usage Examples".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        # Run examples
        await example_1_basic_image_fetch()
        await example_2_web_scraper_direct()
        await example_3_multiple_locations()
        await example_4_different_products()
        await example_5_coordinate_validation()
        
        print("=" * 60)
        print("All examples completed!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Run the validation script: python validate.py")
        print("2. Start the API server: cd src/api && python -m uvicorn main:app --reload")
        print("3. Test the API: curl http://localhost:8000/health")
        print()
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
