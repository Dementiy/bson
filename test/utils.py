import threading


class ExceptionCatchingThread(threading.Thread):
    """A thread that stores any exception encountered from run()."""

    def __init__(self, *args, **kwargs):
        self.exc = None
        super().__init__(*args, **kwargs)

    def run(self):
        try:
            super().run()
        except BaseException as exc:
            self.exc = exc
            raise