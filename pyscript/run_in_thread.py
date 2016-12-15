import threading
import time


class run_in_thread(threading.Thead):
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.daemon = True

    def run(self):
        self.func(*self.args, **self.kwargs)

def test_func(s):
    time.sleep(s)


if __name__ == '__main__':
    t = run_in_thread(test_func, 10)
    t.start()
    t.join()
