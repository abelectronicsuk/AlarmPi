#!/usr/bin/env python3
# set a wakeup time on Alarm Pi board from AB Electronics UK when Raspberry Pi is connected to reset pin
# www.abelectronics.co.uk
# uses quick2wire from http://quick2wire.com/ github: https://github.com/quick2wire/quick2wire-python-api
# Requries Python 3 
# GPIO API depends on Quick2Wire GPIO Admin. To install Quick2Wire GPIO Admin, follow instructions at http://github.com/quick2wire/quick2wire-gpio-admin
# I2C API depends on I2C support in the kernel

# Version 1.0  - 26/04/2013
# Version History:
# 1.0 - Initial Release
# 

import quick2wire.i2c as i2c

import time
import sys, math, struct

rtc_address1 = 0x51

with i2c.I2CMaster(1) as bus:
	
	# general functions for conversion
	def fromBCDtoDecimal(x):
		return x - 6 * (x >> 4)
		#return (newvalue /16 * 10) + (newvalue%16)
	def decToBcd(x):
		bcdstring = ''
		if x < 10:
			bcdstring = '0000'
		for i in str(x):
			bcdstring += bcddigit(i)
		return int(bcdstring,2)
		return hex(int(bcdstring,2))
		
	def bcddigit(sn):
		n = int(sn)
		bin_nr = bin(n)[2:]
		return ('0000' + bin_nr)[-4:]
				
	def bin2bcd(x):
		return x + 6 * (x /10)
	# end general functions for conversion	
	
	def initClock():
		# reset all clock values to factory default
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x0, 0x0, 0x0, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x80, 0x80, 0x80, 0x80, 0x0, 0x0))			

	def setClkOutput():
		# enable clock output on CLKOUT at 32.768 kHz
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x0D, 0x80))
		
		
	def clearClkOutput():
		# reset clock output 
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x0, 0x0, 0x0))
		
	def clearStatus():
		#reset status bytes
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x0D, 0x80))
		
	def getDate():
		# get date and return value
		
		#get day
		day, day2 = bus.transaction(
			i2c.writing_bytes(rtc_address1, 0x05),
			i2c.reading(rtc_address1,2))[0]
		timeday1 = ((day >> 4) & 0x03)
		timeday2 = (day & 0x0F)
		
		#get month
		month, month2 = bus.transaction(
			i2c.writing_bytes(rtc_address1, 0x07),
			i2c.reading(rtc_address1,2))[0]
		timemonth1 = ((month >> 4) & 0x01)
		timemonth2 = (month & 0x0F)
		
		#get year
		year, year2 = bus.transaction(
			i2c.writing_bytes(rtc_address1, 0x08),
			i2c.reading(rtc_address1,2))[0]
		timeyear1 = ((year >> 4))
		timeyear2 = (year & 0x0F)

		return str(timeday1) + str(timeday2) + "/" + str(timemonth1) + str(timemonth2) + "/" + str(timeyear1) + str(timeyear2)
		
	def getTime():
		#get time and return value
		# get seconds	
		seconds, seconds2 = bus.transaction(
			i2c.writing_bytes(rtc_address1, 0x02),
			i2c.reading(rtc_address1,2))[0]
		timeseconds1 = ((seconds >> 4) & 0x07)
		timeseconds2 = (seconds & 0x0F)
		#get minute
		minute, minute2 = bus.transaction(
			i2c.writing_bytes(rtc_address1, 0x03),
			i2c.reading(rtc_address1,2))[0]
		timeminute1 = ((minute >> 4) & 0x07)
		timeminute2 = (minute & 0x0F)
		#get hour
		hour, hour2 = bus.transaction(
			i2c.writing_bytes(rtc_address1, 0x04),
			i2c.reading(rtc_address1,2))[0]
		timehour1 = ((hour >> 4) & 0x03)
		timehour2 = (hour & 0x0F)
		return str(timehour1) + str(timehour2) + ":" + str(timeminute1) + str(timeminute2) + ":" + str(timeseconds1) + str(timeseconds2)
		
	def setDate(day, weekday, month, century, year):
		# set the date to the clock
		# year is 00-99
		# high bit of month = century
		# 0 = 20xx
		# 1 = 19xx
		savemonth = decToBcd(month)
		if (century == 1):
			savemonth |= 0x80
		else:
			savemonth &= ~0x80
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x05, 
		decToBcd(day), decToBcd(weekday), savemonth, decToBcd(year)))	
		
		
	def setTime(hour, minute, second):
		# set the time to the clock
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x02, 
		decToBcd(second), decToBcd(minute), decToBcd(hour)))
		
		
	def setAlarm(minuite, hour, day, weekday):
		# set alarm data to clock
		enableAlarm()
		
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x09, 
		decToBcd(minuite), decToBcd(hour), decToBcd(day), decToBcd(weekday)))
		
	def enableAlarm():
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x01, 0x02))
		
	
	def clearAlarm():
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x0D, 0x80))
		
	def resetAlarm():
		# clear alarm flag leaving interupt unchanged
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x01, 0x00))
		#bus.transaction(i2c.writing_bytes(rtc_address1, 0x01, 0x08))
			
	def readAlarm():
		alarmstatus, status22 = bus.transaction(
			i2c.writing_bytes(rtc_address1, 0x01),
			i2c.reading(rtc_address1,2))[0]
		return alarmstatus
		
	# now we start communication with the clock and enable clock pin out and alarm									
	initClock()
	setClkOutput()
	enableAlarm()
	# set time at 22:50:00
	setTime(22,59,58)
	
	# set the date to be 17th April 2013, 3rd weekday
	setDate(17, 3, 4, 1, 13)
	
	# set the alarm to wake the Raspberry Pi in 10 minutes.
	# run sudo shutdown -h now to halt the raspberry pi after running this script.
	setAlarm(0, 23, 17, 3)

	
	while True:
		
		
		print(getDate())
		print(getTime())
		print(readAlarm() )
		if (readAlarm() == 66):
			print ("not active")
		if (readAlarm() == 10):
			print ("Active")
			clearAlarm()
			resetAlarm()
		if (readAlarm() == 2):
			print ("Reset")
		time.sleep(1)	
