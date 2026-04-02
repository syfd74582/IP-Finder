
# IP-Finder
IP Finder – A GUI tool to discover any network device (IP cameras, routers, etc.) regardless of its IP range. Uses ARP sniffing/scanning, displays MAC vendor, device type, open ports, and exports results to CSV.

# 🔍 IP Finder - Network Device Discovery Tool

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg)]()

> A professional GUI tool to discover any network device (IP cameras, routers, IoT devices) regardless of its IP range.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **Auto Discovery** | Detects devices without needing to know the IP range in advance |
| 📡 **Two Detection Modes** | Passive Sniffer + Active ARP Scan |
| 🏭 **Vendor Recognition** | Extracts manufacturer from MAC address (OUI database) |
| 🖥️ **Device Type Detection** | Distinguishes between IP cameras, routers, printers, servers |
| 🔌 **Port Scanning** | Shows open ports (HTTP, RTSP, SSH, and more) |
| 💾 **Save Results** | Export results to CSV file |
| 🌐 **Arabic Interface** | User-friendly GUI built with Tkinter |

## 🚀 Usage Guide

### Prerequisites
- Windows / Linux operating system
- Python 3.8 or higher
- Administrator privileges (for sniffer mode)

### Installation & Execution

```bash
# 1. Clone the repository
git clone https://github.com/syfd74582/IP-Finder.git
cd IP-Finder

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the program
python ip_finder.py
```

> **Important Note:** On Windows, it's recommended to run the program as Administrator to ensure the passive sniffer works correctly.

## 🖥️ Screenshot

```
┌─────────────────────────────────────────────────────────────────┐
│  🔍 IP Finder - Network Device Discovery                ─ □ × │
├─────────────────────────────────────────────────────────────────┤
│  Network Interface: [Ethernet (192.168.1.100)          ▼] [Refresh] │
│                                                                  │
│  [▶ Start Discovery] [🔄 Restart]            Status: ✓ Ready    │
│                                                                  │
│  ════════════════════════════════════════════════════════════   │
│  │ IP           │ MAC               │ Vendor        │ Type     │  │
│  │ 192.168.1.1  │ 00:1C:9E:XX:XX:XX │ Hikvision     │ Camera   │  │
│  │ 192.168.1.2  │ 70:56:81:XX:XX:XX │ TP-Link       │ Router   │  │
│  │ 192.168.1.5  │ 00:15:5D:XX:XX:XX │ Microsoft     │ Generic  │  │
│  ════════════════════════════════════════════════════════════   │
│                                                                  │
│  [💾 Save CSV] [🗑 Clear] [📋 Details]                           │
│                                                                  │
│  [Event Log]                                                    │
│  [14:30:01] Starting discovery on interface: Ethernet           │
│  [14:30:15] New device: 192.168.1.1 (Hikvision) - Camera       │
└─────────────────────────────────────────────────────────────────┘
```

## 🖥️ Screenshot

<div align="center">
  <img src="ip_find.png" alt="Application Interface" width="100%">
</div>

## 📊 Manufacturer Database (OUI)

The program recognizes over 50 manufacturers, including:

| Manufacturer | Type |
|--------------|------|
| Hikvision | Surveillance Cameras |
| Dahua | Surveillance Cameras |
| TP-Link | Routers, Network Switches |
| Cisco | Professional Network Devices |
| Ubiquiti | Wireless Access Points |
| Apple | Apple Devices |
| Samsung | Various Devices |
| Netgear | Network Devices |
| MikroTik | Network Devices |
| Axis Communications | IP Cameras |

## 🔧 Project Structure

```
IP-Finder/
├── ip_finder.py          # Main program file
├── requirements.txt      # Required dependencies
├── README.md             # Project documentation
├── LICENSE               # MIT License
└── .gitignore            # Git ignored files
```

## 📝 Dependencies

```txt
scapy>=2.4.5    # For network packet handling (ARP, Sniffer)
```

> **Note:** The program does not depend on `netifaces` to avoid Windows compatibility issues.

## 🤝 Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing`)
3. Make your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📧 Contact

- **Developer:** syfd74582
- **Email:** [alqyadydnan@gmail.com]
- **GitHub:** [github.com/syfd74582](https://github.com/syfd74582)

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with ❤️ by Adnan Alqyady</sub>
</div>
```


