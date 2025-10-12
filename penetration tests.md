# Host Enumeration

The enumeration of hosts is one of the first tasks you need to perform in the information-gathering phase of a penetration test. 
Host enumeration is performed internally and externally. When performed externally, you typically want to limit the IP addresses 
you are scanning to just the ones that are part of the scope of the test. This reduces the chance of inadvertently scanning an 
IP address that you are not authorized to test. When performing an internal host enumeration, you typically scan the full subnet or 
subnets of IP addresses being used by the target. Host enumeration is usually performed using a tool such as Nmap or Masscan; however, 
vulnerability scanners also perform this task as part of their automated testing. Example 3-23, earlier in this module, shows a sample 
Nmap ping scan being used for host enumeration on the network 192.168.88.0/24. In earlier versions of Nmap, the Nmap ping scan 
option was -sP (not -sn ).

# User Enumeration

Gathering a valid list of users is the first step in cracking a set of credentials. 
When you have the username, you can then begin brute-force attempts to get the account password. 
You perform user enumeration when you have gained access to the internal network. On a Windows network, 
you can do this by manipulating the Server Message Block (SMB) protocol, which uses TCP port 445. Figure 3-12 illustrates 
how a typical SMB implementation works.

`nmap --script smb-enum-users.nse <host>`

#Group Enumeration

For a penetration tester, group enumeration is helpful in determining the authorization roles that are being used in the target environment. 
The Nmap NSE script for enumerating SMB groups is smb-enum-groups. This script attempts to pull a list of groups from a remote 
Windows machine. You can also reveal the list of users who are members of those groups. The syntax of the command is as follows:

`nmap --script smb-enum-groups.nse -p445 <host>`

#Network Share Enumeration

Identifying systems on a network that are sharing files, folders, and printers is helpful in building out an attack surface 
of an internal network. The Nmap smb-enum-shares NSE script uses Microsoft Remote Procedure Call (MSRPC) for network share enumeration.

`nmap --script smb-enum-shares.nse -p 445 <host>`