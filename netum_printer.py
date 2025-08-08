#!/usr/bin/env python3
"""
Netum Bluetooth Printer Connection Module

This module provides a clean interface for connecting to and printing with
Netum Bluetooth thermal printers (NT-1809D and compatible models).

Supports automatic printer discovery or manual configuration.
"""

import serial
import serial.tools.list_ports
import time
import re
from typing import Optional, Union, List


def discover_netum_printers() -> List[dict]:
    """
    Discover Netum printers connected via Bluetooth
    
    Returns:
        List of dictionaries with printer information:
        [{'port': 'COM8', 'description': '...', 'bt_address': '66:22:FA:2B:78:F1'}]
    """
    printers = []
    
    # Get all Bluetooth COM ports
    ports = list(serial.tools.list_ports.comports())
    bt_ports = [p for p in ports if 'bluetooth' in p.description.lower()]
    
    for port in bt_ports:
        printer_info = {
            'port': port.device,
            'description': port.description,
            'bt_address': None
        }
        
        # Extract Bluetooth address from hardware ID if available
        if hasattr(port, 'hwid') and port.hwid:
            # Look for pattern like "6622FA2B78F1" in hardware ID
            bt_match = re.search(r'([0-9A-F]{12})', port.hwid.upper())
            if bt_match:
                bt_addr = bt_match.group(1)
                # Format as standard BT address: XX:XX:XX:XX:XX:XX
                formatted_addr = ':'.join([bt_addr[i:i+2] for i in range(0, 12, 2)])
                printer_info['bt_address'] = formatted_addr
        
        printers.append(printer_info)
    
    return printers


class NetumPrinter:
    """Interface for Netum Bluetooth thermal printers"""
    
    def __init__(self, port: Optional[str] = None, baudrate: int = 9600, auto_discover: bool = True):
        """
        Initialize printer connection parameters
        
        Args:
            port: COM port for the printer (None for auto-discovery)
            baudrate: Connection speed (default: 9600)
            auto_discover: Automatically find the first available Netum printer
        """
        self.baudrate = baudrate
        self.connection: Optional[serial.Serial] = None
        self.is_connected = False
        
        # Auto-discover printer if no port specified
        if port is None and auto_discover:
            printers = discover_netum_printers()
            if printers:
                # Prefer COM8 if it exists (known working port)
                preferred_port = None
                for printer in printers:
                    if printer['port'] == 'COM8':
                        preferred_port = printer
                        break
                
                if preferred_port:
                    self.port = preferred_port['port']
                    print(f"Auto-discovered Netum printer on {self.port} (preferred)")
                    if preferred_port['bt_address']:
                        print(f"Bluetooth address: {preferred_port['bt_address']}")
                else:
                    # Use first available
                    self.port = printers[0]['port']
                    print(f"Auto-discovered Netum printer on {self.port}")
                    if printers[0]['bt_address']:
                        print(f"Bluetooth address: {printers[0]['bt_address']}")
            else:
                print("No Bluetooth printers found. Please specify port manually.")
                self.port = None
        else:
            self.port = port
    
    def connect(self) -> bool:
        """
        Connect to the printer
        
        Returns:
            True if connection successful, False otherwise
        """
        if self.port is None:
            print("No printer port specified. Use auto_discover=True or provide port manually.")
            return False
            
        try:
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=8,
                parity=serial.PARITY_NONE,
                stopbits=1,
                timeout=3,
                write_timeout=3
            )
            self.is_connected = True
            print(f"Connected to Netum printer on {self.port}")
            return True
            
        except serial.SerialException as e:
            print(f"Connection failed: {e}")
            print("Make sure the printer is:")
            print("  - Powered on")
            print("  - Bluetooth paired and connected")
            print("  - Not being used by another application")
            self.is_connected = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the printer"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            self.is_connected = False
            print("Disconnected from printer")
    
    def print_text(self, text: Union[str, bytes]) -> bool:
        """
        Print text to the printer
        
        Args:
            text: Text to print (string or bytes)
            
        Returns:
            True if print successful, False otherwise
        """
        if not self.is_connected or not self.connection:
            print("Not connected to printer")
            return False
        
        try:
            # Convert string to bytes if needed
            if isinstance(text, str):
                data = text.encode('utf-8')
            else:
                data = text
                
            bytes_written = self.connection.write(data)
            self.connection.flush()
            
            print(f"Sent {bytes_written} bytes to printer")
            return True
            
        except Exception as e:
            print(f"Print failed: {e}")
            return False
    
    def print_line(self, text: str = "") -> bool:
        """
        Print a line of text with newline
        
        Args:
            text: Text to print (empty string for blank line)
            
        Returns:
            True if print successful, False otherwise
        """
        return self.print_text(text + "\n")
    
    def feed_lines(self, count: int = 3) -> bool:
        """
        Feed blank lines (useful for separating printouts)
        
        Args:
            count: Number of blank lines to feed
            
        Returns:
            True if successful, False otherwise  
        """
        return self.print_text("\n" * count)
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


def list_available_printers():
    """List all available Netum printers"""
    print("=== Available Netum Printers ===")
    printers = discover_netum_printers()
    
    if not printers:
        print("No Bluetooth printers found.")
        print("\nTroubleshooting:")
        print("1. Make sure your Netum printer is powered on")
        print("2. Pair the printer with Windows Bluetooth settings")
        print("3. Ensure the printer is connected (not just paired)")
        return []
    
    for i, printer in enumerate(printers, 1):
        print(f"{i}. Port: {printer['port']}")
        print(f"   Description: {printer['description']}")
        if printer['bt_address']:
            print(f"   Bluetooth Address: {printer['bt_address']}")
        print()
    
    return printers


def test_connection() -> bool:
    """Test basic printer connection and functionality"""
    print("=== Netum Printer Connection Test ===")
    
    # List available printers first
    printers = list_available_printers()
    
    # Test with auto-discovery
    with NetumPrinter() as printer:
        if not printer.is_connected:
            print("Failed to connect to printer")
            return False
            
        # Test basic printing
        printer.print_line("=== Connection Test ===")
        printer.print_line(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        printer.print_line("Printer: Netum Bluetooth")
        printer.print_line("Status: Connected successfully!")
        printer.feed_lines(3)
        
        print("Test print sent successfully")
        return True


if __name__ == "__main__":
    test_connection()