extends Button
var index := 0
var paint := Color.WHITE
var remaining := 0
var active := false
var font: Font = preload("res://assets/fonts/Body.tres")

func _ready() -> void:
	flat = true
	add_theme_stylebox_override("normal", StyleBoxEmpty.new())
	add_theme_stylebox_override("hover", StyleBoxEmpty.new())
	add_theme_stylebox_override("pressed", StyleBoxEmpty.new())
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())

func setup(i: int, color: Color) -> void:
	index = i
	paint = color
	tooltip_text = "Color %d" % (index + 1)
	queue_redraw()

func update_state(count: int, selected: bool) -> void:
	remaining = count
	active = selected
	queue_redraw()

func _draw() -> void:
	var center := Vector2(size.x * 0.5, 30)
	if active:
		draw_circle(center, 29, Color("DCC7F5"))
		draw_circle(center, 26, Color.WHITE)
	draw_circle(center + Vector2(0, 3), 23, paint.darkened(.2))
	draw_circle(center, 23, paint if remaining > 0 else paint.lightened(.55))
	draw_arc(center, 19, PI * 1.13, PI * 1.84, 24, Color(1, 1, 1, .38), 2, true)
	var ink := Color("302345") if paint.get_luminance() > .40 else Color.WHITE
	if remaining == 0:
		draw_polyline(PackedVector2Array([center + Vector2(-9, 0), center + Vector2(-2, 7), center + Vector2(10, -7)]), Color("645178"), 3, true)
	else:
		var text_value := str(index + 1)
		var width := font.get_string_size(text_value, HORIZONTAL_ALIGNMENT_LEFT, -1, 22).x
		draw_string(font, center + Vector2(-width / 2, 8), text_value, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, ink)
		var count_text := str(remaining)
		var w := font.get_string_size(count_text, HORIZONTAL_ALIGNMENT_LEFT, -1, 10).x
		draw_string(font, Vector2(center.x - w / 2, 66), count_text, HORIZONTAL_ALIGNMENT_LEFT, -1, 10, Color("9A83AC"))
