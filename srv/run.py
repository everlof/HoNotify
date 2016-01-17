#!/usr/bin/env python

import sys, os, logging, socket

from threading import Thread
from user import HonUser
import appcom

HOST = ''
PORT = 11091

def main():
  logging.basicConfig(level=logging.DEBUG)
  logging.info('Running HoNotify')

  srv_sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

  srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  srv_sock.bind((HOST, PORT))
  srv_sock.listen(1)

  logging.info("Listening on %d" % PORT)
  i = 0

  while 1:
    conn, addr = srv_sock.accept()
    i += 1

    t = Thread(target = appcom.appclient_accepted, args = (conn, addr))
    t.start()

    print("Client %d accepted" % i)

  sys.exit(0)

if __name__ == '__main__':
  main()
