"""
Author: Mark Serrano
Python Messenger server
"""

from multiprocessing import Process, Pipe
import select
import socket
import sys
from time import sleep

def signIn(s,db,size,data): #nn noname av available
  nn = db[0]
  av = db[2]
  avr = db[3]
  name = data[4:]
  if data[0:4] == "NME:":
    if name in av:
      s.send("NOTAVAL")
    else:
      s.send("CONEST")
      nn.remove(s)
      av[name] = s
      avr[s] = name
  else:
  	s.send("Invalid params. Connection Terminated\n")
  	s.close()
  	nn.remove(s)

def makeConnection(s1,db,size,reps):
  pd = db[1]
  av = db[2]
  avr = db[3]
  if reps[0:4] == "ACP:":
    pd[s1].send("RAC:"+avr[s1])
    s2 = pd[s1]
    # deletes user 1 from available list
    del av[avr[s1]]
    del avr[s1]
    # deletes user 2 from available list
    del av[avr[s2]]
    del avr[s2]
    # deletes entry in pending connections list
    del pd[s1]
    # Spins thread off for convo
    p = Process(target=chatRoom, args=(s1, s2, size))
    #processes.append(p)
    p.start()
    #start thread here
  else:
    pd[s1].send("RDE:")
    del pd[s1]
    

def chatRoom(s1,s2,size):
  input = [s1,s2]
  while True:
      #blocks until one of these inputs has an input event
      inputready,outputready,exceptready = select.select(input,[],[]) 

      for s in inputready:
        data = s.recv(size)
        if data:
          if s == s1:
            s2.send(data)
          else:
            s1.send(data)
        else:
         s1.close()
         s2.close()
         return


def getAvail(dict,socket):
  s = "REP:"
  for i in dict.keys():
    if dict[i] != socket:
     s += i + ":"
  return s[:-1]
  
def manage(s,db,size,data):
  if data[0:4] == "QUE:":
    print "Available Users Sent!"
    s.send(getAvail(db[2],s))
  if data[0:4] == "REQ:":
    if data[4:] in db[2]:
      db[1][db[2][data[4:]]] = s
      s.send("RST")
      name = str(db[3][s])
      db[2][data[4:]].send("NRQ:"+name)
    
    

def main():
  host = ''      #empty string == use local host name
  port = 50000   #hope no one is using this

  backlog = 5 #how many connections can be waiting to be accepted at one time?
  size = 1024

  #Create a socket object of a particular type - not affiliated with any
  #machine or port yet.   AF_INET = IPv4; SOCK_STREAM = TCP (vs UDP)
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  

  #Allow us to reuse this socket more quickly if no one is currently using it
  server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

  #Connect that socket to host and port
  server.bind((host,port))

  #Start listening with the backlog value
  server.listen(backlog)
  # remember 7
  # of intvw 9
  noname = []
  pending = {}
  available = {}
  ava_reverse = {}
  database = [noname,pending,available,ava_reverse]

  input = [server,sys.stdin]
  clients_list = []
  running = 1
  while running:
      #blocks until one of these inputs has an input event
      inputready,outputready,exceptready = select.select(input+noname+available.values(),[],[]) 

      for s in inputready:

          if s == server:
              # handle the server socket
              client, address = server.accept()
              database[0].append(client)

          elif s == sys.stdin:
              # handle standard input
              junk = sys.stdin.readline()
              running = 0 

          else:
              # handle all other sockets
              data = s.recv(size)
              if data:
                if s in noname:
                  signIn(s,database,size,data)
                elif s in pending:
                  makeConnection(s,database,size,data)
                elif s in available.values():
                  manage(s,database,size,data)
              else:
                s.close()
                  
  server.close()

main()
