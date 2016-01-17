#!/usr/bin/env python

import sys, os, logging
import socket
import struct

from ..common import packets

HOST = ''
PORT = 11091

ENV_USERNAME = 'HON_USERNAME'
ENV_PASSWORD = 'HON_PASSWORD'

def main():
  if os.environ.get(ENV_USERNAME) == None or os.environ.get(ENV_PASSWORD) == None:
    print "Username and password are required, use env. vars: %s and %s" % (ENV_USERNAME, ENV_PASSWORD)
    sys.exit(1)

  logging.basicConfig(level=logging.DEBUG)
  logging.info('Running HoNotify - client')

  sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
  sock.connect((HOST, PORT))

  # Login
  packets.app_send_client(sock, packets.APP_ID.APP_CS_LOGIN, os.environ.get(ENV_USERNAME), 0, os.environ.get(ENV_PASSWORD))
  packet = packets.recv_packet(sock)

  res, data = packets.parse_part(packet, 'H')

  if res[0] == packets.APP_ID.APP_SC_LOGIN_OK:
    print "LOGIN OK"
  elif res[0] == packets.APP_ID.APP_SC_LOGIN_NOK:
    print "LOGIN NOT OK"
  else:
    print('Unrecognized package ID')

  sys.exit(0)

if __name__ == '__main__':
  main()
