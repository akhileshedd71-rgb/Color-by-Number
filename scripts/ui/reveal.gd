extends Control
const REGION = preload("res://scenes/game/region.tscn")
var generation := 0

func _ready() -> void:
	resized.connect(_layout)

func _layout() -> void:
	var fit := minf(size.x, size.y) / 600.0 * .94
	$Artwork.scale = Vector2.ONE * fit
	$Artwork.position = size * .5 - Vector2(300, 300) * fit

func play(art: ArtworkData) -> void:
	generation += 1
	var this_run := generation
	for child in $Artwork.get_children():
		$Artwork.remove_child(child)
		child.queue_free()
	var data := art.read_regions()
	var lookup: Dictionary = {}
	for shape in data.shapes:
		var r: ColorRegion = REGION.instantiate()
		$Artwork.add_child(r)
		r.configure(shape, data.palette, [])
		r.number.hide()
		lookup[r.region_id] = r
	_layout()
	var order := Progress.filled_ids(art.id)
	for id in order:
		if this_run != generation or not is_visible_in_tree(): return
		if lookup.has(id): lookup[id].fill_region()
		await get_tree().create_timer(1.7 / maxf(order.size(), 1)).timeout
