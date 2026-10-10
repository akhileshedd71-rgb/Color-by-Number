class_name ColorRegion
extends Node2D

var region_id: String
var color_index: int
var target: Color
var points: PackedVector2Array
var label_position: Vector2
var label_radius := 10.0
var label_scale := 1.0
var filled := false
var selected := false
var fill_tween: Tween
@onready var polygon: Polygon2D = $Polygon
@onready var outline: Line2D = $Outline
@onready var number: Label = $Number

func configure(shape: Dictionary, palette: Array, saved: Array) -> void:
	region_id = shape.id
	label_radius = float(shape.get("label_radius", 10.0))
	color_index = int(shape.color)
	target = Color(palette[color_index])
	for p in shape.points:
		points.append(Vector2(p[0], p[1]))
	polygon.polygon = points
	var bounds := Rect2(points[0], Vector2.ZERO)
	for point in points:
		bounds = bounds.expand(point)
	polygon.material = polygon.material.duplicate()
	polygon.material.set_shader_parameter("region_min", bounds.position)
	polygon.material.set_shader_parameter("region_size", bounds.size)
	outline.points = points
	label_position = Vector2(shape.label[0], shape.label[1])
	number.position = label_position - Vector2(18, 16)
	number.text = str(color_index + 1)
	filled = region_id in saved
	refresh()

func refresh() -> void:
	number.visible = not filled and label_radius * label_scale >= 6.8
	polygon.color = target if filled else (Color("E7DDFE") if selected else Color("FAF8FF"))
	number.add_theme_color_override("font_color", Color("603BB1") if selected else Color("837C97"))
	outline.default_color = Color("332447")
	outline.width = 1.8

func set_selected(index: int) -> void:
	selected = color_index == index
	if not filled:
		refresh()

func fill_region(animated: bool = true) -> void:
	filled = true
	number.hide()
	if fill_tween and fill_tween.is_running():
		fill_tween.kill()
	if animated:
		fill_tween = create_tween()
		fill_tween.tween_property(polygon, "color", target.lightened(0.26), 0.10)
		fill_tween.tween_property(polygon, "color", target, 0.22)
	else:
		polygon.color = target

func flash_wrong() -> void:
	var tw := create_tween()
	tw.tween_property(number, "scale", Vector2.ONE * 1.35, 0.1)
	tw.tween_property(number, "scale", Vector2.ONE, 0.16)

func hit(local_point: Vector2) -> bool:
	return Geometry2D.is_point_in_polygon(local_point, points)

func update_label(art_scale: float) -> void:
	label_scale = art_scale
	var visual_scale := clampf(1.0 / maxf(art_scale, .1), .24, 1.5)
	number.scale = Vector2.ONE * visual_scale
	number.position = label_position - Vector2(18, 16) * visual_scale
	number.visible = not filled and label_radius * art_scale >= 6.8
