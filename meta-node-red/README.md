# meta-node-red - IoT2050 Node-RED Layer

## Overview

The `meta-node-red` layer provides support for Node-RED, a flow-based
development tool for visual programming of IoT applications, on the IoT2050
platform.

## Pre-installed Nodes

The following Node-RED packages are pre-installed:

| Node Package | Purpose |
|--------------|---------|
| `node-red` | Core Node-RED runtime |
| `node-red-contrib-opcua` | OPC-UA communication |
| `node-red-contrib-modbus` | Modbus protocol support |
| `node-red-contrib-s7` | Siemens S7 PLC integration |
| `node-red-dashboard` | Web dashboard creation |
| `node-red-gpio` | Hardware GPIO control |
| `node-red-node-serialport` | Serial port communication |
| `node-red-node-sqlite` | SQLite database nodes |
| `node-red-node-random` | Random number generation |
| `mindconnect-node-red-contrib-mindconnect` | MindConnect IoT platform integration |

## Getting Started

### Build
Node-RED is included in the example image by default:
```sh
./kas-container build kas-iot2050-example.yml
```

### Access Node-RED
1. Open a web browser and navigate to `http://<IOT2050_IP>:1880`. The default
   port for Node-RED is **1880**.
2. Start creating flows by dragging nodes from the palette.
3. Click the **Deploy** button to activate your flows.

### Maintainers

See the top-level `MAINTAINERS` file in the repository root.

### License

MIT License - See `COPYING.MIT` in the repository root.