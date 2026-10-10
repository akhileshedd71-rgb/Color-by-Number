class_name ColoringBoard
extends Control
signal region_filled(region: ColorRegion)
signal wrong_color(index: int)
signal ready_to_play

const REGION = preload("res://scenes/game/region.tscn")
const BURST = preload("res://scenes/game/fill_burst.tscn")
var regions: Array[ColorRegion] = []
var active_color := 0
var zoom_factor := 1.0
var pan := Vector2.ZERO
var base_scale := 1.0
var pointers: Dictionary = {}
var press_point := Vector2.ZERO
var moved := false
var pinching := false
var mouse_down := false
var art: ArtworkData
var hint_tween: Tween
@onready var artwork_root: Node2D = $Artwork
@onready var backdrop: Control = $Backdrop
@onready var hint_ring: Control = $HintRing

func _ready() -> void:
	resized.connect(_layout)

func load_art(data: ArtworkData) -> void:
	art = data
	for r in regions:
		r.queue_free()
	regions.clear()
	var content := art.read_regions()
	var saved := Progress.filled_ids(art.id)
	for shape in content.shapes:
		var region: ColorRegion = REGION.instantiate()
		artwork_root.add_child(region)
		region.configure(shape, content.palette, saved)
		regions.append(region)
	reset_view()
	select_color(0)
	ready_to_play.emit()

func _layout() -> void:
	base_scale = minf(size.x / 600.0, size.y / 600.0) * 0.95
	_clamp_pan()
	artwork_root.scale = Vector2.ONE * base_scale * zoom_factor
	artwork_root.position = size * 0.5 + pan - Vector2(300, 300) * base_scale * zoom_factor
	for region in regions:
		region.update_label(base_scale * zoom_factor)

func _clamp_pan() -> void:
	var extent := Vector2.ONE * 300 * base_scale * zoom_factor
	var limit := (extent - size * 0.5 + Vector2.ONE * 70).max(Vector2.ZERO)
	pan = pan.clamp(-limit, limit)

func reset_view() -> void:
	if hint_tween and hint_tween.is_running(): hint_tween.kill()
	zoom_factor = 1.0
	pan = Vector2.ZERO
	hint_ring.hide()
	_layout()

func select_color(index: int) -> void:
	active_color = index
	hint_ring.hide()
	for r in regions:
		r.set_selected(index)

func board_point(point: Vector2) -> Vector2:
	return (point - artwork_root.position) / artwork_root.scale

func tap(point: Vector2) -> bool:
	var at := board_point(point)
	for i in range(regions.size() - 1, -1, -1):
		var r := regions[i]
		if not r.hit(at): continue
		if r.filled: return false
		if r.color_index != active_color:
			r.flash_wrong()
			wrong_color.emit(r.color_index)
			return false
		r.fill_region()
		hint_ring.hide()
		var burst: CPUParticles2D = BURST.instantiate()
		add_child(burst)
		burst.position = point
		burst.color = r.target.lightened(0.2)
		burst.emitting = true
		get_tree().create_timer(1.2).timeout.connect(burst.queue_free)
		region_filled.emit(r)
		return true
	return false

func zoom_at(factor: float, focus: Vector2) -> void:
	var previous := zoom_factor
	zoom_factor = clampf(zoom_factor * factor, 1.0, 4.5)
	pan = focus - size * 0.5 - (focus - size * 0.5 - pan) * zoom_factor / previous
	_layout()

func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP and event.pressed: zoom_at(1.15, event.position)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN and event.pressed: zoom_at(1.0 / 1.15, event.position)
		elif event.button_index == MOUSE_BUTTON_LEFT:
			mouse_down = event.pressed
			if event.pressed:
				press_point = event.position
				moved = false
			elif not moved: tap(event.position)
	elif event is InputEventMouseMotion and mouse_down:
		if event.position.distance_to(press_point) > 9: moved = true
		if moved:
			pan += event.relative
			_layout()
	elif event is InputEventScreenTouch:
		if event.pressed:
			pointers[event.index] = event.position
			if pointers.size() == 1:
				press_point = event.position
				moved = false
				pinching = false
			else:
				pinching = true
				moved = true
		else:
			if pointers.has(event.index) and pointers.size() == 1 and not moved and not pinching and not event.canceled:
				tap(event.position)
			pointers.erase(event.index)
	elif event is InputEventScreenDrag and pointers.has(event.index):
		if pointers.size() >= 2:
			var before: Array = pointers.values()
			var old_distance: float = before[0].distance_to(before[1])
			var old_center: Vector2 = (before[0] + before[1]) * 0.5
			pointers[event.index] = event.position
			var after: Array = pointers.values()
			var center: Vector2 = (after[0] + after[1]) * 0.5
			if old_distance > 0: zoom_at(after[0].distance_to(after[1]) / old_distance, old_center)
			pan += center - old_center
			_layout()
		else:
			if event.position.distance_to(press_point) > 9: moved = true
			if moved:
				pan += event.position - Vector2(pointers[event.index])
				_layout()
			pointers[event.index] = event.position
	accept_event()

func focus_hint() -> bool:
	for r in regions:
		if r.filled or r.color_index != active_color: continue
		if hint_tween and hint_tween.is_running(): hint_tween.kill()
		var target_pan := -(r.label_position - Vector2(300, 300)) * base_scale * 2.6
		hint_tween = create_tween().set_parallel(true)
		hint_tween.tween_property(self, "zoom_factor", 2.6, 0.4).set_trans(Tween.TRANS_CUBIC)
		hint_tween.tween_property(self, "pan", target_pan, 0.4).set_trans(Tween.TRANS_CUBIC)
		hint_tween.tween_method(func(_v: float): _layout(), 0.0, 1.0, 0.4)
		hint_tween.chain().tween_callback(func():
			_layout()
			hint_ring.position = artwork_root.position + r.label_position * artwork_root.scale - hint_ring.size * 0.5
			hint_ring.show())
		return true
	return false

func cancel_input() -> void:
	pointers.clear()
	mouse_down = false
	moved = true
	pinching = false
