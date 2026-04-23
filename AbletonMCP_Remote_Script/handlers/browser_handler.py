from __future__ import print_function, unicode_literals


class BrowserHandler(object):
    def __init__(self, app, song, logger):
        self._app = app
        self._song = song
        self._logger = logger

    def get_browser_tree(self, category_type="all"):
        try:
            if not self._app:
                raise RuntimeError("Could not access Live application")

            if not hasattr(self._app, 'browser') or self._app.browser is None:
                raise RuntimeError("Browser is not available in the Live application")

            browser_attrs = [attr for attr in dir(self._app.browser) if not attr.startswith('_')]
            self._logger.debug("Available browser attributes: {0}".format(browser_attrs))

            result = {
                "type": category_type,
                "categories": [],
                "available_categories": browser_attrs
            }

            def process_item(item):
                if not item:
                    return None

                return {
                    "name": item.name if hasattr(item, 'name') else "Unknown",
                    "is_folder": hasattr(item, 'children') and bool(item.children),
                    "is_device": hasattr(item, 'is_device') and item.is_device,
                    "is_loadable": hasattr(item, 'is_loadable') and item.is_loadable,
                    "uri": item.uri if hasattr(item, 'uri') else None,
                    "children": []
                }

            if (category_type == "all" or category_type == "instruments") and hasattr(self._app.browser, 'instruments'):
                try:
                    instruments = process_item(self._app.browser.instruments)
                    if instruments:
                        instruments["name"] = "Instruments"
                        result["categories"].append(instruments)
                except Exception as e:
                    self._logger.error("Error processing instruments: " + str(e))

            if (category_type == "all" or category_type == "sounds") and hasattr(self._app.browser, 'sounds'):
                try:
                    sounds = process_item(self._app.browser.sounds)
                    if sounds:
                        sounds["name"] = "Sounds"
                        result["categories"].append(sounds)
                except Exception as e:
                    self._logger.error("Error processing sounds: " + str(e))

            if (category_type == "all" or category_type == "drums") and hasattr(self._app.browser, 'drums'):
                try:
                    drums = process_item(self._app.browser.drums)
                    if drums:
                        drums["name"] = "Drums"
                        result["categories"].append(drums)
                except Exception as e:
                    self._logger.error("Error processing drums: " + str(e))

            if (category_type == "all" or category_type == "audio_effects") and hasattr(self._app.browser, 'audio_effects'):
                try:
                    audio_effects = process_item(self._app.browser.audio_effects)
                    if audio_effects:
                        audio_effects["name"] = "Audio Effects"
                        result["categories"].append(audio_effects)
                except Exception as e:
                    self._logger.error("Error processing audio_effects: " + str(e))

            if (category_type == "all" or category_type == "midi_effects") and hasattr(self._app.browser, 'midi_effects'):
                try:
                    midi_effects = process_item(self._app.browser.midi_effects)
                    if midi_effects:
                        midi_effects["name"] = "MIDI Effects"
                        result["categories"].append(midi_effects)
                except Exception as e:
                    self._logger.error("Error processing midi_effects: " + str(e))

            for attr in browser_attrs:
                if attr not in ['instruments', 'sounds', 'drums', 'audio_effects', 'midi_effects'] and \
                   (category_type == "all" or category_type == attr):
                    try:
                        item = getattr(self._app.browser, attr)
                        if hasattr(item, 'children') or hasattr(item, 'name'):
                            category = process_item(item)
                            if category:
                                category["name"] = attr.capitalize()
                                result["categories"].append(category)
                    except Exception as e:
                        self._logger.error("Error processing {0}: {1}".format(attr, str(e)))

            self._logger.debug("Browser tree generated for {0} with {1} root categories".format(
                category_type, len(result['categories'])))
            return result

        except Exception as e:
            self._logger.error("Error getting browser tree: " + str(e))
            raise

    def get_browser_items_at_path(self, path):
        try:
            if not self._app:
                raise RuntimeError("Could not access Live application")

            if not hasattr(self._app, 'browser') or self._app.browser is None:
                raise RuntimeError("Browser is not available in the Live application")

            browser_attrs = [attr for attr in dir(self._app.browser) if not attr.startswith('_')]

            path_parts = path.split("/")
            if not path_parts:
                raise ValueError("Invalid path")

            root_category = path_parts[0].lower()
            current_item = None

            if root_category == "instruments" and hasattr(self._app.browser, 'instruments'):
                current_item = self._app.browser.instruments
            elif root_category == "sounds" and hasattr(self._app.browser, 'sounds'):
                current_item = self._app.browser.sounds
            elif root_category == "drums" and hasattr(self._app.browser, 'drums'):
                current_item = self._app.browser.drums
            elif root_category == "audio_effects" and hasattr(self._app.browser, 'audio_effects'):
                current_item = self._app.browser.audio_effects
            elif root_category == "midi_effects" and hasattr(self._app.browser, 'midi_effects'):
                current_item = self._app.browser.midi_effects
            else:
                found = False
                for attr in browser_attrs:
                    if attr.lower() == root_category:
                        try:
                            current_item = getattr(self._app.browser, attr)
                            found = True
                            break
                        except Exception as e:
                            self._logger.error("Error accessing browser attribute {0}: {1}".format(attr, str(e)))

                if not found:
                    return {
                        "path": path,
                        "error": "Unknown or unavailable category: {0}".format(root_category),
                        "available_categories": browser_attrs,
                        "items": []
                    }

            for i in range(1, len(path_parts)):
                part = path_parts[i]
                if not part:
                    continue

                if not hasattr(current_item, 'children'):
                    return {
                        "path": path,
                        "error": "Item at '{0}' has no children".format('/'.join(path_parts[:i])),
                        "items": []
                    }

                found = False
                for child in current_item.children:
                    if hasattr(child, 'name') and child.name.lower() == part.lower():
                        current_item = child
                        found = True
                        break

                if not found:
                    return {
                        "path": path,
                        "error": "Path part '{0}' not found".format(part),
                        "items": []
                    }

            items = []
            if hasattr(current_item, 'children'):
                for child in current_item.children:
                    item_info = {
                        "name": child.name if hasattr(child, 'name') else "Unknown",
                        "is_folder": hasattr(child, 'children') and bool(child.children),
                        "is_device": hasattr(child, 'is_device') and child.is_device,
                        "is_loadable": hasattr(child, 'is_loadable') and child.is_loadable,
                        "uri": child.uri if hasattr(child, 'uri') else None
                    }
                    items.append(item_info)

            return {
                "path": path,
                "name": current_item.name if hasattr(current_item, 'name') else "Unknown",
                "uri": current_item.uri if hasattr(current_item, 'uri') else None,
                "is_folder": hasattr(current_item, 'children') and bool(current_item.children),
                "is_device": hasattr(current_item, 'is_device') and current_item.is_device,
                "is_loadable": hasattr(current_item, 'is_loadable') and current_item.is_loadable,
                "items": items
            }

        except Exception as e:
            self._logger.error("Error getting browser items at path: " + str(e))
            raise

    def get_browser_item(self, uri, path):
        try:
            if not self._app:
                raise RuntimeError("Could not access Live application")

            result = {
                "uri": uri,
                "path": path,
                "found": False
            }

            if uri:
                item = self._find_browser_item_by_uri(self._app.browser, uri)
                if item:
                    result["found"] = True
                    result["item"] = {
                        "name": item.name,
                        "is_folder": item.is_folder,
                        "is_device": item.is_device,
                        "is_loadable": item.is_loadable,
                        "uri": item.uri
                    }
                    return result

            if path:
                path_parts = path.split("/")

                current_item = None
                if path_parts[0].lower() == "instruments":
                    current_item = self._app.browser.instruments
                elif path_parts[0].lower() == "sounds":
                    current_item = self._app.browser.sounds
                elif path_parts[0].lower() == "drums":
                    current_item = self._app.browser.drums
                elif path_parts[0].lower() == "audio_effects":
                    current_item = self._app.browser.audio_effects
                elif path_parts[0].lower() == "midi_effects":
                    current_item = self._app.browser.midi_effects
                else:
                    current_item = self._app.browser.instruments
                    path_parts = ["instruments"] + path_parts

                for i in range(1, len(path_parts)):
                    part = path_parts[i]
                    if not part:
                        continue

                    found = False
                    for child in current_item.children:
                        if child.name.lower() == part.lower():
                            current_item = child
                            found = True
                            break

                    if not found:
                        result["error"] = "Path part '{0}' not found".format(part)
                        return result

                result["found"] = True
                result["item"] = {
                    "name": current_item.name,
                    "is_folder": current_item.is_folder,
                    "is_device": current_item.is_device,
                    "is_loadable": current_item.is_loadable,
                    "uri": current_item.uri
                }

            return result

        except Exception as e:
            self._logger.error("Error getting browser item: " + str(e))
            raise

    def load_browser_item(self, track_index, item_uri):
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            item = self._find_browser_item_by_uri(self._app.browser, item_uri)

            if not item:
                raise ValueError("Browser item with URI '{0}' not found".format(item_uri))

            self._song.view.selected_track = track
            self._app.browser.load_item(item)

            return {
                "loaded": True,
                "item_name": item.name,
                "track_name": track.name,
                "uri": item_uri
            }
        except Exception as e:
            self._logger.error("Error loading browser item: {0}".format(str(e)))
            raise

    def _find_browser_item_by_uri(self, browser_or_item, uri, max_depth=10, current_depth=0):
        try:
            if hasattr(browser_or_item, 'uri') and browser_or_item.uri == uri:
                return browser_or_item

            if current_depth >= max_depth:
                return None

            if hasattr(browser_or_item, 'instruments'):
                categories = [
                    browser_or_item.instruments,
                    browser_or_item.sounds,
                    browser_or_item.drums,
                    browser_or_item.audio_effects,
                    browser_or_item.midi_effects
                ]

                for category in categories:
                    item = self._find_browser_item_by_uri(category, uri, max_depth, current_depth + 1)
                    if item:
                        return item

                return None

            if hasattr(browser_or_item, 'children') and browser_or_item.children:
                for child in browser_or_item.children:
                    item = self._find_browser_item_by_uri(child, uri, max_depth, current_depth + 1)
                    if item:
                        return item

            return None
        except Exception as e:
            self._logger.error("Error finding browser item by URI: {0}".format(str(e)))
            return None