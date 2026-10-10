extends Control
func open() -> void:
	$Center/Panel/Content/Sound.set_pressed_no_signal(Progress.setting("sound"))
	$Center/Panel/Content/Haptics.set_pressed_no_signal(Progress.setting("haptics"))
	show()

func _on_sound(value: bool) -> void:
	Progress.set_setting("sound", value)

func _on_haptics(value: bool) -> void:
	Progress.set_setting("haptics", value)

func _on_close() -> void:
	hide()
