#!/usr/bin/env python3
"""
Tourist Trap Detector - CLI interface
"""
import sys
from src.config import validate_config
from src.analyzer import analyze_venue, format_analysis


def main():
    # Validate configuration
    try:
        validate_config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please copy .env.example to .env and fill in your API keys.")
        sys.exit(1)

    # Get input
    if len(sys.argv) > 1:
        # Command line arguments
        query = sys.argv[1]
        location = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        # Interactive mode
        print("Tourist Trap Detector")
        print("-" * 40)
        query = input("Enter restaurant name: ").strip()
        location = input("Enter city/location (optional): ").strip() or None

    if not query:
        print("Error: Please provide a restaurant name")
        sys.exit(1)

    # Run analysis with keyword-based RAG (best accuracy with minimal latency)
    print()
    analysis = analyze_venue(query, location, use_rag=True, rag_mode="keyword")

    # Display results
    print()
    print(format_analysis(analysis))


if __name__ == "__main__":
    main()
