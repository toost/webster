#    Webster: A Stupid HTTP server
#    Copyright (C) 2014 toost
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import socket
import threading

HOST = ''
PORT = 6543
BACKLOG = 5
BUF_SIZE = 500

CODES = { 200:'200 OK', 400:'400 Bad Request', 404:'404 Not Found', 501:'501 Not Implemented' }


def parseHTTP(d):
    """  """
    result = { 'comm':None, 'host':None, 'page':None, 'vsn':None }
    ds = d.split('\r\n')
    count = 0
    for l in ds:
        a = l.partition(':')
        if count == 0 and len(a[0]) > 1:
            x = a[0].split()
            if len(x) == 3:
                result['comm'] = x[0]
                result['page'] = x[1]
                result['vsn'] = x[2].rstrip()
        elif len(a[0]) >= 1:
            result[a[0].lower()] = a[2].rstrip()
        else:
            break
        count += 1
    return result


def htmlResponse(msg,code,conn):
    html = '<!DOCTYPE HTML><html><head><title>' + code
    html += '</title></head><body><h1>'+ msg + '</h1></body>'
    html = html.encode()
    head = 'HTTP/1.1 ' + code + '\r\n'
    head += 'Content-Length: ' + str(len(html)) + '\r\n'
    head += 'Connection: ' + conn + '\r\nContent-type: text/html\r\n\r\n'
    head = head.encode()
    head += html
    print(head)
    return head


def parseRequest(conn):
    """  """
    while True:
        buff = ''
        while '\r\n\r\n' not in buff:
            data = conn.recv(BUF_SIZE).decode()
            if not data:
                return
            buff += data
        req = parseHTTP(buff)
        print(req)
        if not req['comm']:
            conn.sendall(htmlResponse(CODES[400],CODES[400],'close'))
            return
        elif req['comm'] != 'GET':
            conn.sendall(htmlResponse(CODES[501],CODES[501],'close'))
            return
        elif req['comm'] == 'GET':
            msg = 'Hoi! Hoe gaat het, '+req['page']+'?  Gaat, dank je!'
            conn.sendall(htmlResponse(msg,CODES[200],'keep-alive'))


class ClientThread(threading.Thread):
    def __init__(self,conn):
        threading.Thread.__init__(self)
        self.conn = conn

    def run(self):
        parseRequest(self.conn)
        self.conn.close()


def listenAndServe():
    """ Main HTTP listen & serve loop.  """
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((HOST,PORT))
    s.listen(BACKLOG)
    while True:
        print("Threads:",threading.active_count())
        conn, addr = s.accept()
        print('Connected by', addr)
        t = ClientThread(conn)
        t.start()


if __name__ == '__main__':
    listenAndServe()
