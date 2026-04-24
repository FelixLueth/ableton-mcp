# Unit tests for MCP Server modules
# Can run without Ableton Live installed

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add the parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import directly from the modules without going through MCP_Server/__init__.py
from MCP_Server.connection import AbletonConnection, DEFAULT_HOST, DEFAULT_PORT
from MCP_Server.clip_helpers import validate_notes, DRUM_NOTES, create_drum_pattern
from MCP_Server.browser_helpers import validate_category, BROWSER_CATEGORIES


class TestConnection(unittest.TestCase):
    """Test connection module"""

    def test_default_host(self):
        """Test default host is localhost"""
        conn = AbletonConnection(host=DEFAULT_HOST, port=DEFAULT_PORT)
        self.assertEqual(conn.host, "localhost")
        self.assertEqual(conn.port, 9877)

    def test_connection_not_connected_initially(self):
        """Test connection starts as not connected"""
        conn = AbletonConnection(host="localhost", port=9877)
        self.assertIsNone(conn.sock)


class TestClipHelpers(unittest.TestCase):
    """Test clip helpers"""

    def test_validate_notes_valid(self):
        """Test valid notes pass validation"""
        notes = [
            {"pitch": 60, "start_time": 0.0, "duration": 1.0},
            {"pitch": 64, "start_time": 1.0, "duration": 1.0}
        ]
        valid, error = validate_notes(notes)
        self.assertTrue(valid)

    def test_validate_notes_invalid_pitch(self):
        """Test invalid pitch fails"""
        notes = [{"pitch": 200, "start_time": 0.0, "duration": 1.0}]
        valid, error = validate_notes(notes)
        self.assertFalse(valid)
        self.assertIn("pitch", error.lower())

    def test_validate_notes_missing_field(self):
        """Test missing required field fails"""
        notes = [{"pitch": 60}]
        valid, error = validate_notes(notes)
        self.assertFalse(valid)
        self.assertIn("field", error.lower())

    def test_validate_notes_invalid_velocity(self):
        """Test invalid velocity fails"""
        notes = [{"pitch": 60, "start_time": 0.0, "duration": 1.0, "velocity": 200}]
        valid, error = validate_notes(notes)
        self.assertFalse(valid)
        self.assertIn("velocity", error.lower())

    def test_drum_notes_constant(self):
        """Test drum notes are defined"""
        self.assertIn("kick", DRUM_NOTES)
        self.assertIn("snare", DRUM_NOTES)
        self.assertEqual(DRUM_NOTES["kick"], 36)

    def test_create_drum_pattern(self):
        """Test drum pattern creation"""
        pattern = "x.|.x.|..|.."
        notes = create_drum_pattern(pattern)
        self.assertIsInstance(notes, list)
        for note in notes:
            self.assertIn("pitch", note)
            self.assertIn("start_time", note)
            self.assertIn("duration", note)
            self.assertIn("velocity", note)


class TestBrowserHelpers(unittest.TestCase):
    """Test browser helpers"""

    def test_validate_category_valid(self):
        """Test valid categories pass"""
        for category in BROWSER_CATEGORIES:
            self.assertTrue(validate_category(category))
        self.assertTrue(validate_category("all"))

    def test_validate_category_invalid(self):
        """Test invalid category fails"""
        self.assertFalse(validate_category("invalid"))
        self.assertFalse(validate_category(""))


class TestGetFullSessionState(unittest.TestCase):
    """Test get_full_session_state tool"""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_successful_response(self, mock_get_conn):
        """Test successful response handling"""
        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "ok": True,
            "session": {
                "tempo": 120.0,
                "track_count": 1
            },
            "tracks": [
                {
                    "index": 0,
                    "name": "Drums",
                    "type": "midi",
                    "clip_slots": [{"index": 0, "has_clip": True}],
                    "devices": []
                }
            ]
        }
        mock_get_conn.return_value = mock_conn

        from MCP_Server.server import get_full_session_state
        from mcp.server.fastmcp import Context

        mock_ctx = MagicMock(spec=Context)
        result = get_full_session_state(mock_ctx)

        parsed = json.loads(result)
        self.assertTrue(parsed.get("ok"))
        self.assertIn("session", parsed)
        self.assertEqual(parsed["session"]["tempo"], 120.0)
        self.assertEqual(len(parsed["tracks"]), 1)

    @patch('MCP_Server.server.get_ableton_connection')
    def test_error_response_from_remote_script(self, mock_get_conn):
        """Test error handling when Remote Script returns error"""
        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "ok": False,
            "error": {
                "code": "SESSION_STATE_COLLECTION_FAILED",
                "message": "Failed to collect session state",
                "details": "Unexpected error"
            }
        }
        mock_get_conn.return_value = mock_conn

        from MCP_Server.server import get_full_session_state
        from mcp.server.fastmcp import Context

        mock_ctx = MagicMock(spec=Context)
        result = get_full_session_state(mock_ctx)

        parsed = json.loads(result)
        self.assertFalse(parsed.get("ok"))
        self.assertIn("error", parsed)
        self.assertEqual(parsed["error"]["code"], "SESSION_STATE_COLLECTION_FAILED")

    @patch('MCP_Server.server.get_ableton_connection')
    def test_ableton_not_reachable(self, mock_get_conn):
        """Test Ableton not reachable error handling"""
        mock_get_conn.side_effect = Exception("Connection refused")

        from MCP_Server.server import get_full_session_state
        from mcp.server.fastmcp import Context

        mock_ctx = MagicMock(spec=Context)
        result = get_full_session_state(mock_ctx)

        parsed = json.loads(result)
        self.assertFalse(parsed.get("ok"))
        self.assertIn("error", parsed)
        self.assertEqual(parsed["error"]["code"], "ableton_not_running")
        self.assertIn("Ableton is not reachable", parsed["error"]["message"])

    @patch('MCP_Server.server.get_ableton_connection')
    def test_response_schema_structure(self, mock_get_conn):
        """Test response has correct schema structure"""
        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "ok": True,
            "session": {
                "tempo": 174.0,
                "track_count": 3
            },
            "tracks": [
                {
                    "index": 0,
                    "name": "Drums",
                    "type": "midi",
                    "is_foldable": False,
                    "has_midi_input": True,
                    "has_audio_input": False,
                    "clip_slots": [
                        {
                            "index": 0,
                            "has_clip": True,
                            "clip": {
                                "name": "Amen Loop",
                                "is_audio_clip": False,
                                "is_midi_clip": True,
                                "length": 4.0,
                                "is_playing": False,
                                "is_recording": False
                            }
                        }
                    ],
                    "devices": [
                        {
                            "index": 0,
                            "name": "Drum Rack",
                            "class_name": "DrumGroupDevice",
                            "type": "drum_machine",
                            "is_active": True
                        }
                    ]
                }
            ]
        }
        mock_get_conn.return_value = mock_conn

        from MCP_Server.server import get_full_session_state
        from mcp.server.fastmcp import Context

        mock_ctx = MagicMock(spec=Context)
        result = get_full_session_state(mock_ctx)

        parsed = json.loads(result)

        self.assertTrue(parsed.get("ok"))
        self.assertIn("session", parsed)
        self.assertIn("tempo", parsed["session"])
        self.assertIn("track_count", parsed["session"])
        self.assertIn("tracks", parsed)

        track = parsed["tracks"][0]
        self.assertIn("index", track)
        self.assertIn("name", track)
        self.assertIn("type", track)
        self.assertIn("clip_slots", track)
        self.assertIn("devices", track)

        clip_slot = track["clip_slots"][0]
        self.assertIn("index", clip_slot)
        self.assertIn("has_clip", clip_slot)
        if clip_slot.get("has_clip"):
            self.assertIn("clip", clip_slot)
            clip_data = clip_slot["clip"]
            self.assertIn("name", clip_data)
            self.assertIn("is_audio_clip", clip_data)
            self.assertIn("is_midi_clip", clip_data)
            self.assertIn("length", clip_data)
            self.assertIn("is_playing", clip_data)
            self.assertIn("is_recording", clip_data)

        device = track["devices"][0]
        self.assertIn("index", device)
        self.assertIn("name", device)
        self.assertIn("class_name", device)
        self.assertIn("type", device)
        self.assertIn("is_active", device)


if __name__ == "__main__":
    unittest.main()
