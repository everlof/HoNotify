

import sys, os, logging, struct
from struct import unpack
import time
import socket, asyncore, asynchat
from hashlib import md5
import masterserver
from ..common import packets

class HonUser(asynchat.async_chat):
    def __init__(self):
        asynchat.async_chat.__init__( self )
        self.username = None
        self.password = None
        self.id2nick = {}
        self.chan2id = {}
        self.id2chan = {}
        self.id2clan = {}
        self.nick2id = {}
        self.nick2clan = {}
        self.chat_url = None
        self.chat_port = None
        self.sock = None
        self.buffer = ''
        self.connection_timeout_threshold = 60
        self.connection_timeout = time.time() + 5

    def set_username(self, username):
        self.username = username

    def set_password(self, password, is_hash):
        if is_hash:
            self.password = password
        else:
            self.password = md5(password).hexdigest()

    def __str__(self):
        return "username=%s, password=%s" % (self.username, self.password)

    def perform_connect(self):
        self.create_socket( socket.AF_INET, socket.SOCK_STREAM )
        self.connect( ( self.chat_url, self.chat_port ) )
        asyncore.loop()

    def readable(self):
        if time.time() - self.connection_timeout >= self.connection_timeout_threshold:
            self.close()
            return False
        return True

    def collect_incoming_data( self, data ):
        self.buffer += data

    def found_terminator( self ):
        if self.got_len:
            self.set_terminator(2)
            self.dispatch(self.buffer)
        else:
            self.set_terminator(unpack("<H",self.buffer)[0])
        self.buffer = ''
        self.got_len = not self.got_len

    def handle_connect( self ):
        print ('handle_connect()')
        self.set_terminator(2)
        self.got_len = False
        self.write_packet(
            packets.ID.HON_CS_AUTH_INFO,
            self.account_id,
            self.cookie,
            self.ip,
            self.auth_hash,
            packets.ID.HON_PROTOCOL_VERSION,
            0x010681, # was 0x383,
            'lac',
            3, # Version MAJOR
            8, # Version MINOR
            1, # Version THIRD
            0, # Version FOURTH
            0,
            'en',
            'en',)

    def write( self, data ):
        self.push(data)

    def write_packet(self,packet_id,*args):
        data = packets.pack(packet_id,*args)
        self.write(struct.pack('<H',len(data)))
        self.write(data)
        print("SEND")
        print(packets.dump(data))

    def dispatch(self,data):
        self.connection_timeout = time.time()

        print("RECV")
        print(packets.dump(data))

    def auth(self):
        auth_data = masterserver.auth(self.username, self.password)
        if 'ip' not in auth_data or 'auth_hash' not in auth_data:
            print("Login Failure")
            return False
        self.chat_url = auth_data['chat_url']
        self.chat_port = int(auth_data['chat_port'])
        self.ip = auth_data['ip']
        self.cookie = auth_data['cookie']
        self.account_id = int(auth_data['account_id'])
        self.auth_hash = auth_data['auth_hash']
        self.got_len = False
        self.nick = auth_data['nickname']
        self.id2nick[self.account_id] = self.nick
        self.nick2id[self.nick] = self.account_id
        if "clan_member_info" in auth_data:
            self.clan_info = auth_data["clan_member_info"]
        else:
            self.clan_info = {}
        if "clan_roster" in auth_data and "error" not in auth_data["clan_roster"]:
            self.clan_roster = auth_data["clan_roster"]
        else:
            self.clan_roster = {}
        if "buddy_list" in auth_data:
            buddy_list = auth_data["buddy_list"]
        else:
            buddy_list = {}
        self.buddy_list = {}

        for id in self.clan_roster:
            if self.clan_roster[id]['nickname']:
                nick = normalize_nick(self.clan_roster[id]['nickname']).lower()
            self.id2nick[id] = nick
            self.nick2id[nick] = id

        for buddies in buddy_list.values():
            for buddy in buddies.values():
                try:
                    id = int(buddy['buddy_id'])
                    self.buddy_list[id] = buddy
                    nick = normalize_nick(buddy['nickname'])
                    self.id2nick[id] = nick
                    self.nick2id[nick] = id
                except:
                    pass

        return auth_data