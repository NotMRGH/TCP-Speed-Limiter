# Async TCP Proxy with Per-IP Speed Limit

This Python script creates a simple **TCP proxy** that forwards traffic from an input port to an output port. It includes per-IP rate limiting, ensuring that each client can only use a specified amount of bandwidth while allowing unlimited total connections.

## Features
- **TCP traffic forwarding**: Redirects traffic from an input port to an output port.
- **Per-IP speed limit**: Restricts each client to a user-defined bandwidth (e.g., 8 Mbps per client).
- **Unlimited connections**: No limit on the total number of clients.
- **Fully asynchronous**: Uses `asyncio` for efficient non-blocking performance.
- **Error handling**: Prevents unnecessary console error logs.

## Requirements
- Python 3.8 or newer

## Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/NotMRGH/TCP-Speed-Limiter.git
   cd TCP-Speed-Limiter
   ```

2. **(Optional) Create a virtual environment:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies (if required):**
   The script does not require external dependencies beyond Python’s standard library.

## Usage
1. Run the script:
   ```sh
   python3 proxy.py
   ```
   
2. Enter the required settings when prompted:
   ```
   Enter input port: 9429
   Enter output port: 30324
   Enter speed limit in Mbps: 8
   ```

3. The proxy will start running and display:
   ```
   Serving on ('0.0.0.0', 9429), Speed Limit: 8 Mbps
   ```

## How It Works
- When a client connects, their traffic is forwarded from the **input port** to the **output port**.
- Each client's **IP address** is monitored to ensure they do not exceed the speed limit.
- The script dynamically adjusts speed limits per second for each client.
- The total speed of all connections is **unlimited**, but each IP gets a fixed bandwidth.

## Example Use Case
This script is useful in scenarios like:
- **Managing proxy traffic** for V2Ray, Shadowsocks, or similar applications.
- **Controlling per-user bandwidth** in a shared network environment.
- **Testing networking applications** with controlled bandwidth.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributions
Contributions are welcome! Feel free to open an issue or submit a pull request.