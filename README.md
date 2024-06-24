# Python Laboratory Hardware Abstraction Layer, Py-Lab-HAL

Py-Lab-HAL is a multi-platform Python library for Lab Test Equipment Control
and Automation. It has been run and tested under Windows, Linux, and Mac.

We support some common and uncommon lab test equipment:
* DC Power Supply
* Battery Emulator
* DMM
* Electronic Load
* Function Generator
* Light Panel
* Power Meter
* Generic USB Relay
* Remote Power Switch
* Oscilloscope
* SMU
* Spectroradiometer
* Stepper Motor
* Temperature Chamber
* Robot Arm

Py-Lab-HAL also supports multiple equipment interfaces:
* Serial
* VXI-11
* USB
* Socket
* HiSLIP (Coming Soon...)

## Requirements

1. OS: Windows, Mac, or Linux
1. Python 3.9+
2. NI-VISA if running on Windows
   1. [Download Here](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html)

## Installation
We currently only offer installing from GitHub. PyPi install coming soon!
``` shell
git clone https://github.com/google/py-lab-hal.git
cd py-lab-hal
pip install .
```
For linux users, you will have to run an extra step:

`echo "SUBSYSTEM==\"usb\", MODE=\"0666\", GROUP=\"usbusers\"" | sudo tee -a /etc/udev/rules.d/99-usbusers.rules`

to configure your USB device access or you won't be able to see instruments over
an USB connection. You might have to restart the computer after entering the
command.

## Getting Started
Let's get our basic imports out of the way:

```python
from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface
```
The `builder` helps us build the instrument while `cominterface` defines the
communication interface in which the host/test computer will use to talk to the
test equipment.

## Creating the Builder
Creating the `builder` is a simple one-liner:

```
build = builder.PyLabHALBuilder()
```
## Configuring the cominterface
Since Py-Lab-HAL is supporting various interfaces, there are quite a lot of
parameters to set up across each interface. For details, check out the source.

To see what is connected to your system and their resource data, you can use our
built-in utility in a terminal:
```shell
python3 -m py_lab_hal.scan
```
This will scan and list out all the visa_resources available to your system.

### Configuring USB and VXI-11
An USB or VXI-11 connection is straight-forward,
just fill in the `visa_resource` you need
:
```python
build.connection_config = cominterface.ConnectConfig(
    visa_resource='USB0::10893::769::MY59006118::0::INSTR',
)
```
### Configuring Socket
For Socket connections, you will need to know the
`socket_host` and `socket_port` of your instrument. This will be filled into
an addition config, `NetworkConfig`, which you can define separately, or
in-line as we have done here:
```python
build.connection_config = cominterface.ConnectConfig(
    network=cominterface.NetworkConfig(
        host='192.168.11.11',
        port=5025,
    ),
)
```
### Configuring Serial
Setting up serial connection is the most involved as it contains
the most parameters. As in socket, you will need to fill out an addition config,
`SerialConfig`. If you are using all default values, then you can just pass in
`SerialConfig` as is, if not, you will need to set it up. The parameters and
their defaults are as follows:
* Baud Rate
  * Default = 9600
```python
cominterface.SerialConfig(baud_rate = 9600)
```
* Data Bits
  * Default = 8
```python
cominterface.SerialConfig(data_bits = 8)
```
* Stop Bits
  * Default = 1 or `cominterface.StopBits.ONE`
  * Select from:
```python
cominterface.StopBits.ONE
cominterface.StopBits.ONE_POINT_FIVE
cominterface.StopBits.TWO

#Usage
cominterface.SerialConfig(stop_bits = cominterface.StopBits.ONE)
```
* Parity
  * Default = 'N' or `cominterface.Parity.NONE`
  * Select from:
```python
cominterface.Parity.EVEN
cominterface.Parity.NONE
cominterface.Parity.SPACE
cominterface.Parity.MARK
cominterface.Parity.ODD

#Usage
cominterface.SerialConfig(parity = cominterface.Parity.NONE)
```
* Flow Control
  * Default = 0 or 'cominterface.ControlFlow.NONE'
  * Select from:
```python
cominterface.ControlFlow.DTR_DSR
cominterface.ControlFlow.RST_CTS
cominterface.ControlFlow.NONE
cominterface.ControlFlow.XON_XOFF

#Usage
cominterface.SerialConfig(flow_control = cominterface.ControlFlow.RST_CTS)
```
A small example of overriding some of the default values when setting up
`SerialConfig`:
```python
build.connection_config = cominterface.ConnectConfig(
    visa_resource='ASRL/dev/ttyUSB0::INSTR',
    serial_config=cominterface.SerialConfig(
        baud_rate=115200,
        flow_control=cominterface.ControlFlow.RST_CTS,
    ),
)
```
## Build the Instrument Object
Now that the builder has been instantiated and cominterface setup, it is time to
build and instantiate the actual instrument!

But first we need to make sure our initalization call to the instrument is
set up correctly:
### Instrument Config
The instrument configuration and their defaults are listed below:
```python
build.instrument_config.reset = True
build.instrument_config.clear = True
build.instrument_config.idn = True
build.instrument_config.auto_init = True
```
`reset`, `clear`, and `idn` are standard VISA SCPI commands, while `auto_init`
is a Py-Lab-HAL command. The first 3 commands and their SCPI equivalents are as
follows:
* `reset` = `*RST`
* `clear` = `*CLR`
* `idn` = `*IDN?`

`auto_init` determines whether to open a connection to the instrument after
builder instantiates the object. If you select false, you will have to issue a
separate call to open a connection to the instrument.


> Note: reset, clear, and idn only applies to VISA SCPI instruments.
> For non-VISA
instruments, all 3 of these flags must be set to False or you will get an error
with the instrument. A few examples of a non-VISA instrument would be:
robot arm, panel light, temp chamber, and generic USB relay.

### Build Instrument
To finish building the instrument, we will invoke the `build_instrument`
function:
```python
build.build_instrument(builder.FOLDER_NAME.MODULE_NAME)
```
Where:
* `FOLDER_NAME` = The type of equipment, e.g., DMM, DC Power Supply, etc.
* `MODULE_NAME` = The module or model name of the instrument, e.g., Keysight,
Tektronix, Lecroy, etc. The `MODULE_NAME` follows the convention of
* `MAKER`_`MODEL`, for example: `KEYSIGHT_N6705C` in all caps.

Usage:
```python
dcpsu = build.build_instrument(builder.DCPowerSupply.KEYSIGHT_N6705C)
dmm = build.build_instrument(builder.DMM.AGILENT_34465A)
```
For details on putting it all together, see the example below and
our demo folder for more examples.

## Example

```python
import time
from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface

build = builder.PyLabHALBuilder()

build.connection_config = cominterface.ConnectConfig(
  visa_resource='USB0::10893::769::MY59006118::0::INSTR',
)
dmm = build.build_instrument(builder.DMM.AGILENT_34465A)

build.connection_config = cominterface.ConnectConfig(
  visa_resource='ASRL/dev/ttyUSB0::INSTR',
  serial_config=cominterface.SerialConfig()
)
dcpsu = build.build_instrument(builder.DCPowerSupply.GWIN_PST3202)

try:
  dcpsu.set_output(1, 5, 1)
  dcpsu.enable_output(1, True)
  print('output 5 V')
  time.sleep(1)
  for i in range(5):
    print(dmm.read())

  dcpsu.set_output(1, 6, 1)
  dcpsu.enable_output(1, True)
  print('output 6 V')
  time.sleep(1)
  for i in range(5):
    print(dmm.read())

finally:
  dmm.close()
  dcpsu.close()
```

## Disclaimer
This is not an official Google product.
