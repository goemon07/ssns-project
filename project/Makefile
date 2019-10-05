CONTIKI_PROJECT = fubar
TARGET = arduino
ARDUINO_MODEL=Uno
CONTIKI = ..
TTY=/dev/ttyACM0

deploy: all
	avr-objcopy -v -O ihex -R .eeprom -R .fuse fubar.arduino fubar.hex
	avrdude -p m328p -P $(TTY) -c arduino -b 115200 -U flash:w:fubar.hex

tail:
	stty -F $(TTY) cs8 9600 ignbrk -brkint -icrnl -imaxbel -opost -onlcr -isig -icanon -iexten -echo -echoe -echok -echoctl -echoke noflsh -ixon -crtscts
	echo Press ^C to abort
	tail -f $(TTY)

all: $(CONTIKI_PROJECT)

include $(CONTIKI)/Makefile.include
