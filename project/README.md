# Installation

  - `sudo apt-get install build-essential binutils-msp430 gcc-msp430 msp430-libc binutils-avr gcc-avr gdb-avr avr-libc avrdude binutils-arm-none-eabi gcc-arm-none-eabi gdb-arm-none-eabi ant libncurses5-dev doxygen srecord git openjdk-11-jdk`

# Instructions

The following make targets are useful for development:

  - `make all`: builds the binary
  - `make deploy`: builds & deploys the binary
  - `make tail`: configures the tty and reads it (abort with Ctrl+C)

To start and check the serial output, use `make deploy tail`.