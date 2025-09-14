#!/usr/bin/env python3
"""
Start script for the Manim FastMCP server.
"""

import sys
import os

# Add the parent directory to Python path to import manim
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import mcp

if __name__ == "__main__":
    print("Starting Manim FastMCP server...")
    print(f"Manim version: {__import__('manim').__version__}")
    print("Server ready to accept connections")
    mcp.run()