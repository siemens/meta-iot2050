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
| `node-red-dashboard-flowfuse` (`@flowfuse/node-red-dashboard`) | Maintained Dashboard 2.0 |
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
1. Sign in to Cockpit at `https://<IOT2050_IP>/` and enable Administrative access.
2. In **Device Admin**, set the independent Node-RED access password (and
   optionally change the HTTPS port from the default `1880`). The same username
   is selected by default; the system password is not reused.
3. Start Node-RED and use the editor link at `https://<IOT2050_IP>:<PORT>/admin/`
   (default `1880`). The configured port requires HTTPS; the backend is
   loopback-only on port 1881.
4. Create and deploy flows. No business flows or Dashboard pages are deployed
   by the image. Configure Dashboard 2.0 pages under the protected `/http/`
   runtime root. Legacy Dashboard 1.x flows are not automatically migrated.

Remote access also requires an explicit source/interface-scoped firewall policy.
Do not open the configured Node-RED port on a shared public zone exposing other
network interfaces.
Palette installation and external module auto-install are disabled in the
managed profile; add reviewed nodes through image recipes.

The legacy `node-red-dashboard` recipe remains available for explicitly chosen
compatibility builds but is no longer a dependency of the default node set.

### Maintainers

See the top-level `MAINTAINERS` file in the repository root.

### License

MIT License - See `COPYING.MIT` in the repository root.
