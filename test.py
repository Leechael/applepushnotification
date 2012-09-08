import gevent.monkey; gevent.monkey.patch_all()

import unittest

import gevent

import applepushnotification as apn

original_gevent_sleep = gevent.sleep
send_signal = True


class FakeConnection(object):

    def __init__(self, *args, **kwargs):
        pass

    def connect_ex(self, *args, **kwargs):
        return self

    def send(self, msg):
        global send_signal
        if send_signal:
            original_gevent_sleep(0)
        else:
            raise Exception('Mock Sending Error')

    def recv(self, length):
        while True:
            original_gevent_sleep(0)

    def close(self):
        pass

    def set_no_send(self, new_val):
        self.no_send = new_val


class TestApplePushNotification(unittest.TestCase):

    def setUp(self):
        self._sleep = apn.gevent.sleep
        apn.gevent.sleep = self.mock_sleep
        self.last_sleep = 0

        self._wrap_socket = apn.ssl.wrap_socket
        apn.ssl.wrap_socket = FakeConnection

        self.msg = apn.NotificationMessage('1' * 32, 'hello')

        self.service = apn.NotificationService(certfile='PEM')
        self.service.start()
        self.service.send(self.msg)

    def tearDown(self):
        apn.gevent.sleep = self._sleep
        apn.ssl.wrap_socket = self._wrap_socket
        self.service._send_queue.queue.clear()

    def mock_sleep(self, seconds):
        original_gevent_sleep(0)

    def test_successful_send(self):
        global send_signal
        send_signal = True
        self.assertEqual(self.service._send_queue.qsize(), 1)
        original_gevent_sleep(0)
        self.assertEqual(self.service._send_queue.qsize(), 0)

    def test_failed_send(self):
        global send_signal
        send_signal = False
        self.assertEqual(self.service._send_queue.qsize(), 1)
        original_gevent_sleep(0)
        self.assertEqual(self.service._send_queue.qsize(), 1)

    def test_fabonacci_timeout(self):
        global send_signal
        send_signal = False
        self.assertEqual(self.service._send_queue.qsize(), 1)
        original_gevent_sleep(0)
        self.assertEqual(self.service._send_queue.qsize(), 1)
        self.assertEqual(self.service.timeout, 5)
        original_gevent_sleep(0)
        self.assertEqual(self.service._send_queue.qsize(), 1)
        self.assertEqual(self.service.timeout, 8)

    def test_max_timeout(self):
        global send_signal
        send_signal = False
        # test max timeout
        for _ in range(100):
            original_gevent_sleep(0)
        self.assertEqual(self.service._send_queue.qsize(), 1)
        self.assertEqual(self.service.timeout, 600)

    def test_timeout_reset(self):
        global send_signal
        send_signal = False
        self.assertEqual(self.service._send_queue.qsize(), 1)
        original_gevent_sleep(0)
        original_gevent_sleep(0)
        self.assertEqual(self.service._send_queue.qsize(), 1)
        self.assertEqual(self.service.timeout, 8)

        send_signal = True
        original_gevent_sleep(0)
        original_gevent_sleep(0)
        self.assertEqual(self.service._send_queue.qsize(), 0)
        self.assertEqual(self.service.timeout, 5)


if __name__ == '__main__':
    unittest.main()

