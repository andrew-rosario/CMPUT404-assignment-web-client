#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
import time
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, headers=None, body=""):
        self.code = code
        self.headers = []
        self.body = body

    def get_code(self):
        return self.code

    def get_headers_list(self):
        return self.headers

    def get_message_body(self):
        return self.body


class HTTPClient(object):
    # def get_host_port(self,url):

    def __init__(self):
        self.socket = None

    def connect(self, host, port=80):
        if port is None:
            port = 80
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data) -> int:
        """
        Get the HTTP response code from the HTTP response.
        :param data:
        :return:
        """
        first_line = str.split("\r\n")[0]

        try:
            test = int(first_line.split(" ")[1])
        except ValueError:
            print("This is not a number.")

        return int(first_line.split(" ")[1])

    def get_headers(self, data) -> list:
        """
        Get the headers from a HTTP response.
        :param data: A HTTP-compliant response.
        :return: a list of strings containing the headers
        """
        headers = []
        traverse = data.split("/r/n")[1:]
        for line in traverse:
            header_split = line.split(": ")
            header_split[1] = header_split[1].rstrip()
            headers.append((header_split[0],header_split[1]))
            if line == "\r\n":
                break
        return headers

    def get_body(self, data):
        '''
        Get the body from a= HTTP response.
        :param data: A HTTP-compliant response.
        :return: the body of the HTTP response.
        '''
        lines = data.split("\r\n")
        index_start = 0

        found = False
        for line in lines:
            if line != "":
                index_start += 1
            else:
                found = True
                break
        if not found:
            return ""
        else:
            return lines[index_start:]

    def get_url_components(self, url):
        index_start = 0
        index_end = 0
        # https://
        # first, find if http is the proper scheme
        if re.match("(?<scheme>http(?<is_secure>s?):\/\/)(?<domain>[A-Za-z0-9.]+)+(?<directory>[A-Za-z0-9\/]*)?", url):
            pass

    def get_host(self, url):
        '''
        A very, very, very inefficient way to get the host address lol
        :param url: a String
        :return:
        '''
        index_start = 0
        index_end = 0

        for character in url:
            if index_end == 0:
                if character == "/":
                    index_start += 2
                    index_end = index_start
                index_start += 1
        # http://google.com

        while True:
            if url[index_end] != "/":
                index_end += 1
            else:
                return url[index_start:index_end]

    def get_subdirectory(self, url):
        index_start = 0
        index_end = 0
        count = 0
        for character in url:
            if index_end == 0:
                if character == "/":
                    count += 1
                    if count == 3:
                        break
                elif index_start + 1 == len(url):
                    return "/"
                index_start += 1
        # http://google.com
        return url[index_start:len(url)]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        if self.socket:
            self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        print("Entered recvall")
        buffer = bytearray()
        done = False
        time_start = time.time()
        while not done:
            part = sock.recv(1024)
            if part:
                buffer.extend(part)
            else:
                done = not part
            print(time.time() - time_start)
            if time.time() - time_start > 30:
                return ""
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        url_split = urllib.parse.urlparse(url)
        print(f"Connecting to {url_split.hostname} {url_split.port}")
        self.connect(url_split.hostname, url_split.port)
        code = 500
        headers = []
        body = ""
        #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #sock.connect((url_split.scheme +url_split.hostname,url_split.port))
        print(url)

        request = f"GET {url_split.path} HTTP/1.1\r\nHost: {url_split.hostname}"
        print(f'Sent following message: {request}')

        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()
        if response:
            print(f"Response received: {response}")
            code = self.get_code(response)
            headers = self.get_headers(response)
            body = self.get_body(response)
            return HTTPResponse(code, headers, body)
        else:
            print("Message has not been received. Perhaps the connection was lost?")
            return None

    def POST(self, url, args=None):
        """
        Post data to the specified URL.
        :param url: The URL to post to.
        :param args: The data to be posted.
        :return: A HTTPResponse object.
        """
        url_split = urllib.parse.urlparse(url)
        self.connect(url_split.hostname,url_split.port)

        content_to_send = {"content-type": "", "content-length": "0",
                           "content": ""}

        if not args:
            content_to_send["content-type"] = "application/x-www-form-urlencoded"
            content_to_send["content-length"] = str(len(args))
            content_to_send["content"] = str(args)

        type = content_to_send["content-type"]
        length = content_to_send["content-length"]
        content = content_to_send["content"]
        request = (f"POST {url_split.path} HTTP/1.1\r\n"
                   f"Host: {url_split.hostname}\r\n"
                   f"Content-Type: {type}\r\n"
                   f"Content-Length: {length}"
                   f"\r\n"
                   f"{content}")
        print(f"Request sent: {request}")
        self.sendall(request)

        response = self.recvall(self.socket)

        code = 500
        body = ""
        headers = None

        if response:
            code = self.get_code(response)
            body = self.get_body(response)
            headers = self.get_headers(response)
            return HTTPResponse(code, headers, body)
        else:
            print("Message has not been received. Perhaps the connection was lost?")
            return None

    def command(self, url, command="GET", args=None):
        if command == "POST":
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if len(sys.argv) <= 1:
        help()
        sys.exit(1)
    elif len(sys.argv) == 3:
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
