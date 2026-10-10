extends Control
var time := 0.0
func _process(delta: float) -> void:
	if visible:
		time += delta
		queue_redraw()
func _draw() -> void:
	draw_arc(size * 0.5, 27 + sin(time * 5) * 3, 0, TAU, 48, Color("FFD977"), 3, true)
	draw_arc(size * 0.5, 34 + sin(time * 5) * 3, 0, TAU, 48, Color(1, 0.85, 0.45, 0.3), 2, true)
