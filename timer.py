import threading
import time


class Timer(threading.Thread):
    def __init__(self, timeout=60, exe=None, exe_args=None):
        threading.Thread.__init__(self)
        self.exe = exe
        self.exe_args = exe_args

        self.event = threading.Event()
        self.count = timeout


    def run(self):
        while self.count > 0 and not self.event.is_set():
            self.count -= 1
            self.event.wait(1)

        if self.exe is not None:
            if self.exe_args is not None:
                self.execute(self.exe(self.exe_args))
            else:
                self.execute(self.exe())


        self.stop()


    def stop(self):
        self.exe = None
        self.exe_args = None
        self.event.set()


    def execute(self, fun=None, *args):
        try:
            fun(*args)
        except:
            return None
