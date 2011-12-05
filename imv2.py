from multiprocessing import Process, Pipe
import select
import socket
import sys
from time import sleep

def signIn(s,nn,av,avr,size): #nn nonage av available
  data = s.recv(size)
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

def makeConnection(s1,pd,av,avr,size):
  reps = s1.recv(size)
  if reps[0:4] == "ACP:":
    pd[s1].send("Request Accepted")
    del av[avr[s]]
    del avr[s]
    #start thread here
  else:
    pd[s1].send("Request Denied")
    del pd[s1]
    
  

def connection(client, address,conn):
  running = 1
  while running:
    data = client.recv(1024)
    if data:
      if data[0:3] == "SND":
        for addr in conn.recv():
          if addr != client:
            addr.send(data[3:])
        client.send("Message Sent\n")
      elif data[0:3] == "WHO":
        client.send(str(clients))
      #elif data [0:4] == "CLR":
      #  asd
    else:
      client.close()
      clients.removeClient(client)
      running = 0


def getAvail(dict,socket):
  s = "REP:"
  for i in dict.keys():
    if dict[i] != socket:
     s += i + ":"
  return s[:-1]
  
def manage(s,available,ava_reverse,pending,size):
  data = s.recv(size)
  if data[0:4] == "QUE:":
    print "Available Users Sent!"
    s.send(getAvail(available,s))
  if data[0:4] == "REQ:":
    if data[4:] in available:
      pending[available[data[4:]]] = s
      s.send("RST")
      name = str(ava_reverse[s])
      available[data[4:]].send("NRQ:"+name)
    
    

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
              noname.append(client)

          elif s == sys.stdin:
              # handle standard input
              junk = sys.stdin.readline()
              running = 0 

          else:
              # handle all other sockets
              if s in noname:
                print "SignIn started"
                signIn(s,noname,available,ava_reverse,size)
              elif s in pending:
                makeConnection(s, pending, available, ava_reverse,size)
              elif s in available.values():
                manage(s,available,ava_reverse,pending,size)
              else:
                s.close()
                  
  server.close()

main()
