import gevent.monkey; gevent.monkey.patch_all()

import sys

import applepushnotification


def main():
    service = applepushnotification.NotificationService(certfile=sys.argv[1])
    service.start()

    token = sys.argv[2].decode('hex')

    message = applepushnotification.NotificationMessage(token, u'hello')

    service.send(message)
    if service.wait_send(5):
        print('Succeed!')
    else:
        print('Failed!')
        print(service.get_last_error())
    service.stop()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('%s [pemfile] [push-token]' % sys.argv[0])
        sys.exit(1)
    main()

