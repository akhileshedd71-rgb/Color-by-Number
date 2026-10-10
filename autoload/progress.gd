extends Node
signal changed
signal save_failed

const SAVE_VERSION := 1
var save_path := "user://progress.json"
var data: Dictionary = {"version": SAVE_VERSION, "artworks": {}, "sound": true, "haptics": true, "daily_dates": []}
var catalog: Array[ArtworkData] = []
const ART_IDS := ["cosmic_peony", "moonwing", "dream_fox", "starlit_valley", "sugar_mandala", "coral_garden", "golden_hour", "aurora_wings", "velvet_fox", "candy_mountains", "jewel_wheel", "orchid_party", "nebula_lotus", "rosewater"]

func _ready() -> void:
	for id in ART_IDS:
		catalog.append(load("res://resources/levels/%s.tres" % id) as ArtworkData)
	load_progress()

func load_progress() -> void:
	if not FileAccess.file_exists(save_path):
		return
	var parser := JSON.new()
	var parse_error := parser.parse(FileAccess.get_file_as_string(save_path))
	var loaded: Variant = parser.data if parse_error == OK else null
	if not loaded is Dictionary or loaded.get("version") != SAVE_VERSION or not loaded.get("artworks") is Dictionary:
		# Keep the unreadable file for recovery, never discard it silently.
		DirAccess.copy_absolute(save_path, save_path + ".corrupt")
		return
	data = loaded
	var clean_artworks: Dictionary = {}
	for art in catalog:
		var entry: Variant = data.artworks.get(art.id)
		if not entry is Dictionary or not entry.get("filled", []) is Array: continue
		var valid_ids: Array = []
		for shape in art.read_regions().shapes: valid_ids.append(shape.id)
		var clean: Array = []
		for id in entry.get("filled", []):
			if id is String and id in valid_ids and id not in clean: clean.append(id)
		clean_artworks[art.id] = {"filled": clean, "complete": clean.size() == valid_ids.size()}
	data.artworks = clean_artworks
	if not data.get("daily_dates", []) is Array:
		data.daily_dates = []

func save() -> bool:
	var file := FileAccess.open(save_path + ".tmp", FileAccess.WRITE)
	if file == null:
		save_failed.emit()
		return false
	file.store_string(JSON.stringify(data))
	file.flush()
	var error := file.get_error()
	file.close()
	if error != OK or DirAccess.rename_absolute(save_path + ".tmp", save_path) != OK:
		save_failed.emit()
		return false
	changed.emit()
	return true

func filled_ids(id: String) -> Array:
	return data.artworks.get(id, {}).get("filled", []).duplicate()

func store_fill(id: String, region_id: String, total: int) -> bool:
	var entry: Dictionary = data.artworks.get(id, {"filled": [], "complete": false})
	if region_id not in entry.filled:
		entry.filled.append(region_id)
	entry.complete = entry.filled.size() >= total
	data.artworks[id] = entry
	if entry.complete and id == daily_art().id:
		var dates: Array = data.get("daily_dates", [])
		var today := Time.get_date_string_from_system()
		if today not in dates:
			dates.append(today)
		data.daily_dates = dates
	return save()

func completed_count() -> int:
	var count := 0
	for entry in data.artworks.values():
		if entry.get("complete", false):
			count += 1
	return count

func is_complete(id: String) -> bool:
	return data.artworks.get(id, {}).get("complete", false)

func is_unlocked(art: ArtworkData) -> bool:
	return completed_count() >= art.unlock_after

func daily_art() -> ArtworkData:
	return catalog[posmod(Time.get_date_string_from_system().hash(), 12)]

func setting(key: String) -> bool:
	return bool(data.get(key, true))

func set_setting(key: String, value: bool) -> void:
	data[key] = value
	save()
