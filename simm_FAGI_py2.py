#!/usr/bin/python
# -*- coding:utf-8 -*-
#
# python 2.7.5
#

from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ClientFactory, ServerFactory
from twisted.internet.error import ConnectionLost, ConnectionDone, ConnectionAborted
import sys

if 'bsd' in sys.platform:
    from twisted.internet import kqreactor
    kqreactor.install()
    print (".......kqreactor")
elif sys.platform.startswith('linux'):
    from twisted.internet import epollreactor
    epollreactor.install()
    print (".......epollreactor")
elif sys.platform.startswith('darwin'):
    from twisted.internet import kqreactor
    kqreactor.install()
    print (".......kqreactor")
elif sys.platform == 'win32':
    raise Exception("Sorry dude, Twisted/Windows select/iocp reactors lack the necessary bits.")
else:
    raise Exception("Hey man, what OS are you using?")

from twisted.internet import reactor

import string
import re
import time
import struct
from array import array
from time import sleep

ENCODE_STR='euc-kr'

class FagiClientProtocol(LineReceiver):
    def __init__(self):
        #print ('FAGI.__init__')
        self.m_nState = 0
        
    def GetId(self):
        return self.factory.m_szEapClientId
        
    def connectionMade(self):
        print ("connectionMade from (%s)" % (str(self.transport.client)))
        self.factory.clientReady(self)
        self.m_nState = 0
        
    def dataReceived(self, line):
        #print ("$ got msg.... State=%d, Len=%d(%s)\r\n" % (self.m_nState, len(line), line))
        szCmd = ""
        token = line.rstrip().split()

        if line.find("HANGUP") >= 0 :
            return ConnectionAborted()

        if self.m_nState == 0 :
            if line.find("agi_network_script:") > 0 :
                self.m_nState = 1
                szCmd = "ANSWER\n";
        elif token[0] == "200" or token[0] == "500" :
            # Must be receive response (200 result=0 (123) or 500 Invalid ...)
            nResponse = int(token[0])
            nResult = -1
            szData = ""
            #print ('-- State[%d].Recv(%s,%d)' % (self.m_nState, token, len(token)))

            if nResponse == 200 :
                if len(token) >= 2 :
                    nResult = int(token[1].replace("result=", ""))
                if len(token) >= 3 :
                    szData = token[2]
            else :
                nReponse = int(token[0])
                if len(token) >= 2 :
                    szData = token[1]
            #print ('-- State[%d].Recv(%d,%d,%s)' % (self.m_nState, nResponse, nResult, szData))

            if nResponse == 200 :
                if self.m_nState == 1 :
                    if nResult == 0 :
                        szCmd = "SAY DIGITS 1 \"\"\n"
                        self.m_nState = 2
                elif self.m_nState == 2 :
                    if nResult == 0 :
                        szCmd = "EXEC READ digito \"\" 1 \"\"\n"
                        self.m_nState = 3
                elif self.m_nState == 3 :
                    if nResult == 0 :
                        szCmd = "GET VARIABLE digito\n"
                        self.m_nState = 4
                elif self.m_nState == 4 :
                    if nResult >= 0 :
                        szData = szData.lstrip('(').rstrip(')')
                        szCmd = "SAY DIGITS " + szData + " \"\"\n"
                        self.m_nState = 4

        if len(szCmd) > 0 : 
            self.transport.write(szCmd)
            #print ('-- State[%d].Send(%s)' % (self.m_nState, szCmd))
        
    def connectionLost(self, reason):
        print ("Disconnected from (%s)" % (str(self.transport.client)))
        #print ('-- clientConnectionLost() called...' + str(reason))

class MyFactory(ClientFactory):
    protocol = FagiClientProtocol
    
    def __init__(self, szClientId):
        print ('MyFactory.__init__ szClientId=%s' % (szClientId))
        self.startFactory()
        self.m_szClientId = szClientId
        
    def clientConnectionFailed(self, connector, reason):
        reactor.stop()
       
    def clientConnectionLost(self, connector, reason):
        print ('-- clientConnectionLost() called')
        #connector.stop()

    def startFactory(self):
        print ('-- startFactory() called')
        self.messageQueue = []
        self.clientInstance = None
       
    def stopFactory(self) :
        print ('-- stopFactory() called')

    def clientReady(self, instance):
        #print ('-- clientReady() called')
        self.clientInstance = instance
        for msg in self.messageQueue:
            self.sendMessge(msg)
        
    def sendMessage(self, msg):
        if self.clientInstance is not None:
            print ('$ client instance is not null')
            self.clientInstance.sendLine(msg)
        else:
            print ('$ client instance is null')
            self.messageQueue.append(msg)

host = '0.0.0.0'
port = 4574
if __name__ == '__main__':

    argc = len(sys.argv)
    if argc > 1 :
        myFactory = MyFactory(sys.argv[1])
        reactor.listenTCP(port, myFactory)
        reactor.run()
    else :
        print ('Usage: %s [id]' % (sys.argv[0]))
        sys.exit(2)
