#!/usr/bin/python3

### Script for show/sending commands to cisco catalyst by ssh connection with paramiko library.
### Is not all my work, I take differnet peaces of code from internet and adapt to my purpose.
### Need separate text file named host_file.txt with list of all ip's of switches each one in new line.
### The script ask for login (user, password and enable password) or you can hardcode it for lab purposes.
### Output to console and text files one for every switch with name IP+date, and if some switch is not accessible output a log+date file with list of IP's not accesible.
### By Tom Gilabert. I'm not responsable of any result executing this scripts. Thanks

import paramiko
import time
import datetime
from multiprocessing import Pool
from functools import partial
import os
import getpass

commands = [
    'show version',
    'conf t',
    'end',
    'wr mem'
]

# Login with credentials hardcoded, only for lab!
"""
user="user"
passwd="password"
epasswd="enable_password"
"""

# Pull target hosts from host_file
with open('host_file.txt') as f:
    hosts = f.read().splitlines()

max_buffer = 65535

def clear_buffer(connection):
    if connection.recv_ready():
        return connection.recv(max_buffer)

def ssh_conn(user,passwd,epasswd,ip):
    try:
        date_time = datetime.datetime.now().strftime("%Y-%m-%d")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=22, username=user, password=passwd, look_for_keys=False, allow_agent=False, timeout=None)
        connection = ssh.invoke_shell()
        output = clear_buffer(connection)
        time.sleep(2)
        connection.send("terminal length 0\n")
        time.sleep(1)
        connection.send("\n")
        connection.send("enable\n")
        time.sleep(.5)
        connection.send(epasswd + "\n")
        time.sleep(.5)
        outputFileName = ip + ' ' + str(date_time) + '_output.txt'
        with open(outputFileName, 'wb') as f:
            for command in commands:
                print(f"Executing command {command}")
                connection.send(command + "\n")
                time.sleep(5)
                file_output = connection.recv(max_buffer)
                f.write(file_output)
                print(file_output.decode(encoding='utf-8'))
        connection.close()
        print("%s is done" % ip)
        
    except:
        print(ip + ": Cannot connect, Please try again!!!")
        with open("log_" + str(date_time) + ".txt", 'a') as l:
            l.write(ip + ": Error connection\n")

if __name__ == '__main__':

    # Ask for credentials
    if not all(var in globals() for var in ('user','passwd','epasswd')):
        user = input("User: ")
        passwd = getpass.getpass('Password:')
        epasswd = getpass.getpass('Enable Password:')

    # Assignem parametres abans del multithreat, despres al pool nomes passem iterancia -> hosts
    func = partial(ssh_conn,user,passwd,epasswd)
    # Pool(5) means 5 process will be run at a time, more hosts will go in the next group
    with Pool(5) as p:
        print(p.map(func, hosts))
