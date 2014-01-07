AlarmPi
=======

Demo files for Alarm Pi board from AB Electronics UK


run the following commands to setup the module

modprobe i2c-dev

modprobe rtc-pcf8563

echo pcf8563 0x51 > /sys/class/i2c-adapter/i2c-0/new_device



Further instructions for using the PCF8563 Real Time Clock with C code samples are available on http://www.susa.net/wordpress/2012/06/raspberry-pi-pcf8563-real-time-clock-rtc/