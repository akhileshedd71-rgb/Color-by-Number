extends Control
signal back_requested
signal settings_requested
signal completed(art: ArtworkData)
const CHIP = preload("res://scenes/ui/color_chip.tscn")
var art: ArtworkData
var palette: Array = []
var chips: Array = []
var finished := false
var session_id := 0
@onready var board: ColoringBoard = $Board

func start(value: ArtworkData) -> void:
	session_id += 1
	art = value
	finished = false
	$Header/Names/Title.text = art.title
	$Header/Names/Subtitle.text = art.category + " · " + art.difficulty
	palette = art.read_regions().palette
	for chip in chips:
		chip.get_parent().remove_child(chip)
		chip.queue_free()
	chips.clear()
	board.load_art(art)
	for i in range(palette.size()):
		var chip := CHIP.instantiate()
		$PalettePanel/Scroll/Colors.add_child(chip)
		chip.setup(i, Color(palette[i]))
		chip.pressed.connect(_select.bind(i))
		chips.append(chip)
	finished = _filled_count() == board.regions.size()
	_select(_next_color())
	_refresh()
	$Instruction.text = "Your masterpiece. Pinch to explore every detail." if finished else "Pick a color. Tap its matching numbers."

func _select(index: int) -> void:
	board.select_color(index)
	_refresh()
	if not finished:
		$Instruction.text = "Find the %ds. A little magic is waiting." % (index + 1)
	if chips.size() > index:
		$PalettePanel/Scroll.ensure_control_visible(chips[index])

func _remaining(index: int) -> int:
	var count := 0
	for r in board.regions:
		if not r.filled and r.color_index == index: count += 1
	return count

func _filled_count() -> int:
	var count := 0
	for r in board.regions:
		if r.filled: count += 1
	return count

func _next_color() -> int:
	for i in range(palette.size()):
		if _remaining(i) > 0: return i
	return 0

func _refresh() -> void:
	var done := _filled_count()
	var total := board.regions.size()
	$Progress.value = float(done) / maxi(total, 1) * 100
	$Percent.text = "%d%%" % roundi($Progress.value)
	$PalettePanel/Remaining.text = "%d little moments to go" % (total - done) if done < total else "Every color, complete!"
	for i in range(chips.size()):
		chips[i].update_state(_remaining(i), board.active_color == i)
	$Controls/Hint.disabled = done == total

func _on_filled(region: ColorRegion) -> void:
	Progress.store_fill(art.id, region.region_id, board.regions.size())
	Sound.play("fill", 1.0 + float(region.color_index) * .035)
	Sound.haptic()
	_refresh()
	if _filled_count() == board.regions.size() and not finished:
		finished = true
		$Instruction.text = "You made something beautiful."
		board.reset_view()
		var current_session := session_id
		await get_tree().create_timer(1.0).timeout
		if visible and session_id == current_session:
			completed.emit(art)
	elif _remaining(board.active_color) == 0:
		_select(_next_color())
		$Instruction.text = "Color complete! On to the next little joy."

func _on_wrong(index: int) -> void:
	$Instruction.text = "This little piece needs color %d." % (index + 1)

func _on_hint() -> void:
	if _remaining(board.active_color) == 0: _select(_next_color())
	if board.focus_hint():
		Sound.play("hint")
		$Instruction.text = "There you are! Tap the glowing circle."

func _on_zoom() -> void:
	board.zoom_at(1.3, board.size * 0.5)

func _on_back() -> void:
	session_id += 1
	board.cancel_input()
	back_requested.emit()

func _on_settings() -> void:
	board.cancel_input()
	settings_requested.emit()
