"""
Author: Mark Serrano
Python Messenger Client
"""

import socket
import sys
import select

def connect(host,port,size):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((host,port))
  while True:
    name = raw_input("Enter your Name")
    s.send("NME:"+name)
    data = s.recv(size)
    if data == "CONEST":
      print "Welcome %s, you are now connected" %(name)
      return s
    else:
      print "Sorry, the username '%s' is already taken!" %(name)

def checkUsers(socket,size):
  socket.send("QUE:")
  resp = socket.recv(size)
  resp = resp.strip()
  resp = resp[4:]
  if len(resp) > 0:
    print "*"*20, "\n"
    print "Available Users\t\t\n"
    resp = resp.split(":")
    for i in range(len(resp)):
      print "%d. %s" %(i+1,resp[i])
    print "*"*20, "\n"
    user = raw_input("Enter the number of the user you wish to chat with (or -1 to cancel): ")
    if user.isdigit() and int(user) >= -1 and int(user) <= len(resp) and int(user) != 0:
      if int(user) != -1:
        msg = "REQ:" + str(resp[int(user)-1])
        print msg
        socket.send(msg)
    else:
      print "Invalid Choice"
  else:
    print "NO USERS AVAILABLE"

def manage(socket,size):
  input = [socket,sys.stdin]
  while True:
      print "***********************************\n", \
        "Please Choose from the following options: \n", \
        "1. Start a new chat \n2. QUIT"
      #blocks until one of these inputs has an input event
      inputready,outputready,exceptready = select.select(input,[],[]) 
      for s in inputready:

          if s == sys.stdin:
              # handle standard input
              opt = sys.stdin.readline()
              opt = opt.strip()
              if checkValid(opt):
                opt = int(opt)
                if opt == 1:
                  checkUsers(socket,size)
                  break
                elif opt == 2:
                  quit()
              else:
                print "Invalid input!"

          else:
            data = s.recv(size)
            if data:
              if data[0:4] == "NRQ:":
                print "New chat request from " + data[4:]
                print "Do you accept?"
                if getYorN():
                  s.send("ACP:")
                  startChat(s,size,data[4:])
                else:
                  s.send("DEN:")
              elif data[0:4] == "RST:":
                print "Request Sent"
              elif data[0:4] == "RAC:":
                print "Request Accepted"
                startChat(s,size,data[4:])
              elif data[0:4] == "RDE:":
                print "Request Denied"
            else:
              print "Connection dropped by server. Exiting"
              quit()
                
def startChat(sock,size,name):
  print "IN CHAT MODE"
  input = [sock,sys.stdin]
  status = True
  while status:
      #blocks until one of these inputs has an input event
      inputready,outputready,exceptready = select.select(input,[],[]) 
      for s in inputready:

          if s == sys.stdin:
              # handle standard input
              opt = sys.stdin.readline()
              opt = opt.strip()
              sock.send(opt)
          else:
            data = s.recv(size)
            if data:
              print name + ": " + data
            else:
              print "Connection Terminated"
              quit()
              
def getYorN():
  while True:
    usr = raw_input("Yes or No?")
    usr = usr.lower().strip()
    if usr == "y" or usr == "yes":
      return True
    elif usr == "n" or usr == "no":
      return False
    else:
      print "invalid choice"
      
def checkValid(opt):
  if opt.isdigit() and int(opt) > 0 and int(opt) < 4:
    return True
  return False

def main():
  host = ''#'sage.cs.swarthmore.edu'
  port = 50000
  size = 1024
  s = connect(host,port,size)
  manage(s,size)
  s.close()

main()