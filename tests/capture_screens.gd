extends Node
var main: Control
var output := "res://docs/screenshots"

func snap(name: String) -> void:
	await get_tree().create_timer(.75).timeout
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	var result := image.save_png(output.path_join(name + ".png"))
	assert(result == OK)
	print("SCREENSHOT: ", name, " ", image.get_size())

func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(output)
	Progress.save_path = "user://visual_review.json"
	Progress.data = {"version": 1, "artworks": {}, "sound": false, "haptics": false, "daily_dates": []}
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	await snap("01-gallery")
	main._open_art(Progress.catalog[0])
	await snap("02-coloring")
	var board: ColoringBoard = main.get_node("Game/Board")
	for r in board.regions:
		if r.color_index in [0, 1, 2, 3]:
			board.select_color(r.color_index)
			board.tap(board.artwork_root.position + r.label_position * board.artwork_root.scale)
	await snap("03-in-progress")
	main.get_node("Game")._on_hint()
	await get_tree().create_timer(.5).timeout
	await snap("04-hint-zoom")
	board.reset_view()
	for r in board.regions:
		if not r.filled:
			board.select_color(r.color_index)
			board.tap(board.artwork_root.position + r.label_position * board.artwork_root.scale)
	await get_tree().create_timer(3.1).timeout
	await snap("05-completion")
	main._gallery()
	main.get_node("Gallery")._navigate("MyArt")
	await snap("06-my-art")
	main.get_node("Gallery")._navigate("Daily")
	await snap("07-daily")
	main._settings()
	await snap("08-settings")
	main.get_node("Settings").hide()
	main._open_art(Progress.catalog[2])
	await snap("09-fox")
	get_window().size = Vector2i(390, 844)
	print("PHONE WINDOW: ", get_window().size, " scale=", get_window().content_scale_size)
	await get_tree().create_timer(.4).timeout
	await snap("10-tall-phone")
	DirAccess.remove_absolute(Progress.save_path)
	print("SCREEN REVIEW COMPLETE")
	get_tree().quit()
