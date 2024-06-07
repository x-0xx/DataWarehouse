# -*- encoding: utf-8 -*-
import socket
import struct
import time
import logging


# 装饰器
class Singleton(object):
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}

    def __call__(self, *args, **kwargs):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls(*args, **kwargs)
        return self._instance[self._cls]


EPOCH_TIMESTAMP = 1288834974657


@Singleton
class Generator(object):
    def __init__(self, worker):
        self.datacenter_id = self._get_datacenter_id()
        self.worker = worker
        self.node_id = ((self.datacenter_id & 0x03) << 8) | (worker & 0xff)
        self.last_timestamp = EPOCH_TIMESTAMP
        self.sequence = 0
        self.sequence_overload = 0
        self.errors = 0
        self.generated_ids = 0

    def snow_flake(self):
        curr_time = int(time.time() * 1000)

        if curr_time < self.last_timestamp:
            # stop handling requests til we've caught back up
            self.errors += 1

        if curr_time > self.last_timestamp:
            self.sequence = 0
            self.last_timestamp = curr_time

        self.sequence += 1

        if self.sequence > 4095:
            # the sequence is overload, just wait to next sequence
            logging.warning('The sequence has been overload')
            self.sequence_overload += 1
            time.sleep(0.001)
            return self.get_next_id()

        generated_id = ((curr_time - EPOCH_TIMESTAMP) <<
                        22) | (self.node_id << 12) | self.sequence

        self.generated_ids += 1
        return generated_id

    @property
    def stats(self):
        return {
            'datacenter_id': self.datacenter_id,
            'worker': self.worker,
            # current timestamp for this worker
            'timestamp': int(time.time() * 1000),
            # the last timestamp that generated ID on
            'last_timestamp': self.last_timestamp,
            'sequence': self.sequence,  # the sequence number for last timestamp
            # the number of times that the sequence is overflow
            'sequence_overload': self.sequence_overload,
            'errors': self.errors,  # the number of times that clock went backward
        }

    def _get_datacenter_id(self):
        """get local ip to number as datacenter_id"""
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except:
            ip = ""
        finally:
            if s:
                s.close()
        return socket.ntohl(struct.unpack("I", socket.inet_aton(ip))[0])
