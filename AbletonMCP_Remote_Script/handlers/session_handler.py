from __future__ import print_function, unicode_literals


class SessionHandler(object):
    def __init__(self, song, app, logger):
        self._song = song
        self._app = app
        self._logger = logger

    def get_session_info(self):
        try:
            return {
                "tempo": self._song.tempo,
                "signature_numerator": self._song.signature_numerator,
                "signature_denominator": self._song.signature_denominator,
                "track_count": len(self._song.tracks),
                "return_track_count": len(self._song.return_tracks),
                "master_track": {
                    "name": "Master",
                    "volume": self._song.master_track.mixer_device.volume.value,
                    "panning": self._song.master_track.mixer_device.panning.value
                }
            }
        except Exception as e:
            self._logger.error("Error getting session info: " + str(e))
            raise

    def set_tempo(self, tempo):
        try:
            self._song.tempo = tempo
            return {"tempo": self._song.tempo}
        except Exception as e:
            self._logger.error("Error setting tempo: " + str(e))
            raise

    def start_playback(self):
        try:
            self._song.start_playing()
            return {"playing": self._song.is_playing}
        except Exception as e:
            self._logger.error("Error starting playback: " + str(e))
            raise

    def get_full_session_state(self):
        """Collect full session state for LLM introspection."""
        try:
            tracks_data = []
            for track_index, track in enumerate(self._song.tracks):
                tracks_data.append(self._get_track_data(track, track_index))

            return {
                "ok": True,
                "session": {
                    "tempo": self._song.tempo,
                    "track_count": len(self._song.tracks)
                },
                "tracks": tracks_data
            }
        except Exception as e:
            self._logger.error("Error collecting session state: " + str(e))
            return {
                "ok": False,
                "error": {
                    "code": "SESSION_STATE_COLLECTION_FAILED",
                    "message": "Failed to collect session state",
                    "details": str(e)
                }
            }

    def _get_track_data(self, track, track_index):
        """Collect track data."""
        try:
            clip_slots = self._get_clip_slots(track)
            devices = self._get_devices(track)

            return {
                "index": track_index,
                "name": track.name,
                "type": self._get_track_type(track),
                "is_foldable": getattr(track, "is_foldable", None),
                "has_midi_input": track.has_midi_input,
                "has_audio_input": track.has_audio_input,
                "clip_slots": clip_slots,
                "devices": devices
            }
        except Exception as e:
            self._logger.error("Error collecting track data: " + str(e))
            return {
                "index": track_index,
                "name": getattr(track, "name", "Unknown"),
                "type": "unknown",
                "clip_slots": [],
                "devices": []
            }

    def _get_track_type(self, track):
        """Determine track type."""
        if track.is_foldable:
            return "group"
        if track.has_audio_input and not track.has_midi_input:
            return "audio"
        if track.has_midi_input:
            return "midi"
        return "unknown"

    def _get_clip_slots(self, track):
        """Collect clip slots for a track."""
        slots = []
        try:
            for slot_index, slot in enumerate(track.clip_slots):
                slot_data = {
                    "index": slot_index,
                    "has_clip": slot.has_clip
                }
                if slot.has_clip:
                    try:
                        clip = slot.clip
                        slot_data["clip"] = self._get_clip_data(clip)
                    except Exception as e:
                        self._logger.error("Error getting clip data: " + str(e))
                slots.append(slot_data)
        except Exception as e:
            self._logger.error("Error collecting clip slots: " + str(e))
        return slots

    def _get_clip_data(self, clip):
        """Collect clip data."""
        try:
            return {
                "name": clip.name,
                "is_audio_clip": clip.is_audio_clip,
                "is_midi_clip": clip.is_midi_clip,
                "length": clip.length,
                "is_playing": clip.is_playing,
                "is_recording": clip.is_recording
            }
        except Exception as e:
            self._logger.error("Error getting clip properties: " + str(e))
            return {"name": getattr(clip, "name", "Unknown")}

    def _get_devices(self, track):
        """Collect devices for a track."""
        devices = []
        try:
            for device_index, device in enumerate(track.devices):
                try:
                    device_data = {
                        "index": device_index,
                        "name": device.name,
                        "class_name": device.class_name,
                        "type": self._get_device_type(device),
                        "is_active": device.is_active
                    }
                    devices.append(device_data)
                except Exception as e:
                    self._logger.error("Error getting device data: " + str(e))
                    devices.append({
                        "index": device_index,
                        "name": "Unknown Device"
                    })
        except Exception as e:
            self._logger.error("Error collecting devices: " + str(e))
        return devices

    def _get_device_type(self, device):
        """Determine device type."""
        try:
            if device.can_have_drum_pads:
                return "drum_machine"
            elif device.can_have_chains:
                return "rack"
            elif "instrument" in device.class_display_name.lower():
                return "instrument"
            elif "audio_effect" in device.class_name.lower():
                return "audio_effect"
            elif "midi_effect" in device.class_name.lower():
                return "midi_effect"
            return "unknown"
        except Exception:
            return "unknown"

    def stop_playback(self):
        try:
            self._song.stop_playing()
            return {"playing": self._song.is_playing}
        except Exception as e:
            self._logger.error("Error stopping playback: " + str(e))
            raise
