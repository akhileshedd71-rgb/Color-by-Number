@tool
extends Control
@export var dark := false
@export var seed_value := 41

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	resized.connect(queue_redraw)

func _draw() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_value
	if dark:
		draw_rect(Rect2(Vector2.ZERO, size), Color("211440"))
		for i in range(5):
			var c := Vector2(size.x * rng.randf(), size.y * rng.randf())
			draw_circle(c, rng.randf_range(40, 100), Color(0.4, 0.24, 0.65, 0.04))
	for i in range(36 if dark else 18):
		var p := Vector2(rng.randf() * size.x, rng.randf() * size.y)
		var c := Color("B69DE9") if dark else Color("DDD0FA")
		c.a = rng.randf_range(0.25, 0.6)
		var radius := rng.randf_range(1.0, 2.0)
		draw_circle(p, radius, c)
		if i % 8 == 0:
			draw_line(p - Vector2(5, 0), p + Vector2(5, 0), c, 1.2, true)
			draw_line(p - Vector2(0, 5), p + Vector2(0, 5), c, 1.2, true)
