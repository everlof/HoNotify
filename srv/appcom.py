import sys, os, logging, struct

from user import HonUser
from ..common import packets

import masterserver

def appclient_accepted(conn, addr):
  u = HonUser();

  packet = packets.recv_packet(conn)

  packet_ID, packet = packets.parse_part(packet, 'H')
  packet_ID = packet_ID[0]

  logging.info('Packet ID: %s' % format(packet_ID, '02x'))

  if packet_ID == packets.APP_ID.APP_CS_LOGIN:
    
    packet_content, packet = packets.parse_part(packet, 'sBs')
    username = packet_content[0]
    is_hashed = packet_content[1]
    password = packet_content[2]


    print "Login %s/%s (hashed? %d)" % (username, password, is_hashed)

    u.set_username(username)
    u.set_password(password, is_hashed)

    logging.info('Log in with user/pass')
    if u.auth():
        u.perform_connect()
        print("Authenticated!")
    else:
      print("NOT Authenticated")

    packets.app_send_srv(conn, packets.APP_ID.APP_SC_LOGIN_OK)
    
    conn.close()
  else:
    print('Unrecognized package ID')
    conn.close()
