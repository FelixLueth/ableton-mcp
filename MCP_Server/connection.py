import socket
import json
import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AbletonMCPServer")

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9877
DEFAULT_TIMEOUT = 15.0


@dataclass
class AbletonConnection:
    host: str
    port: int
    sock: Optional[socket.socket] = None

    def connect(self) -> bool:
        if self.sock:
            return True

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to Ableton at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ableton: {str(e)}")
            self.sock = None
            return False

    def disconnect(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                logger.error(f"Error disconnecting from Ableton: {str(e)}")
            finally:
                self.sock = None

    def _receive_full_response(self, sock: socket.socket, buffer_size: int = 8192) -> bytes:
        chunks = []
        sock.settimeout(15.0)

        try:
            while True:
                try:
                    chunk = sock.recv(buffer_size)
                    if not chunk:
                        if not chunks:
                            raise Exception("Connection closed before receiving any data")
                        break

                    chunks.append(chunk)

                    try:
                        data = b''.join(chunks)
                        json.loads(data.decode('utf-8'))
                        return data
                    except json.JSONDecodeError:
                        continue
                except socket.timeout:
                    logger.warning("Socket timeout during chunked receive")
                    break
                except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                    logger.error(f"Socket connection error during receive: {str(e)}")
                    raise
        except Exception as e:
            logger.error(f"Error during receive: {str(e)}")
            raise

        if chunks:
            data = b''.join(chunks)
            try:
                json.loads(data.decode('utf-8'))
                return data
            except json.JSONDecodeError:
                raise Exception("Incomplete JSON response received")
        else:
            raise Exception("No data received")

    def send_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Ableton")

        command = {
            "type": command_type,
            "params": params or {}
        }

        is_modifying_command = command_type in [
            "create_midi_track", "create_audio_track", "set_track_name",
            "create_clip", "add_notes_to_clip", "set_clip_name",
            "set_tempo", "fire_clip", "stop_clip", "set_device_parameter",
            "start_playback", "stop_playback", "load_instrument_or_effect"
        ]

        try:
            logger.info(f"Sending command: {command_type} with params: {params}")

            self.sock.sendall(json.dumps(command).encode('utf-8'))

            if is_modifying_command:
                import time
                time.sleep(0.1)

            timeout = 15.0 if is_modifying_command else 10.0
            self.sock.settimeout(timeout)

            response_data = self._receive_full_response(self.sock)
            response = json.loads(response_data.decode('utf-8'))

            if response.get("status") == "error":
                logger.error(f"Ableton error: {response.get('message')}")
                raise Exception(response.get("message", "Unknown error from Ableton"))

            if is_modifying_command:
                import time
                time.sleep(0.1)

            return response.get("result", {})
        except socket.timeout:
            logger.error("Socket timeout while waiting for response from Ableton")
            self.sock = None
            raise Exception("Timeout waiting for Ableton response")
        except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
            logger.error(f"Socket connection error: {str(e)}")
            self.sock = None
            raise Exception(f"Connection to Ableton lost: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Ableton: {str(e)}")
            self.sock = None
            raise Exception(f"Invalid response from Ableton: {str(e)}")
        except Exception as e:
            logger.error(f"Error communicating with Ableton: {str(e)}")
            self.sock = None
            raise Exception(f"Communication error with Ableton: {str(e)}")


class AbletonConnectionManager:
    _connection: Optional[AbletonConnection] = None

    @classmethod
    def get_connection(cls) -> AbletonConnection:
        global _connection

        if _connection is not None:
            try:
                _connection.sock.settimeout(1.0)
                _connection.sock.sendall(b'')
                return _connection
            except Exception as e:
                logger.warning(f"Existing connection is no longer valid: {str(e)}")
                try:
                    _connection.disconnect()
                except Exception:
                    pass
                _connection = None

        if _connection is None:
            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                try:
                    logger.info(f"Connecting to Ableton (attempt {attempt}/{max_attempts})...")
                    _connection = AbletonConnection(host=DEFAULT_HOST, port=DEFAULT_PORT)
                    if _connection.connect():
                        _connection.send_command("get_session_info")
                        logger.info("Connection validated successfully")
                        return _connection
                    else:
                        _connection = None
                except Exception as e:
                    logger.error(f"Connection attempt {attempt} failed: {str(e)}")
                    if _connection:
                        _connection.disconnect()
                        _connection = None

                    if attempt < max_attempts:
                        import time
                        time.sleep(1.0)

            if _connection is None:
                raise Exception("Could not connect to Ableton. Make sure the Remote Script is running.")

        return _connection

    @classmethod
    def disconnect(cls):
        global _connection
        if _connection:
            _connection.disconnect()
            _connection = None


_ableton_connection = None

def get_ableton_connection() -> AbletonConnection:
    global _ableton_connection

    if _ableton_connection is not None:
        try:
            _ableton_connection.sock.settimeout(1.0)
            _ableton_connection.sock.sendall(b'')
            return _ableton_connection
        except Exception as e:
            logger.warning(f"Existing connection is no longer valid: {str(e)}")
            try:
                _ableton_connection.disconnect()
            except Exception:
                pass
            _ableton_connection = None

    if _ableton_connection is None:
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"Connecting to Ableton (attempt {attempt}/{max_attempts})...")
                _ableton_connection = AbletonConnection(host=DEFAULT_HOST, port=DEFAULT_PORT)
                if _ableton_connection.connect():
                    _ableton_connection.send_command("get_session_info")
                    logger.info("Created new persistent connection to Ableton")
                    return _ableton_connection
                else:
                    _ableton_connection = None
            except Exception as e:
                logger.error(f"Connection attempt {attempt} failed: {str(e)}")
                if _ableton_connection:
                    _ableton_connection.disconnect()
                    _ableton_connection = None

                if attempt < max_attempts:
                    import time
                    time.sleep(1.0)

        if _ableton_connection is None:
            logger.error("Failed to connect to Ableton after multiple attempts")
            raise Exception("Could not connect to Ableton. Make sure the Remote Script is running.")

    return _ableton_connection


def create_connection(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> AbletonConnection:
    return AbletonConnection(host=host, port=port)
