# Self Trainer:
# Author: Matt Howard (themdhoward [at] gmail [dot] com)
#
# -denies access to a list of applications (mostly games I guess) and records
# -auto-closes a blacklist of window titles
# -monitors idle time
# -email notifications for idle time after threshold exceeded

# note: built from python 2.4! 


import pydbg
import os
from pydbg.defines import *
import time
import win32api
import win32process
import win32gui
import win32con
import datetime
import smtplib
import dns.resolver
from email.MIMEText import MIMEText # different in other versions of python, will add support later


########### User defined variables ### TODO: add options or a simple gtk interface ########
idle_timer = 60 # 1 minute by default
idle_max = 60*1 # 1 min TESTING
email_addr="" # change me! preferably a phone email address!

# list of programs to monitor for/kill
deny_program_list = ["sc2.exe", "iw5mp.exe", "smplayer.exe"]

# list of window titles to monitor for/kill
deny_title_list = ["slashdot", "reddit", "starcraft", "facebook"]
###########################################################################################

last_input = 0
timer = 0
idle=False
message_sent = False

pydb = pydbg.pydbg()
w=win32gui

#currently I've only tested this against *@gmail.com so be warned if it doesnt work
# for your specific email address... Also any help appreciated.. :)
def send_msg(email, msg):
    try:
		domain = email[email.find("@")+1:]
		servers = dns.resolver.query(domain, 'MX')
    except:
		return -2
    
    msg = MIMEText(msg)
    msg['Subject'] = 'Idle time exceeded max!'
    msg['From'] = "idletimer@gmail.com"
    msg['To'] = email
    our_smtp = servers[0].to_text() # lets use the first response# add more checks later
    our_smtp = our_smtp[our_smtp.find(" ")+1:] # take out the 
	
    print our_smtp
    try:
		s = smtplib.SMTP(our_smtp)
		s.sendmail("idletimer@gmail.com", [email], msg.as_string())
    except:
		print "email send failed"
		return -1 ## lets make some better error catching later
    print "email notification sent to " + email
    s.quit()


if __name__ == "__main__":
	# the event loop
	while(1):
		time.sleep(1)
		
		# idle timer
		temp_input = win32api.GetLastInputInfo()
		if(temp_input != last_input):
			if(idle):
				print "Idle for " + str(datetime.timedelta(seconds=timer)) + " (hh:mm:ss)"
				idle=False
			timer=0
		else:
			timer=timer+1
		last_input=temp_input
		if(timer >= idle_timer):
			idle=True
			if(timer >= idle_max and message_sent == False):
				send_msg(email_addr, "Idle limit reached! Back to work!")
				message_sent = True
		
		#check the window title of current window
		hwnd=w.GetForegroundWindow()
		window_text = w.GetWindowText(w.GetForegroundWindow())
		pid=str(win32process.GetWindowThreadProcessId(w.GetForegroundWindow())[1])
		for nono in deny_title_list:
			# perhaps better to match exactly here?
			if(nono.lower() in window_text.lower()):
				print "Logged an attempt of a window containing %s: (%s:%s)" % (nono, window_text, pid)
				win32gui.SendMessage (hwnd, win32con.WM_CLOSE, 0, 0)   # close is better
				# os.system("taskkill /PID " + pid)
		# check the process list
		for (pid, app) in pydb.enumerate_processes():
			for nono in deny_program_list:
				if(nono.lower() == app.lower()):
					print "Logged an attempt at running: (%s:%d)" % (app,pid)
					os.system("taskkill /F /im " + app)
				else:
					pass