# meta-node-red - IoT2050 Node-RED Layer

## Overview

The `meta-node-red` layer provides Node-RED support for the IoT2050 platform. Node-RED is a flow-based development tool for visual programming of IoT applications.

## Purpose

- **Visual programming** - Flow-based application development
- **Industrial nodes** - Pre-built nodes for industrial protocols
- **Rapid prototyping** - Quick IoT application development
- **Integration platform** - Connect various systems and protocols

## Contents

### Node-RED Runtime
- `recipes-app/node-red/` - Core Node-RED runtime
- IoT2050-specific configuration and flows
- Pre-installed industrial nodes

### Industrial Nodes
- **OPC-UA nodes** - Connect to OPC-UA servers
- **Modbus nodes** - Modbus TCP/RTU communication
- **S7 nodes** - Siemens PLC integration
- **GPIO nodes** - Direct hardware control
- **Dashboard nodes** - Web-based UI components

## Key Features

- 🎨 **Visual Programming** - Drag-and-drop flow creation
- 🏭 **Industrial Protocols** - Built-in protocol support
- 📊 **Dashboard** - Real-time web dashboards
- 🔌 **GPIO Access** - Direct hardware I/O control
- 🌐 **Web Interface** - Browser-based development
- 📦 **Node Palette** - Extensive library of nodes

## Pre-installed Nodes

| Node Package | Purpose |
|--------------|---------|
| node-red | Core Node-RED runtime |
| node-red-contrib-opcua | OPC-UA communication |
| node-red-contrib-modbus | Modbus protocol support |
| node-red-contrib-s7 | Siemens S7 PLC integration |
| node-red-dashboard | Web dashboard creation |
| node-red-gpio | Hardware GPIO control |
| node-red-node-serialport | Serial port communication |
| node-red-node-sqlite | SQLite database nodes |
| node-red-node-random | Random number generation |
| mindconnect-node-red-contrib-mindconnect | MindConnect IoT platform |

## Industrial Applications

1. **Data Collection** - Gather data from industrial devices
2. **Protocol Translation** - Convert between different protocols
3. **Edge Processing** - Process data at the edge
4. **Dashboard Creation** - Real-time monitoring interfaces
5. **Automation Logic** - Simple control applications
6. **IoT Gateway** - Connect industrial systems to cloud

## Getting Started

### Access Node-RED
1. Open browser to `http://iot2050-ip:1880`
2. Start creating flows by dragging nodes
3. Deploy flows to activate them

### Basic Flow Example
```
[Inject] → [Function] → [Debug]
```

### Industrial Flow Example
```
[OPC-UA] → [Process Data] → [MQTT Out] → [Dashboard]
```

## Configuration

### Node-RED Settings
- **Configuration file**: `/etc/node-red/settings.js`
- **Flow storage**: `/var/lib/node-red/flows.json`
- **User directory**: `/var/lib/node-red/`

### Security
- Authentication can be enabled in settings.js
- HTTPS support available
- Access control for flows and dashboard

## Dependencies

- **meta-iot2050-bsp** - Base hardware support
- **Node.js runtime** - JavaScript execution environment
- **npm packages** - Additional Node-RED nodes

## Build

```bash
kas build kas/iot2050-example.yml  # Includes Node-RED
```

## Development Workflow

1. **Design flows** in Node-RED editor
2. **Test locally** on IoT2050 device
3. **Export flows** for version control
4. **Deploy to production** systems

## Troubleshooting

### Check Node-RED Status
```bash
systemctl status node-red
```

### View Logs
```bash
journalctl -u node-red -f
```

### Restart Service
```bash
systemctl restart node-red
```

## Maintainers

See top-level `MAINTAINERS` file in the repository root.

## License

MIT License - See COPYING.MIT in repository root.