#!/usr/bin/env python3
"""
NetworkPulse - IONIC Health Network Analysis Tool
"""
import sys
import traceback
from gui import NetworkAnalyzerGUI

def main():
    """Main entry point for the NetworkPulse application."""
    print("[DEBUG] Starting NetworkPulse application")
    try:
        app = NetworkAnalyzerGUI()
        app.run()
        print("[DEBUG] NetworkPulse application closed normally")
    except Exception as e:
        print("[DEBUG] Fatal error in NetworkPulse application:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()