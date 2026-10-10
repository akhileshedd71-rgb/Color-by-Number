extends Button

func _ready() -> void:
	button_down.connect(_squash.bind(true))
	button_up.connect(_squash.bind(false))
	mouse_exited.connect(_squash.bind(false))
	pressed.connect(func(): Sound.play("tap"))
	resized.connect(func(): pivot_offset = size * 0.5)

func _squash(down: bool) -> void:
	pivot_offset = size * 0.5
	create_tween().tween_property(self, "scale", Vector2.ONE * (0.95 if down else 1.0), 0.10).set_trans(Tween.TRANS_QUAD)
