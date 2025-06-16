#!/usr/bin/python

import paramiko

IP_ADDRESS_RE = re.compile(r"^\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\b$")

def ip_address_valid(ip_addr):
  if not IP_ADDRESS_RE.match(ip_addr):
    return False
  ip_addr_octets = ip_addr.split(".")
  for octet in ip_addr_octets:
	  if (0 <= int(octet) <= 255):
		  return True

def toc(ip,typed_username,typed_password,line_cmd,typed_sleeping_time,typed_frequency):
	try:
		session=paramiko.SSHClient()
		session.load_system_host_keys()
		session.set_missing_host_key_policy(paramiko.RejectPolicy())
		session.connect(ip,username=typed_username,password=typed_password)
		connection=session.invoke_shell()
		connection.send("terminal length 0\n")
		time.sleep(1)
		connection.send(line_cmd+'\n')
		time.sleep(typed_sleeping_time)
	except paramiko.AuthenticationException:
        print("* Invalid username or password. \n* Please check the username/password file or the device configuration!")
        print("* Closing program...\n")
    finally:
		session.close()
		
def main():
  ip_addr = raw_input("Type IP adress from network:") 
  username = raw_input("Type username of network device:") 
  password = raw_input("Type IP adress of network device:") 
  command_all = raw_input("Type commands which would you like to try:") 
  delay_all = raw_input("Type delay for each command:")  
  frequency = raw_input("Type frequency of commands on network device:") 
  input_cmd = []
  input_cmd.append(command_all.split(','))  
  
  while not ip_address_valid(ip_addr):
	  print("Your error address input",ip_addr)
	  ip_addr = raw_input("Type IP adress from network again:")	
	  toc(input_cmd,command_all,delay_all,frequency,ip_addr2,username,password)
  else:
	  toc(input_cmd,command_all,delay_all,frequency,ip_addr,username,password)
