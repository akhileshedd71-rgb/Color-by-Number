extends Button
signal chosen(art: ArtworkData)
var art: ArtworkData

func _ready() -> void:
	pressed.connect(func(): chosen.emit(art))
	button_down.connect(func(): _press(true))
	button_up.connect(func(): _press(false))
	resized.connect(_resize_preview)

func configure(value: ArtworkData) -> void:
	art = value
	$PreviewPanel/Preview.texture = art.thumbnail
	$Title.text = art.title
	$Detail.text = "%s · %d min" % [art.difficulty, art.minutes]
	var done := Progress.is_complete(art.id)
	var count := Progress.filled_ids(art.id).size()
	$PreviewPanel/Badge.text = "COMPLETE" if done else ("IN PROGRESS" if count > 0 else "")
	if not Progress.is_unlocked(art):
		$PreviewPanel/Badge.text = "COMPLETE %d TO UNLOCK" % art.unlock_after
		$PreviewPanel/Preview.modulate = Color(0.6, 0.5, 0.75)
	_resize_preview()

func _resize_preview() -> void:
	$PreviewPanel.size.x = maxf(100, size.x - 12)

func _press(down: bool) -> void:
	pivot_offset = size * 0.5
	create_tween().tween_property(self, "scale", Vector2.ONE * (0.97 if down else 1), 0.1)
