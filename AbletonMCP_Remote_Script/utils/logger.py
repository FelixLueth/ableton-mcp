from __future__ import print_function, unicode_literals


class Logger(object):
    def __init__(self, control_surface):
        self._cs = control_surface

    def log(self, message):
        self._cs.log_message(message)

    def error(self, message):
        self._cs.log_message("ERROR: " + message)

    def warning(self, message):
        self._cs.log_message("WARNING: " + message)

    def debug(self, message):
        self._cs.log_message("DEBUG: " + message)