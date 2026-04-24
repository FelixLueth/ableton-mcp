# Mock Ableton TCP Server for Testing
# Used to test MCP server behavior without Ableton Live running

import socket
import threading
import json
import logging

logger = logging.getLogger("MockAbleton")


class MockAbletonServer:
    """Mock TCP server that simulates Ableton Remote Script responses"""
    
    def __init__(self, host: str = "localhost", port: int = 9877):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.thread = None
        self.received_commands = []
        
    def start(self):
        """Start the mock server"""
        if self.running:
            return
            
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.server_socket.settimeout(5.0)
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info(f"Mock Ableton server started on {self.host}:{self.port}")
        
    def stop(self):
        """Stop the mock server"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        if self.thread:
            self.thread.join(timeout=2.0)
        logger.info("Mock Ableton server stopped")
        
    def _run(self):
        """Main server loop"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True
                ).start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    logger.error(f"Server error: {e}")
                    
    def _handle_client(self, client_socket):
        """Handle client connection"""
        try:
            data = b""
            client_socket.settimeout(5.0)
            
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                try:
                    json.loads(data.decode('utf-8'))
                    break
                except json.JSONDecodeError:
                    continue
            
            if data:
                command = json.loads(data.decode('utf-8'))
                self.received_commands.append(command)
                
                response = self._generate_response(command)
                client_socket.sendall(json.dumps(response).encode('utf-8'))
                
        except Exception as e:
            logger.error(f"Client handler error: {e}")
        finally:
            client_socket.close()
            
    def _generate_response(self, command: dict) -> dict:
        """Generate response to command"""
        cmd_type = command.get("type", "")
        params = command.get("params", {})
        
        responses = {
            "get_session_info": {
                "status": "ok",
                "result": {
                    "tempo": 120.0,
                    "time_signature": "4/4",
                    "track_count": 2,
                    "tracks": [
                        {"name": "Track 1", "type": "MIDI", "muted": False, "soloed": False, "armed": False},
                        {"name": "Track 2", "type": "MIDI", "muted": False, "soloed": False, "armed": False}
                    ]
                }
            },
            "get_track_info": {
                "status": "ok",
                "result": {
                    "name": f"Track {params.get('track_index', 0) + 1}",
                    "type": "MIDI",
                    "muted": False,
                    "soloed": False,
                    "armed": False,
                    "volume": 0.0,
                    "panning": 0.0,
                    "clip_slots": [],
                    "devices": []
                }
            },
            "create_midi_track": {
                "status": "ok",
                "result": {"name": "New MIDI Track"}
            },
            "set_track_name": {
                "status": "ok",
                "result": {"name": params.get("name", "Renamed Track")}
            },
            "set_tempo": {
                "status": "ok",
                "result": {"tempo": params.get("tempo", 120.0)}
            },
            "create_clip": {"status": "ok", "result": {}},
            "add_notes_to_clip": {"status": "ok", "result": {"notes_added": len(params.get("notes", []))}},
            "set_clip_name": {"status": "ok", "result": {"name": params.get("name", "")}},
            "fire_clip": {"status": "ok", "result": {}},
            "stop_clip": {"status": "ok", "result": {}},
            "start_playback": {"status": "ok", "result": {}},
            "stop_playback": {"status": "ok", "result": {}},
            "get_browser_tree": {
                "status": "ok",
                "result": {
                    "categories": [
                        {
                            "name": "Instruments",
                            "path": "instruments",
                            "children": [],
                            "has_more": False
                        }
                    ]
                }
            },
            "get_browser_items_at_path": {
                "status": "ok",
                "result": {
                    "items": [
                        {"name": "Test Synth", "is_loadable": True, "uri": "test:synth"}
                    ]
                }
            },
            "load_browser_item": {
                "status": "ok",
                "result": {"loaded": True, "new_devices": ["Test Device"]}
            }
        }
        
        return responses.get(cmd_type, {"status": "error", "message": f"Unknown command: {cmd_type}"})


def run_mock_server():
    """Run the mock server for manual testing"""
    import time
    server = MockAbletonServer()
    server.start()
    print("Mock Ableton server running on port 9877. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_mock_server()