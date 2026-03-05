"""Example: Monitor government sources for changes"""

import sys
sys.path.insert(0, 'src')

from verigov.main import VeriGovApp


def main():
    """Monitor sources for changes"""
    app = VeriGovApp()
    
    # Sources to monitor
    sources = [
        "https://www.whitehouse.gov/briefing-room/",
        "https://www.congress.gov/"
    ]
    
    print("Starting source monitoring...")
    print("Press Ctrl+C to stop")
    
    # Monitor with 1 hour interval
    app.monitor_sources(sources, interval=3600)


if __name__ == "__main__":
    main()
