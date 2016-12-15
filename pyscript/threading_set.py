import time
import logging
import threading
from threading import Event

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def worker(event):
    logger.error('Service is down...')
    while not event.is_set():
        logger.debug('Watting service recovery...')
        event.wait(2)
    logger.debug('Service recovery success...')

def CheckService(event):
    time.sleep(3)
    logger.debug('Checked service recovery...')
    event.set()

if __name__ == '__main__':
    event = Event()
    t1 = threading.Thread(target=worker, args=(event,), name='worker')
    t1.start()
    t2 = threading.Thread(target=CheckService, args=(event,), name='checker')
    t2.start()
