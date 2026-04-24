from __future__ import print_function, unicode_literals

try:
    import Queue as queue
except ImportError:
    import queue


MAIN_THREAD_COMMANDS = frozenset([
    "create_midi_track", "set_track_name", "create_clip", "add_notes_to_clip",
    "set_clip_name", "set_tempo", "fire_clip", "stop_clip",
    "start_playback", "stop_playback", "load_browser_item"
])


class CommandRouter(object):
    def __init__(self, session_handler, track_handler, clip_handler, browser_handler, logger):
        self._session = session_handler
        self._track = track_handler
        self._clip = clip_handler
        self._browser = browser_handler
        self._logger = logger

        self._commands = {
            "get_session_info": self._handle_get_session_info,
            "get_full_session_state": self._handle_get_full_session_state,
            "get_track_info": self._handle_get_track_info,
            "create_midi_track": self._handle_create_midi_track,
            "set_track_name": self._handle_set_track_name,
            "create_clip": self._handle_create_clip,
            "add_notes_to_clip": self._handle_add_notes_to_clip,
            "set_clip_name": self._handle_set_clip_name,
            "set_tempo": self._handle_set_tempo,
            "fire_clip": self._handle_fire_clip,
            "stop_clip": self._handle_stop_clip,
            "start_playback": self._handle_start_playback,
            "stop_playback": self._handle_stop_playback,
            "get_browser_tree": self._handle_get_browser_tree,
            "get_browser_items_at_path": self._handle_get_browser_items_at_path,
            "get_browser_item": self._handle_get_browser_item,
            "load_browser_item": self._handle_load_browser_item,
        }

    def route(self, command, schedule_message):
        command_type = command.get("type", "")
        params = command.get("params", {})

        response = {"status": "success", "result": {}}

        if command_type not in self._commands:
            response["status"] = "error"
            response["message"] = "Unknown command: " + command_type
            return response

        if command_type in MAIN_THREAD_COMMANDS:
            return self._route_main_thread(command, schedule_message)

        try:
            handler = self._commands[command_type]
            response["result"] = handler(params)
        except Exception as e:
            self._logger.error("Error processing command: " + str(e))
            response["status"] = "error"
            response["message"] = str(e)

        return response

    def _route_main_thread(self, command, schedule_message):
        response_queue = queue.Queue()
        command_type = command.get("type", "")
        params = command.get("params", {})

        def main_task():
            try:
                handler = self._commands[command_type]
                result = handler(params)
                response_queue.put({"status": "success", "result": result})
            except Exception as e:
                self._logger.error("Error in main thread task: " + str(e))
                response_queue.put({"status": "error", "message": str(e)})

        try:
            schedule_message(0, main_task)
        except AssertionError:
            main_task()

        try:
            task_response = response_queue.get(timeout=10.0)
            if task_response.get("status") == "error":
                return {"status": "error", "message": task_response.get("message", "Unknown error")}
            return {"status": "success", "result": task_response.get("result", {})}
        except queue.Empty:
            return {"status": "error", "message": "Timeout waiting for operation to complete"}

    def _handle_get_session_info(self, params):
        return self._session.get_session_info()

    def _handle_get_full_session_state(self, params):
        return self._session.get_full_session_state()

    def _handle_get_track_info(self, params):
        track_index = params.get("track_index", 0)
        return self._track.get_track_info(track_index)

    def _handle_create_midi_track(self, params):
        index = params.get("index", -1)
        return self._track.create_midi_track(index)

    def _handle_set_track_name(self, params):
        track_index = params.get("track_index", 0)
        name = params.get("name", "")
        return self._track.set_track_name(track_index, name)

    def _handle_create_clip(self, params):
        track_index = params.get("track_index", 0)
        clip_index = params.get("clip_index", 0)
        length = params.get("length", 4.0)
        return self._clip.create_clip(track_index, clip_index, length)

    def _handle_add_notes_to_clip(self, params):
        track_index = params.get("track_index", 0)
        clip_index = params.get("clip_index", 0)
        notes = params.get("notes", [])
        return self._clip.add_notes_to_clip(track_index, clip_index, notes)

    def _handle_set_clip_name(self, params):
        track_index = params.get("track_index", 0)
        clip_index = params.get("clip_index", 0)
        name = params.get("name", "")
        return self._clip.set_clip_name(track_index, clip_index, name)

    def _handle_set_tempo(self, params):
        tempo = params.get("tempo", 120.0)
        return self._session.set_tempo(tempo)

    def _handle_fire_clip(self, params):
        track_index = params.get("track_index", 0)
        clip_index = params.get("clip_index", 0)
        return self._clip.fire_clip(track_index, clip_index)

    def _handle_stop_clip(self, params):
        track_index = params.get("track_index", 0)
        clip_index = params.get("clip_index", 0)
        return self._clip.stop_clip(track_index, clip_index)

    def _handle_start_playback(self, params):
        return self._session.start_playback()

    def _handle_stop_playback(self, params):
        return self._session.stop_playback()

    def _handle_get_browser_tree(self, params):
        category_type = params.get("category_type", "all")
        return self._browser.get_browser_tree(category_type)

    def _handle_get_browser_items_at_path(self, params):
        path = params.get("path", "")
        return self._browser.get_browser_items_at_path(path)

    def _handle_get_browser_item(self, params):
        uri = params.get("uri", None)
        path = params.get("path", None)
        return self._browser.get_browser_item(uri, path)

    def _handle_load_browser_item(self, params):
        track_index = params.get("track_index", 0)
        item_uri = params.get("item_uri", "")
        return self._browser.load_browser_item(track_index, item_uri)
