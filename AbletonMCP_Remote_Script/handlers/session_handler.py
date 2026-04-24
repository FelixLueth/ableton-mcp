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

    def stop_playback(self):
        try:
            self._song.stop_playing()
            return {"playing": self._song.is_playing}
        except Exception as e:
            self._logger.error("Error stopping playback: " + str(e))
            raise
