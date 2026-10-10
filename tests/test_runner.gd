extends Node
var checks := 0
var failures: Array[String] = []
var main: Control
var game: Control
var board: ColoringBoard

func check(value: bool, description: String) -> void:
	checks += 1
	if not value:
		failures.append(description)
		push_error("FAIL: " + description)

func _ready() -> void:
	# Tests never touch the player's actual save file.
	Progress.save_path = "user://test_progress.json"
	Progress.data = {"version": 1, "artworks": {}, "sound": false, "haptics": false, "daily_dates": []}
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	await get_tree().process_frame
	game = main.get_node("Game")
	board = game.get_node("Board")
	check(Progress.catalog.size() == 14, "14 artworks load")
	var free_count := 0
	var total_shapes := 0
	for art in Progress.catalog:
		if Progress.is_unlocked(art): free_count += 1
		main._open_art(art)
		await get_tree().process_frame
		for i in range(board.regions.size()):
			var r := board.regions[i]
			total_shapes += 1
			check(Geometry2D.triangulate_polygon(r.points).size() > 0, art.id + " / " + r.region_id + " triangulates")
			check(r.hit(r.label_position), art.id + " label is interior")
			for j in range(i + 1, board.regions.size()):
				check(not board.regions[j].hit(r.label_position), art.id + " label is not occluded")
	check(free_count == 12, "12 starter artworks are unlocked")
	print("Validated %d regions across 14 artworks" % total_shapes)
	main._open_art(Progress.catalog[0])
	await get_tree().process_frame
	var target := board.regions[0]
	var point := board.artwork_root.position + target.label_position * board.artwork_root.scale
	board.select_color((target.color_index + 1) % game.palette.size())
	check(not board.tap(point), "Mismatched color rejects fill")
	check(not target.filled, "Wrong tap keeps region empty")
	board.select_color(target.color_index)
	check(board.tap(point), "Correct tap fills region")
	check(target.filled, "Region is colored")
	check(not board.tap(point), "Duplicate tap cannot award twice")
	check(Progress.filled_ids(game.art.id).size() == 1, "Save records one unique region")
	Progress.data.artworks = {}
	Progress.load_progress()
	check(Progress.filled_ids(game.art.id).size() == 1, "Save reload restores progress")
	main._gallery()
	main._open_art(Progress.catalog[0])
	check(board.regions[0].filled, "Reopening artwork restores its fill")
	var before := board.board_point(board.size * .5)
	board.zoom_at(2.0, board.size * .5)
	check(board.board_point(board.size * .5).distance_to(before) < .1, "Zoom preserves focus point")
	board.zoom_at(99, board.size * .5)
	check(board.zoom_factor == 4.5, "Zoom is bounded above")
	board.zoom_at(.0001, board.size * .5)
	check(board.zoom_factor == 1.0, "Zoom is bounded below")
	board.pan = Vector2(100000, -100000)
	board._layout()
	check(board.pan.length() < 500, "Pan is bounded")
	board.reset_view()
	check(board.zoom_factor == 1 and board.pan == Vector2.ZERO, "Fit resets view")
	game._select(game._next_color())
	check(board.focus_hint(), "Hint finds a matching unfilled region")
	await get_tree().create_timer(.55).timeout
	check(board.hint_ring.visible, "Hint visibly highlights target")
	check(is_equal_approx(board.zoom_factor, 2.6), "Hint zooms to target")
	board.reset_view()
	await _test_touch()
	await _test_real_mouse()
	# Solve three full artworks through the same hit-testing path players use.
	for a in range(3):
		main._open_art(Progress.catalog[a])
		await get_tree().process_frame
		for r in board.regions:
			if r.filled: continue
			board.select_color(r.color_index)
			var p := board.artwork_root.position + r.label_position * board.artwork_root.scale
			check(board.tap(p), "Every region is tappable: " + r.region_id)
		await get_tree().create_timer(1.2).timeout
		check(main.get_node("Reward").visible, "Completion opens reward")
		check(Progress.is_complete(Progress.catalog[a].id), "Completion is saved")
		check(game.get_node("Progress").value == 100, "Progress reaches 100%")
	check(Progress.completed_count() == 3, "Three unique completions counted")
	check(Progress.is_unlocked(Progress.catalog[12]), "3-completion milestone unlocks artwork")
	check(not Progress.is_unlocked(Progress.catalog[13]), "6-completion milestone remains locked")
	main._open_art(Progress.catalog[0])
	check(game.finished, "Completed artwork reopens for admiration")
	await get_tree().create_timer(1.15).timeout
	check(not main.get_node("Reward").visible, "Reopening does not award a duplicate completion")
	var gallery: Control = main.get_node("Gallery")
	main._gallery()
	gallery._navigate("MyArt")
	check(gallery.grid.get_child_count() == 3, "My Art shows started and completed work")
	gallery._navigate("Library")
	gallery._filter("Animals")
	check(gallery.grid.get_child_count() == 4, "Category filter matches catalog")
	gallery._navigate("Daily")
	check(gallery.grid.get_child_count() == 1, "Daily view shows one deterministic selection")
	check(Progress.daily_art().id == Progress.daily_art().id, "Daily selection stable")
	Progress.set_setting("sound", false)
	Progress.set_setting("haptics", false)
	Progress.load_progress()
	check(not Progress.setting("sound") and not Progress.setting("haptics"), "Settings persist")
	var stale := FileAccess.open(Progress.save_path, FileAccess.WRITE)
	stale.store_string(JSON.stringify({"version": 1, "artworks": {"cosmic_peony": {"filled": ["region_000", "region_000", "missing", 123], "complete": true}}, "daily_dates": []}))
	stale.close()
	Progress.load_progress()
	check(Progress.filled_ids("cosmic_peony") == ["region_000"], "Stale, duplicate and invalid saved region IDs are sanitized")
	check(not Progress.is_complete("cosmic_peony"), "Saved completion is validated against actual regions")
	# Unreadable and structurally malformed saves must not crash the app.
	var f := FileAccess.open(Progress.save_path, FileAccess.WRITE)
	f.store_string("not json"); f.close()
	Progress.load_progress()
	check(FileAccess.file_exists(Progress.save_path + ".corrupt"), "Corrupt save preserved for recovery")
	Progress.save()
	DirAccess.remove_absolute(Progress.save_path)
	DirAccess.remove_absolute(Progress.save_path + ".corrupt")
	print("RESULT: %d checks; %d failures" % [checks, failures.size()])
	get_tree().quit(0 if failures.is_empty() else 1)

func _touch(index: int, point: Vector2, down: bool, canceled: bool = false) -> void:
	var event := InputEventScreenTouch.new()
	event.index = index; event.position = point; event.pressed = down; event.canceled = canceled
	board._gui_input(event)

func _test_touch() -> void:
	var count: int = game._filled_count()
	_touch(0, Vector2(160, 240), true)
	_touch(1, Vector2(320, 240), true)
	var drag := InputEventScreenDrag.new()
	drag.index = 1; drag.position = Vector2(430, 240)
	board._gui_input(drag)
	check(board.zoom_factor > 1.5, "Two touch points perform pinch zoom")
	_touch(1, Vector2(430, 240), false)
	_touch(0, Vector2(160, 240), false)
	check(game._filled_count() == count, "Pinch release never fills a region")
	board.reset_view()
	var r := board.regions[1]
	board.select_color(r.color_index)
	var point := board.artwork_root.position + r.label_position * board.artwork_root.scale
	_touch(0, point, true)
	_touch(0, point, false, true)
	check(not r.filled, "Canceled touch cannot fill")
	_touch(0, point, true)
	_touch(0, point, false)
	check(r.filled, "Single touch fills a matching region")
	await get_tree().process_frame

func _test_real_mouse() -> void:
	if DisplayServer.get_name() == "headless":
		print("SKIP: window mouse routing requires a display; covered by rendered run.")
		return
	var r := board.regions[2]
	game._select(r.color_index)
	var p := board.global_position + board.artwork_root.position + r.label_position * board.artwork_root.scale
	var motion := InputEventMouseMotion.new()
	motion.position = p
	motion.global_position = p
	Input.parse_input_event(motion)
	await get_tree().process_frame
	for down in [true, false]:
		var event := InputEventMouseButton.new()
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = down
		event.position = p
		event.global_position = p
		Input.parse_input_event(event)
		await get_tree().process_frame
	check(r.filled, "Real viewport mouse events reach board hit testing")
