# NetworkPulse

### IONIC Health Network Analysis Tool

## Description
NetworkPulse is a comprehensive network analysis tool developed for IONIC Health's remote medical equipment monitoring system. It provides real-time analysis and visualization of network characteristics crucial for medical imaging equipment like MRI and CT scanners.

## Project Structure
```
networkpulse/
├── main.py              # Application entry point
├── network_utils.py     # Network utility functions
├── network_analyzer.py  # Network analysis logic
├── gui.py              # GUI implementation
├── requirements.txt    # Project dependencies
└── README.md          # Project documentation
```

## Features
- 🔍 Advanced NAT Configuration Detection
- 📡 DNS Server Analysis and Response Time Measurement
- 🌐 ISP Information and Network Path Analysis
- 🔐 Internal Network Properties Monitoring
- 📊 Network Performance Metrics
- 🚀 Real-time Speed Testing
- 🖥️ Modern, Panel-based GUI Interface
- 🔄 Individual Section Refresh Capability

## Requirements
```
python >= 3.8
dnspython >= 2.4.2
requests >= 2.31.0
netifaces >= 0.11.0
speedtest-cli >= 2.1.3
stun >= 1.1.1
tkinter (usually comes with Python)
```

## Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/NetworkPulse.git
cd NetworkPulse
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
Run the application:
```bash
python main.py
```

The GUI will open with six panels showing different aspects of network analysis:
1. NAT Configuration
2. DNS Servers
3. ISP Information
4. Internal Network Properties
5. External Connectivity
6. Network Performance

Each panel has its own "Update" button to refresh that specific information. There's also a global "Update All" button to refresh everything at once.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## About IONIC Health
IONIC Health is a Brazilian healthcare technology company specializing in automation and innovation in diagnostic medicine. Founded in 2019, the company leverages advanced technologies like AI to remotely monitor, automate, and support medical equipment, improving healthcare efficiency and quality.

## License
MIT License

## Authors
Created for IONIC Health's Future Professional Challenge
