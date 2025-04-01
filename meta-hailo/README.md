# meta-hailo - Support for HAILO NPU chips

This layer provides recipes to build the kernel and userspace drivers 
and utilities (version 4.18) for the Hailo-8 NPU chip. It also supports 
GStreamer and tappas. The main components included are:

- hailo-pci (OSS kernel module)
- hailo-firmware (proprietary firmware for hailo8 chip)
- hailort (Userspace API)
  - hailortcli (tool)
  - hailort (service)
  - libhailort (c library)
  - libhailort-dev (dev package)
  - python3-hailort (python library)
  - HailoRT GStreamer library (HailoNet element)
- tappas (Framework for optimized execution of video-processing pipelines)

> Note: `numpy==1.23.3` is preinstalled. Please do not upgrade it, as
> `hailort v4.18.0` requires this specific version. Upgrading `numpy` may 
> cause `pyhailort` to fail to execute.

The following configurations are supported and recommended for achieving optimal
performance with the Hailo8 AI Card:

- IoT2050 SM with Hailo-8™ mPCIe or Hailo-8™M.2 B+M
- IoT2050 Advanced with Hailo-8™ mPCIe and heatsink

For more information about Hailo, please refer to the 
[Hailo website](https://hailo.ai/) and the 
[Hailo Open Source repository](https://github.com/hailo-ai).

## How to Have a Quick Practice?

You can find Hailo application examples at the [Hailo Application Code Examples](https://github.com/hailo-ai/Hailo-Application-Code-Examples/tree/main/runtime):
- C++
- GStreamer
- Python (It is strongly recommended to use a [Python virtual environment](https://docs.python.org/3/library/venv.html)
to avoid dependency issues)
  - Install venv: `apt-get update && apt-get install python3-venv`
  - Create a venv: `python3 -m venv --system-site-packages path/to/venv`
  - Activate the venv: `source path/to/venv/bin/activate`
  - Install dependencies: `pip install -r requirements.txt`
> Note:
> 1. Do not re-install newer `numpy` package in venv to overwrite the
> preinstalled `numpy==1.23.3`. If `numpy` in `requirements.txt` is not
> `numpy==1.23.3`, please modify it to `1.23.3` or remove it, since it is
> already preinstalled.
> 2. The examples are continuously updated and may not always be compatible 
> with our current Hailo version. If you encounter any problems with the latest 
> examples, please try using an older version of the examples.
> 3. The examples provided are not officially supported by Hailo, solely on  
> an “AS IS” basis and “with all faults”. They may not offer an optimal  
> experience on our platform. Please use them as references to learn how  
> to use Hailo and develop your own AI applications.

Additionally, we have integrated three Tappas (GStreamer) demos to provide
users with a hands-on experience or quick practice. For more details, please
refer to the [Tappas README](recipes-app/tappas/README.md).
 - Detection Pipeline
 - License Plate Recognition
 - Multi-Stream Object Detection

## Versioning

This layer is versioned according to the major hailo driver version.
Note, that the kernel ABI is not stable and by that the version of the
userspace components need to perfectly match the version of the firmware
and the kernel module.
