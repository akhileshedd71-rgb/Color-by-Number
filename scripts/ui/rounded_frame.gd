@tool
extends Control
@export var radius := 20.0
@export var frame_color := Color("F5F0FF")

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	resized.connect(queue_redraw)

func _draw() -> void:
	var corner := PackedVector2Array([Vector2.ZERO, Vector2(radius, 0)])
	for i in range(17):
		var angle := -PI * .5 - float(i) / 16 * PI * .5
		corner.append(Vector2.ONE * radius + Vector2(cos(angle), sin(angle)) * radius)
	for c in range(4):
		var polygon := PackedVector2Array()
		for p in corner:
			polygon.append(Vector2(size.x - p.x if c % 2 == 1 else p.x, size.y - p.y if c >= 2 else p.y))
		draw_colored_polygon(polygon, frame_color)
