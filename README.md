[![License](https://img.shields.io/github/license/pytransitions/transitions.svg)](LICENSE)
<!-- [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat-square)](https://github.com/pre-commit/pre-commit)
[![code style: black](https://img.shields.io/static/v1?label=code%20style&message=black&color=black&style=flat-square)](https://github.com/psf/black)-->

# pi_mav_control
Easy to control RaspberryPi on UAV in your laptop base on pymavlink frameowrk.

## supports

- Ardupilot
- PX4

## requires

- mavproxy
- hashids
- UAV or SITL

## Usage

Use ctl module to control UAV.
```Python
from ctl import control
```

Connect to uav by serial or udp.
```bash
-> connect [serial/udp] [device/host] [baud/port]
```

Arm the throttle.(--isarm=[0:disarm/1:arm] 
```bash
-> arm [--isarm=1]
```

Takeoff the UAV for spec height.
```bash
-> takeoff [height]
```

Checkout current use mode.
```bash
-> mode 
```

Change current mode use setmode.
```bash
-> setmode [STABILIZE|LAND|RTL|GUIDED|LOITER...etc]
```

Make UAV movement in local coordinate.
```bash
-> move [north/south] [east/west] [up/down]
```
