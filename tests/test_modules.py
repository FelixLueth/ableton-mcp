# Unit tests for MCP Server modules
# Can run without Ableton Live installed

import unittest
import sys
import os

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


if __name__ == "__main__":
    unittest.main()