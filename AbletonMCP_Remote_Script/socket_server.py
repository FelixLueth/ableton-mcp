from __future__ import absolute_import, print_function, unicode_literals

import socket
import threading
import json
import time
import traceback


DEFAULT_PORT = 9877
HOST = "localhost"


class SocketServer(object):
    def __init__(self, host=HOST, port=DEFAULT_PORT):
        self._host = host
        self._port = port
        self._server = None
        self._server_thread = None
        self._client_threads = []
        self._running = False
        self._command_callback = None
        self._log_callback = None

    def set_log_callback(self, callback):
        self._log_callback = callback

    def set_command_callback(self, callback):
        self._command_callback = callback

    def start(self):
        if self._running:
            return

        try:
            self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server.bind((self._host, self._port))
            self._server.listen(5)

            self._running = True
            self._server_thread = threading.Thread(target=self._server_loop)
            self._server_thread.daemon = True
            self._server_thread.start()

            self._log("Server started on port {0}".format(self._port))
        except Exception as e:
            self._log("Error starting server: " + str(e))
            raise

    def stop(self):
        self._running = False

        if self._server:
            try:
                self._server.close()
            except:
                pass

        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(1.0)

        for client_thread in self._client_threads[:]:
            if client_thread.is_alive():
                self._log("Client thread still alive during stop")

        self._log("Server stopped")

    def _log(self, message):
        if self._log_callback:
            self._log_callback(message)

    def _server_loop(self):
        self._log("Server thread started")
        self._server.settimeout(1.0)

        while self._running:
            try:
                client, address = self._server.accept()
                self._log("Connection accepted from " + str(address))

                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client,)
                )
                client_thread.daemon = True
                client_thread.start()

                self._client_threads.append(client_thread)
                self._client_threads = [t for t in self._client_threads if t.is_alive()]

            except socket.timeout:
                continue
            except Exception as e:
                if self._running:
                    self._log("Server accept error: " + str(e))
                time.sleep(0.5)

        self._log("Server thread stopped")

    def _handle_client(self, client):
        self._log("Client handler started")
        client.settimeout(None)
        buffer = ''

        try:
            while self._running:
                try:
                    data = client.recv(8192)

                    if not data:
                        self._log("Client disconnected")
                        break

                    try:
                        buffer += data.decode('utf-8')
                    except AttributeError:
                        buffer += data

                    try:
                        command = json.loads(buffer)
                        buffer = ''

                        self._log("Received command: " + str(command.get("type", "unknown")))

                        if self._command_callback:
                            response = self._command_callback(command)
                        else:
                            response = {"status": "error", "message": "No command callback"}

                        try:
                            client.sendall(json.dumps(response).encode('utf-8'))
                        except AttributeError:
                            client.sendall(json.dumps(response))

                    except ValueError:
                        continue

                except Exception as e:
                    self._log("Error handling client data: " + str(e))

                    error_response = {"status": "error", "message": str(e)}
                    try:
                        client.sendall(json.dumps(error_response).encode('utf-8'))
                    except AttributeError:
                        client.sendall(json.dumps(error_response))
                    except:
                        break

                    if not isinstance(e, ValueError):
                        break

        except Exception as e:
            self._log("Error in client handler: " + str(e))
        finally:
            try:
                client.close()
            except:
                pass
            self._log("Client handler stopped")