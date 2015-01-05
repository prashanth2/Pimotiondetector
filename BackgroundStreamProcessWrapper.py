import threading

class BackgroundStreamProcessWrapper(threading.Thread):
    def __init__(self, what_to_process, stream, event_id=None, close_stream=False):
        super(BackgroundStreamProcessWrapper, self).__init__()
        self._what_to_process = what_to_process
        self._stream = stream
        self._event_id = event_id
        self._close_stream = close_stream
        self.daemon = True
        self.start()

    def run(self):

        self._stream.seek(0)

        self._what_to_process(self._stream, self._event_id)

        self._stream.seek(0)
        self._stream.truncate()

        if(self._close_stream):
            self._stream.close()