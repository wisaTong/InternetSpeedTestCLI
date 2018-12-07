try:
    from httplib import HTTPConnection
except ImportError:
    from http.client import HTTPConnection

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

import random
import itertools
import string

from time import time
from threading import currentThread, Thread

class SpeedTest(object):

  DOWNLOAD_FILES = [
    '/speedtest/random350x350.jpg',
    '/speedtest/random500x500.jpg',
    '/speedtest/random1500x1500.jpg'
  ]

  UPLOAD_FILES = [
    # 132884,
    # 493638
    100
  ]

  ALPHABET = string.digits + string.ascii_letters

  def __init__(self, host=None, http_debug=0, runs=2):
    self._host = host
    self.http_debug = http_debug
    self.runs = runs

  def connect(self, url):
    try:
      connection = HTTPConnection(url)
      connection.set_debuglevel(self.http_debug)
      connection.connect()
      return connection
    except:
      raise Exception(f'Unable to connect to {url}')

  def downloadthread(self, connection, url):
    connection.request('GET', url, None, {'Connection': 'Keep-Alive'})
    response = connection.getresponse()
    self_thread = currentThread()
    self_thread.downloaded = len(response.read())
  
  def uploadthread(self, connection, data):
    url = f'/speedtest/upload.php?x={randint()}'
    connection.request('POST', url, data, {
        'Connection': 'Keep-Alive',
        'Content-Type': 'application/x-www-form-urlencoded'
    })
    response = connection.getresponse()
    reply = response.read().decode('utf-8')
    self_thread = currentThread()
    print(reply)
    self_thread.uploaded = int(reply.split('=')[1])

  def ping(self, server=None):
    if not server:
      server = self._host

    connection = self.connect(server)
    times = []
    worst = 0

    for _ in range(5):
      total_start_time = time()
      connection.request(
        'GET',
        '/speedtest/latency.txt?x=%d' % randint(),
        None,
        {'Connection': 'Keep-Alive'})
      response = connection.getresponse()
      response.read()
      total_ms = time() - total_start_time
      times.append(total_ms)
      if total_ms > worst:
        worst = total_ms

    times.remove(worst)
    total_ms = sum(times) * 250  # * 1000 / number of tries (4) = 250
    connection.close()

    return total_ms

  def download(self):
    total_downloaded = 0
    connections = [
      self.connect(self._host) for i in range(self.runs)
    ]
    total_start_time = time()
    for current_file in SpeedTest.DOWNLOAD_FILES:
      threads = []
      for run in range(self.runs):
        thread = Thread(
          target=self.downloadthread,
          args=(connections[run],
          '%s?x=%d' % (current_file, int(time() * 1000))))
        thread.run_number = run + 1
        thread.start()
        threads.append(thread)
      for thread in threads:
        thread.join()
        total_downloaded += thread.downloaded
    total_ms = (time() - total_start_time) * 1000
    for connection in connections:
            connection.close()
    return total_downloaded * 8000 / total_ms

  def upload(self):
    connections = [
      self.connect(self._host) for i in range(self.runs)
    ]

    post_data = [
      urlencode({'content0': content(s)}) for s in SpeedTest.UPLOAD_FILES
    ]

    total_uploaded = 0
    total_start_time = time()
    for data in post_data:
      threads = []
      for run in range(self.runs):
        thread = Thread(target=self.uploadthread,
          args=(connections[run], data))
        thread.run_number = run + 1
        thread.start()
        threads.append(thread)
      for thread in threads:
        thread.join()
        total_uploaded += thread.uploaded
      total_ms = (time() - total_start_time) * 1000
    for connection in connections:
          connection.close()
      
    return total_uploaded * 8000 / total_ms


def randint():
    return random.randint(100000000000, 999999999999)

def pretty_speed(speed):
    units = ['bps', 'Kbps', 'Mbps', 'Gbps']
    unit = 0
    while speed >= 1024:
        speed /= 1024
        unit += 1
    return '%0.2f %s' % (speed, units[unit])

def content(length):
    cycle = itertools.cycle(SpeedTest.ALPHABET)
    return ''.join(next(cycle) for i in range(length))

def main(args=None):
    speedtest = SpeedTest('c.speedtest.net')
    # print(f'Upload speed: {pretty_speed(speedtest.upload())}')
    wwwspeedtest = SpeedTest('www.speedtest.net')
    comm = ''
    while comm is not 'x':
      print('[p] to check your ping')
      print('[d] to check your download speed')
      print('[u] to check your upload speed')
      print('\n[x] to exit')
      comm = input('enter your command: ')

      if comm is 'p':
        print(f'\nPinging...\r', end='')
        print(f'Ping: {speedtest.ping():.2f} ms\n')
      if comm is 'd':
        print(f'\nDownloading...\r', end='')
        print(f'Download speed: {pretty_speed(speedtest.download())}\n')
      if comm is 'u':
        print(f'\nUnder construction\n')
        # print(f'Upload speed: {pretty_speed(wwwspeedtest.upload())}\n')

if __name__ == '__main__':
    main()
