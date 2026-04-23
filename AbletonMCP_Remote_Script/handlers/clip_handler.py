from __future__ import print_function, unicode_literals


class ClipHandler(object):
    def __init__(self, song, logger):
        self._song = song
        self._logger = logger

    def create_clip(self, track_index, clip_index, length):
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            if clip_slot.has_clip:
                raise Exception("Clip slot already has a clip")

            clip_slot.create_clip(length)

            return {"name": clip_slot.clip.name, "length": clip_slot.clip.length}
        except Exception as e:
            self._logger.error("Error creating clip: " + str(e))
            raise

    def add_notes_to_clip(self, track_index, clip_index, notes):
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            clip = clip_slot.clip

            live_notes = []
            for note in notes:
                pitch = note.get("pitch", 60)
                start_time = note.get("start_time", 0.0)
                duration = note.get("duration", 0.25)
                velocity = note.get("velocity", 100)
                mute = note.get("mute", False)
                live_notes.append((pitch, start_time, duration, velocity, mute))

            clip.set_notes(tuple(live_notes))

            return {"note_count": len(notes)}
        except Exception as e:
            self._logger.error("Error adding notes to clip: " + str(e))
            raise

    def set_clip_name(self, track_index, clip_index, name):
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            clip = clip_slot.clip
            clip.name = name

            return {"name": clip.name}
        except Exception as e:
            self._logger.error("Error setting clip name: " + str(e))
            raise

    def fire_clip(self, track_index, clip_index):
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            clip_slot.fire()

            return {"fired": True}
        except Exception as e:
            self._logger.error("Error firing clip: " + str(e))
            raise

    def stop_clip(self, track_index, clip_index):
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            clip_slot.stop()

            return {"stopped": True}
        except Exception as e:
            self._logger.error("Error stopping clip: " + str(e))
            raise