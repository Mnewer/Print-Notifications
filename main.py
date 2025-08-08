#!/usr/bin/env python3
"""
Netum Printer - Development Script

Add your printer tests and functionality here.
"""

from netum_printer import NetumPrinter


def main():
    """Main function - add your code here"""
    
    # Auto-discovery example (recommended):
    with NetumPrinter() as printer:
        if printer.is_connected:
            printer.print_line("Hello from Netum printer!")
            printer.feed_lines(2)
    

if __name__ == "__main__":
    main()