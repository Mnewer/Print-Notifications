# Netum Bluetooth Printer

Easy-to-use Python library for Netum Bluetooth thermal printers (NT-1809D and compatible models).

## Features

- ✅ **Auto-discovery** - Automatically finds your Netum printer
- ✅ **Simple API** - Clean, easy-to-use interface
- ✅ **Cross-platform** - Works on Windows, Mac, Linux
- ✅ **No drivers needed** - Uses standard Bluetooth serial connection
- ✅ **Multiple printers** - Support for multiple connected printers

## Quick Start

### 1. Install Requirements
```bash
pip install pyserial
```

### 2. Setup Your Printer
1. Turn on your Netum printer
2. Pair it with your computer via Bluetooth settings
3. Make sure it's connected (not just paired)

### 3. Test Connection
```bash
python netum_printer.py
```

### 4. Start Coding
```bash
python main.py
```

## Usage Examples

### Auto-Discovery (Recommended)
```python
from netum_printer import NetumPrinter

# Automatically finds and connects to your Netum printer
with NetumPrinter() as printer:
    if printer.is_connected:
        printer.print_line("Hello World!")
        printer.feed_lines(2)
```

### Manual Port Specification
```python
from netum_printer import NetumPrinter

# Connect to specific COM port
with NetumPrinter(port="COM8") as printer:
    if printer.is_connected:
        printer.print_line("Hello from COM8!")
        printer.feed_lines(2)
```

### List Available Printers
```python
from netum_printer import list_available_printers

printers = list_available_printers()
# Shows all detected Netum printers with their ports and Bluetooth addresses
```

### Receipt-Style Printing
```python
from netum_printer import NetumPrinter

with NetumPrinter() as printer:
    if printer.is_connected:
        printer.print_line("=" * 32)
        printer.print_line("        SAMPLE RECEIPT")
        printer.print_line("=" * 32)
        printer.print_line("")
        printer.print_line("Item 1........................$10.00")
        printer.print_line("Item 2........................$15.50")
        printer.print_line("-" * 32)
        printer.print_line("Total.........................$25.50")
        printer.print_line("=" * 32)
        printer.feed_lines(3)
```

## API Reference

### NetumPrinter Class

#### Constructor
```python
NetumPrinter(port=None, baudrate=9600, auto_discover=True)
```
- `port`: Specific COM port (e.g., "COM8") or None for auto-discovery
- `baudrate`: Connection speed (default: 9600)
- `auto_discover`: Automatically find the first available printer

#### Methods
- `connect()` - Connect to printer (returns True/False)
- `disconnect()` - Disconnect from printer
- `print_text(text)` - Print raw text or bytes
- `print_line(text)` - Print text with newline
- `feed_lines(count)` - Print blank lines for spacing

#### Context Manager
```python
with NetumPrinter() as printer:
    # Automatically connects and disconnects
    if printer.is_connected:
        printer.print_line("Hello!")
```

### Utility Functions
- `discover_netum_printers()` - Returns list of available printers
- `list_available_printers()` - Prints and returns available printers

## Troubleshooting

### No Printers Found
1. Make sure your Netum printer is powered on
2. Check Windows Bluetooth settings - printer should be "Paired" AND "Connected"
3. Try unpairing and re-pairing the printer
4. Restart the printer and try again

### Connection Failed
1. Close any other applications using the printer
2. Make sure the printer isn't in use by Windows print spooler
3. Try a different COM port if multiple are available
4. Check if the printer needs to be "connected" in Bluetooth settings

### Print Issues
1. Make sure paper is loaded correctly
2. Check if printer needs charging
3. Try feeding some paper manually to test printer hardware

## Compatible Printers

This library has been tested with:
- Netum NT-1809D
- Other Netum Bluetooth thermal printers should work

## Project Structure

```
├── netum_printer.py    # Core printer interface module
├── main.py            # Development/testing script
└── README.md          # This documentation
```