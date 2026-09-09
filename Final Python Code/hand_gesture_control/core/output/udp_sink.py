import socket
from .base_sink import OutputSink
from ..command import Command


class UDPSink(OutputSink):
    def __init__(self, ip="192.168.1.150", port=4210, categories=None, stability_count=2):
        super().__init__(categories)
        self.addr = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._last_sent_code = None
        self._candidate_code = None
        self._candidate_count = 0
        self._stability_count = stability_count

    def emit(self, command: Command):
        if not self.should_emit(command):
            return
        code = command.code
        if code == self._candidate_code:
            self._candidate_count += 1
        else:
            self._candidate_code = code
            self._candidate_count = 1
        if self._candidate_count < self._stability_count:
            return
        if code == self._last_sent_code:
            return
        self._last_sent_code = code
        try:
            self.sock.sendto(str(code).encode("utf-8"), self.addr)
            print(f"[UDPSink] ارسال شد: {code}")
        except OSError as e:
            print(f"[UDPSink] خطا: {e}")

    def close(self):
        self.sock.close()