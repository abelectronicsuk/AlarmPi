AlarmPi
=======

Demo files for Alarm Pi board from AB Electronics UK


run the following commands to setup the module

sudo modprobe i2c-dev
sudo modprobe rtc-pcf8563


The RTC Pi requires a Linux kernel with i2c drivers such as the Occidentalis system image from http://learn.adafruit.com/adafruit-raspberry-pi-educational-linux-distro/overview which has i2c enabled.

To access the Alarm Pi from your Raspberry Pi:

Boot the Pi from that image and execute these commands as root / su user:

First you need to register the DS1307 RTC chip with the I2C address of 0x51:

For Revision One boards use:

sudo su -

sudo echo pcf8563 0x51 > /sys/class/i2c-adapter/i2c-0/new_device

For Revision Two boards use:

sudo su -

sudo echo pcf8563 0x51 > /sys/class/i2c-adapter/i2c-1/new_device

To set the RTC Pi clock with the current system time:

hwclock --systohc

View the current date and time stored in the RTC Pi:

hwclock -r

Set the Linux system time to the value in the RTC Pi:

hwclock –s

To set the Alarm Pi with a custom time:

hwclock --set --date="2012-12-25 06:00:12"  --utc

To create the Alarm Pi device creation at boot edit /etc/rc.local by running

    sudo nano /etc/rc.local

and add:

    echo pcf8563 0x51 > /sys/class/i2c-adapter/i2c-0/new_device (for v1 raspberry pi)
    echo pcf8563 0x51 > /sys/class/i2c-adapter/i2c-1/new_device (v2 raspberry pi)
    sudo hwclock -s (both versions)

before exit 0

Save your changes and then reboot the Raspberry Pi, the Alarm Pi board will then be detected when the Pi boots and set the time from the clock module.

Further instructions for using the PCF8563 Real Time Clock with C code samples are available on http://www.susa.net/wordpress/2012/06/raspberry-pi-pcf8563-real-time-clock-rtc/