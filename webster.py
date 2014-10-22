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
MAX_THREADS = 50


def parseHTTP(d):
    """  """
    result = { 'comm':None, 'host':None, 'page':None, 'vsn':None }
    ds = d.decode().split('\r\n')
    count = 0
    for l in ds:
        a = l.split()
        if count == 0 and len(a) == 3:
            result['comm'] = a[0]
            result['page'] = a[1]
            result['vsn'] = a[2].rstrip()
        elif len(a) == 2:
            result[a[0].lower()] = a[1].rstrip()
        else:
            break
        count += 1
    return result


def sendError(e):
    """
    Sends the appropriate error response.
    Currently ONLY errors are returned by this server.
    """
    if e == 400:
        msg = str(e) + ' ' + 'Bad Request'
    elif e == 404:
        msg = str(e) + ' ' + 'Not Found'
    else:
        e = 501
        msg = '501 Not Implemented'
    return header(msg,msg,'close')


def header(msg,code,conn):
    head = 'HTTP/1.1 ' + code + '\r\n'
    html = '<!DOCTYPE HTML><html><head><title>' + code
    html += '</title></head><body><h1>'+ msg + '</h1></body>'
    html = html.encode()
    head += 'Content-Length: ' + str(len(html))
    head += '\r\nConnection: ' + conn + '\r\nContent-type: text/html\r\n\r\n'
    head = head.encode()
    head += html
    print(head)
    return head


def parseRequest(conn):
    """  """
    while True:
        data = conn.recv(BUF_SIZE)
        if data:
            req = parseHTTP(data)
            print(req)
            if not req['comm']:
                conn.sendall(sendError(400))
                conn.close()
                break
            elif req['comm'] != 'GET':
                conn.sendall(sendError(501))
                conn.close()
                break
            elif req['comm'] == 'GET':
                #conn.sendall(sendError(404))
                msg = 'Hoi! Hoe gaat het,'+req['page']+'?  Gaat, dank je!'
                conn.sendall(header(msg,'200 OK','keep-alive'))
        else:
            break
    conn.close()


class MyThread(threading.Thread):
    def __init__(self,conn):
        threading.Thread.__init__(self)
        self.conn = conn

    def run(self):
        print('Starting thread with conn:',self.conn)
        parseRequest(self.conn)
        print('Closing thread with conn:',self.conn)


def listenAndServe():
    """ Main HTTP listen & serve loop.  """
    tpool = threading.BoundedSemaphore(value=MAX_THREADS)
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((HOST,PORT))
    while True:
        print("Threads:",threading.active_count())
        #with tpool:
        s.listen(BACKLOG)
        conn, addr = s.accept()
        print('Connected by', addr)
        t = MyThread(conn)
        t.start()

if __name__ == '__main__':
    listenAndServe()
