#!/usr/bin/env python3
#
#-----------------------------------------------------------------------------
# set a wakeup time on AB Electronics PCF8563 board for Raspberry Pi. 
# uses quick2wire see
# https://github.com/quick2wire/quick2wire-python-api
#
# Requries Python 3 
#
# GPIO API depends on Quick2Wire GPIO Admin.
# I2C API depends on I2C support in the kernel
#
# Version 1.00 - 26/04/2013
# Version 2.00 - 18/02/2014
#
# Version History:
#
# 1.00 - Initial Release
# 2.00 - Re-written by M.A. O'Neill <mao@tumblingdice.co.uk>
#---------------------------------------------------------------------------- 

import quick2wire.i2c as i2c
import time
import sys, math, struct


#-------------------------------
# Address of PCF8563 RTC device
#-------------------------------

rtc_address1 = 0x51


#----------------------------
# Use i2c as operational bus
#----------------------------

with i2c.I2CMaster(1) as bus:

#-----------------------------------	
# general functions for conversion
#-----------------------------------

	#---------------------------------------------
	# Binary packed decmal to decimal conversion
	#---------------------------------------------

	def fromBCDtoDecimal(x):
		return x - 6 * (x >> 4)

	#---------------------------------------------
	# Decimal to binary packed decimal conversion
	#---------------------------------------------

	def decToBcd(x):
		bcdstring = ''
		if x < 10:
			bcdstring = '0000'
		for i in str(x):
			bcdstring += bcddigit(i)
		return int(bcdstring,2)

	#----------------
	# Get BCD digit
	#----------------
		
	def bcddigit(sn):
		n = int(sn)
		bin_nr = bin(n)[2:]
		return ('0000' + bin_nr)[-4:]

	#------------------------------------------		
	# Convert binary number to BCD equivalent
	#------------------------------------------
		
	def bin2bcd(x):
		return x + 6 * (x /10)

#---------------------------------------
# end general functions for conversion	
# PCF8563 specific functions follow
#---------------------------------------

	#---------------------------------------------
	# enable clock output on CLKOUT at 32.768 kHz
	#---------------------------------------------
	def setClkOutput():
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x0D, 0x80))
		
	#--------------------		
	# reset clock output 
	#--------------------
	def clearClkOutput():
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x0, 0x0, 0x0))
		

	#--------------------
	# reset status bytes
	#--------------------
	def clearStatus():
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x0D, 0x80))


	#-----------------------------
	# get minute and return value
	#-----------------------------
	def getMinute():

		minute, minute2 = bus.transaction(	i2c.writing_bytes(rtc_address1, 0x03),
							i2c.reading(rtc_address1,2))[0]

		timeminute1 = ((minute >> 4) & 0x07)
		timeminute2 = (minute & 0x0F)

		return int(str(timeminute1) + str(timeminute2))



	#----------------------------
	# get hour and return value
	#----------------------------
	def getHour():

		hour, hour2 = bus.transaction(	i2c.writing_bytes(rtc_address1, 0x04),
						i2c.reading(rtc_address1,2))[0]

		timehour1 = ((hour >> 4) & 0x03)
		timehour2 = (hour & 0x0F)

		return int(str(timehour1) + str(timehour2))


	#--------------------------		
	# get day and return value
	#--------------------------
	def getDay():

		#------		
		# day
		#------
		day, day2 = bus.transaction(	i2c.writing_bytes(rtc_address1, 0x05),
						i2c.reading(rtc_address1,2))[0]

		timeday1 = ((day >> 4) & 0x03)
		timeday2 = (day & 0x0F)
	
		return int(str(timeday1) + str(timeday2))


	#----------------------------
	# get month and return value
	#----------------------------
	def getMonth():
		month, month2 = bus.transaction(i2c.writing_bytes(rtc_address1, 0x07),
                                                i2c.reading(rtc_address1,2))[0]

		timemonth1 = ((month >> 4) & 0x01)
		timemonth2 = (month & 0x0F)

		#----------------------
		# Return month by name
		#----------------------
		monthno = int(str(timemonth1) + str(timemonth2))

		if monthno == 1:
			monthname = "Jan"
		if monthno == 2:
			monthname = "Feb"
		if monthno == 3:
			monthname = "Mar"
		if monthno == 4:
			monthname = "Apr"
		if monthno == 5:
			monthname = "May"
		if monthno == 6:
			monthname = "Jun"
		if monthno == 7:
			monthname = "Jul"
		if monthno == 8:
			monthname = "Aug"
		if monthno == 9:
			monthname = "Sep"
		if monthno == 10:
			monthname = "Oct"
		if monthno == 11:
			monthname = "Nov"
		if monthno == 12:
			monthname = "Dec"

		#------------------------
		# Return month by number 
		#------------------------
		return monthno, monthname


	#---------------------------		
	# get year and return value 
	#---------------------------
	def getYear():
	
		year, year2 = bus.transaction(	i2c.writing_bytes(rtc_address1, 0x08),
						i2c.reading(rtc_address1,2))[0]

		timeyear1 = ((year >> 4))
		timeyear2 = (year & 0x0F)

		#------------------------
		# We're in 21st Century!
		#------------------------
		return int("20" + str(timeyear1) + str(timeyear2))

		
	#-------------------------------------------------------------
	# Is the PCF8563 device present (note only works between 2001
	# and 2099!
	#-------------------------------------------------------------

	def pcf8563OnI2cBus():
		if getYear() == 0:
			return False

		return True

	
	#-------------------------
	# set alarm data to clock
	#-------------------------
	def setAlarm(minute, hour, day, weekday):
		enableAlarm()

		bus.transaction(i2c.writing_bytes(rtc_address1, 0x09, decToBcd(minute), decToBcd(hour), decToBcd(day), decToBcd(weekday)))


	#-------------------------------
	# Return day of week given date
	#-------------------------------
	def weekDay(year, month, day):


		#---------------------------------------------
		# Sanity check - make sure day given does
		# not exceed the number of days in the month!
		#---------------------------------------------

		if month == 1 and day > 31:
			print("     setalarm ERROR: only 31 days in January")
			print(" ")
			exit()

		if year % 4 == 0:
			if month == 2 and day > 29:
				print("     setalarm ERROR: only 29 days in February")
				print("")
				exit()
		else:
			if month == 2 and day > 28:
				print("     setalarm ERROR: only 28 days in February")
				print(" ")
				exit()

		if month == 3 and day > 31:
			print("     setalarm ERROR: only 31 days in March")
			print(" ")
			exit()

		if month == 4 and day > 30:
			print("     setalarm ERROR: only 30 days in April")
			print(" ")
			exit()

		if month == 5 and day > 31:
			print("     setalarm ERROR: only 31 days in May")
			print(" ")
			exit()

		if month == 6 and day > 30:
			print("     setalarm ERROR: only 30 days in June")
			print(" ")
			exit()

		if month == 7 and day > 31:
			print("     setalarm ERROR: only 31 days in July")
			print(" ")
			exit()

		if month == 8 and day > 31:
			print("     setalarm ERROR: only 31 days in August")
			print(" ")
			exit()

		if month == 9 and day > 30:
			print("     setalarm ERROR: only 30 days in September")
			print(" ")
			exit()

		if month == 10 and day > 31:
			print("     setalarm ERROR: only 31 days in October")
			print(" ")
			exit()

		if month == 11 and day > 30:
			print("     setalarm ERROR: only 30 days in November")
			print(" ")
			exit()

		if month == 12 and day > 31:
			print("     setalarm ERROR: only 31 days in December")
			print(" ")
			exit()


		offset = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]

		week   = {0:'Sun',
			  1:'Mon', 
			  2:'Tue', 
			  3:'Wed', 
			  4:'Thu',  
			  5:'Fri', 
			  6:'Sat'}

		afterFeb = 1
		if month > 2:
			afterFeb = 0

		aux = year - 1700 - afterFeb

		#------------------------------------
    		# dayOfWeek for 1700/1/1 = 5, Friday
		#------------------------------------

		dayOfWeek  = 5

		#-------------------------------------------------------
		# partial sum of days betweem current date and 1700/1/1
		#-------------------------------------------------------

		dayOfWeek += (aux + afterFeb) * 365                  

		#----------------------
		# leap year correction    
		#----------------------
		dayOfWeek += int(aux / 4 - aux / 100 + (aux + 100) / 400)     

		#-----------------------------
		# sum monthly and day offsets
		#-----------------------------
		dayOfWeek += offset[month - 1] + (day - 1)               
		dayOfWeek %= 7

		return dayOfWeek, week[dayOfWeek]


	#--------------	
	# enable alarm
	#--------------	
	def enableAlarm():
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x01, 0x02))
	

	#----------------------------------		
	# clear status and alarm registers 
	#----------------------------------
	def resetAlarm():

		#-----------------------
		# Clear status register
		#-----------------------
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x01, 0x00))

		#-----------------------
		# Clear alarm registers
		#-----------------------
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x09, 0x00))
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x0A, 0x00))
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x0B, 0x00))
		bus.transaction(i2c.writing_bytes(rtc_address1, 0x0C, 0x00))

	#-------------------	
	# read alarm status
	#-------------------
	def readAlarm():
		alarmstatus, status22 = bus.transaction(i2c.writing_bytes(rtc_address1, 0x01),
							i2c.reading(rtc_address1,2))[0]

		#----------------------------------
		# Mask alarm interrupt enable flag
		#----------------------------------
		aie = alarmstatus & 0x02

		#---------------------
		# Mask alarm set flag
		#---------------------
		af  = alarmstatus & 0x08

		return af, aie 


	#-----------------
	# Read alarm time
	#-----------------
	def readAlarmTime(month, year):

		#---------
		# minute
		#--------
		minute, minute2 = bus.transaction(      i2c.writing_bytes(rtc_address1, 0x09),
							i2c.reading(rtc_address1,2))[0]

		timeminute1 = ((minute >> 4) & 0x07)
		timeminute2 = (minute & 0x0F)

		#------
		# hour
		#------
		hour, hour2 = bus.transaction(	i2c.writing_bytes(rtc_address1, 0x0A),
						i2c.reading(rtc_address1,2))[0]

		timehour1 = ((hour >> 4) & 0x03)
		timehour2 = (hour & 0x0F)

		#------
		# Day
		#-----
		day, day2 = bus.transaction(	i2c.writing_bytes(rtc_address1, 0x0B),
						i2c.reading(rtc_address1,2))[0]

		timeday1 = ((day >> 4) & 0x05)
		timeday2 = (day & 0x0F)

		alminute        = int(str(timeminute1)+str(timeminute2))
		alhour          = int(str(timehour1)+str(timehour2))
		alday           = int(str(timeday1)+str(timeday2))
		weekday,dayname = weekDay(year,month,alday)

		return alminute, alhour, alday, weekday, dayname


	#-----------------
	# Show alarm time
	#-----------------

	def showAlarmTime():

		year = getYear()
		month, monthname = getMonth()

		alminute, alhour, alday, weekday, dayname = readAlarmTime(month, year)
		af, aie = readAlarm()

		if af == 1:
			print("    setalarm: alarm went off at %02d:%02d %s %02d %s %4d" % (alhour, alminute, dayname, alday, monthname, year))
		else:
			if alminute > 0 or alhour > 0 or alday > 0:
				print("    setalarm: alarm scehduled at %02d:%02d %s %02d %s %4d" % (alhour, alminute, dayname, alday, monthname, year))
			else:
				print("    setalarm: no alarm scheduled")

        #--------------
	# Display help
        #--------------
	def showHelp():
		print("")
		print("    PCF8563 RTC setalarm for Raspberry Pi version 2.00")
		print("    (C) M.A. O'Neill, TumblingDice 2014")
		print("")

		print("    Usage: setalarm [--usage | --help]")
		print("                    |")
		print("                    [-v | --verbose:False]")
		print("                    [-s | --status] | [-c | --cancel] | [-o | --off] |")
		print("                    [-m <minute of hour>  | --minute <minute of hour>]")
		print("                    [-h <hour of day>     | --minute <hour of day>]")
		print("                    [-d <day of month>    | --day <day of month>]")
		print("")
		print("                    The clock is a 24 hour clock: e.g. hour of day is 0..24")
		print("")

		exit()


#------------------------
# Main entry point here
#------------------------

	argp       = 1
	argd       = 0
	do_cancel  = False
	do_status  = False
	do_verbose = False
	argc       = len(sys.argv)

	if argc == 1:
		showHelp()

	#--------------------
	# Parse command tail
	#--------------------
	while(argp < argc):

		#-------------------------------
		# Help if user has requested it
		#-------------------------------
		if sys.argv[argp] == "--usage" or sys.argv[argp] == "--help":
			showHelp()

                #--------------------
		# Is output verbose?
		#--------------------
		if sys.argv[argp] == "-v" or sys.argv[argp] == "--verbose":
			do_verbose = True
			argd = argd + 1

		#----------------
		#  Cancel alarm
		#----------------
		if sys.argv[argp] == "-c" or sys.argv[argp] == "--cancel":
			do_cancel = True
			argd = argd + 1
		else:

			#---------------------
			# Report alarm status
			#---------------------
			if sys.argv[argp] == "-s" or sys.argv[argp] == "--status":
				do_status = True
				argd = argd + 1

		if do_cancel == False and do_status == False:

			#------------------------
			# Get hour to set alarm
			#------------------------
			if sys.argv[argp] == "-h" or sys.argv[argp] == "--hour":
				if argp == argc - 1 or sys.argv[argp+1][0] == '-':
					print("    setalarm ERROR: expecting integer value hour")
					print("")
					exit()
				else:
					try:
						hour = int(sys.argv[argp+1])
					except ValueError:
						print("    setalarm ERROR: integer between 0 and 23 expected")
						exit()

					if hour < 0 or hour > 23:
						print("    setalarm ERROR: expecting integer between 0 and 23")
						print("")
						exit()

				argd = argd + 2
				argp = argp + 1

			#-------------------------
			# Get minute to set alarm
			#-------------------------
			if sys.argv[argp] == "-m" or sys.argv[argp] == "--minute":
				if argp == argc - 1 or sys.argv[argp+1][0] == '-':
					print("    setalarm ERROR: expecting integer value minute")
					print("")
					exit()
				else:
	
					try:
						minute = int(sys.argv[argp+1])
					except ValueError:
						print("    setalarm ERROR: integer between 0 and 59 expected")
						exit()
				
					if minute < 0 or minute > 59:
						print("    setalarm ERROR: expecting integer between 0 and 59")
						print("")
						exit()

				argd = argd + 2
				argp = argp + 1

			#-------------------------------
			# Get day of month to set alarm
			#-------------------------------
			if sys.argv[argp] == "-d" or sys.argv[argp] == "--day":
				if argp == argc - 1 or sys.argv[argp+1][0] == '-':
					print("    setalarm ERROR: expecting integer value day")
					print("")
					exit()
				else:
					try:
						day = int(sys.argv[argp+1])
					except ValueError:
						print("    setalarm ERROR: integer between 0 and 31 expected")
						exit()
				
					if day < 0 or day > 31:
						print("    setalarm ERROR: expecting integer between 0 and 31")
						print("")
						exit()

				argd = argd + 2
				argp = argp + 1

		argp = argp + 1


	#-------------------------------------------
	# Check for unparsed command tail arguments
	#-------------------------------------------
	if argd < argc - 1:
		print("    setalarm ERROR: unparsed command tail arguments")
		print("")
		exit()

	if do_verbose:
		print("")
		print("    PCF8563 RTC setalarm for Raspberry Pi version 2.00")
		print("    (C) M.A. O'Neill, TumblingDice 2014")
		print("")

	if pcf8563OnI2cBus() == False:
		print("    setalarm ERROR: cannot find PCF8563 RTC on I2C bus")
		printf(" ")
		exit()

	#-------------------------------------------	
	# now we start communication with the clock
	# and enable clock pin out and alarm									
	#-------------------------------------------
	setClkOutput()
	enableAlarm()

	#----------------------------	
        # Show alarm Time and status 
	#----------------------------
	if do_status == True:
		showAlarmTime()
	else:
		#--------------
		# Cancel alarm
		#--------------
		if do_cancel == True:
			resetAlarm()

			if do_verbose:
				print("    setalarm: alarm cancelled")
		else:
			#--------------------	
       	 		# Schedule an alarm
			#--------------------
			year            = getYear()
			month,monthname = getMonth() 
			weekday,dayname = weekDay(year,month,day)

			#-----------------------------------------------
			# Sanity check the alarm must be in the future!
			#-----------------------------------------------
			nowDay    = getDay()

			if day < nowDay:
				print("    setalarm ERROR1: you cannot set the alarm to go off in the past!")
				print("")
				exit()
			else:
				nowHour    = getHour()
				nowMinute  = getMinute()
				nowMinutes = 60*nowHour + nowMinute
				minutes    = 60*hour    + minute

				if day < nowDay and minutes < nowMinutes:
					print("    setalarm ERROR2: you cannot set the alarm to go off in the past!")
					print("")
					exit()

			if do_verbose:
				print("    setalarm: alarm scheduled at: %02d:%02d %s %02d %s %4d" % (hour, minute, dayname, day, monthname, year))

			setAlarm(minute, hour, day, weekday)

	if do_verbose == True:
		print("    setalarm: finished")
		print("")

	exit()

