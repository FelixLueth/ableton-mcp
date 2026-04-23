from __future__ import absolute_import, print_function, unicode_literals

from _Framework.ControlSurface import ControlSurface

from .socket_server import SocketServer, DEFAULT_PORT
from .command_router import CommandRouter
from .handlers.session_handler import SessionHandler
from .handlers.track_handler import TrackHandler
from .handlers.clip_handler import ClipHandler
from .handlers.browser_handler import BrowserHandler
from .utils.logger import Logger


class AbletonMCPControlSurface(ControlSurface):
    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self._log = Logger(self)
        self._log.log("AbletonMCP Remote Script initializing...")

        self._app = self.application()
        self._song = self.song()

        self._session_handler = SessionHandler(self._song, self._app, self._log)
        self._track_handler = TrackHandler(self._song, self._log)
        self._clip_handler = ClipHandler(self._song, self._log)
        self._browser_handler = BrowserHandler(self._app, self._song, self._log)

        self._command_router = CommandRouter(
            self._session_handler,
            self._track_handler,
            self._clip_handler,
            self._browser_handler,
            self._log
        )

        self._server = SocketServer()
        self._server.set_log_callback(self._log.log)
        self._server.set_command_callback(self._process_command)
        self._server.start()

        self._log.log("AbletonMCP initialized")
        self.show_message("AbletonMCP: Listening for commands on port " + str(DEFAULT_PORT))

    def disconnect(self):
        self._log.log("AbletonMCP disconnecting...")
        self._server.stop()
        ControlSurface.disconnect(self)
        self._log.log("AbletonMCP disconnected")

    def _process_command(self, command):
        return self._command_router.route(command, self.schedule_message)