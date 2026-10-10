extends Control
var toast_tween: Tween

func _ready() -> void:
	Progress.save_failed.connect(func(): _toast("Saving is unavailable. Please check device storage."))
	get_tree().auto_accept_quit = false
	get_window().size_changed.connect(_apply_safe_area)
	_apply_safe_area()
	_gallery()

func _apply_safe_area() -> void:
	if not OS.has_feature("mobile"): return
	var safe := DisplayServer.get_display_safe_area()
	var screen := Vector2(get_window().size)
	if screen.x <= 0 or screen.y <= 0: return
	var ratio := get_viewport_rect().size / screen
	offset_left = safe.position.x * ratio.x
	offset_top = safe.position.y * ratio.y
	offset_right = -(screen.x - safe.end.x) * ratio.x
	offset_bottom = -(screen.y - safe.end.y) * ratio.y

func _gallery() -> void:
	$Game.hide()
	$Reward.hide()
	$Gallery.show()
	$Gallery.refresh()

func _open_art(art: ArtworkData) -> void:
	$Gallery.hide()
	$Reward.hide()
	$Game.show()
	$Game.start(art)

func _complete(art: ArtworkData) -> void:
	$Game.hide()
	$Reward.show()
	$Reward.celebrate(art)

func _admire() -> void:
	$Reward.hide()
	$Game.show()

func _settings() -> void:
	$Settings.open()

func _toast(text: String) -> void:
	if toast_tween and toast_tween.is_running(): toast_tween.kill()
	$Toast/Text.text = text
	$Toast.modulate.a = 1.0
	$Toast.show()
	toast_tween = create_tween()
	toast_tween.tween_interval(2.8)
	toast_tween.tween_property($Toast, "modulate:a", 0.0, .3)
	toast_tween.tween_callback($Toast.hide)

func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_GO_BACK_REQUEST:
		if $Settings.visible: $Settings.hide()
		elif $Game.visible: $Game._on_back()
		elif $Reward.visible: _gallery()
	elif what == NOTIFICATION_WM_CLOSE_REQUEST:
		Progress.save()
		get_tree().quit()
	elif what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		if is_instance_valid($Game): $Game.board.cancel_input()
	elif what == NOTIFICATION_APPLICATION_PAUSED:
		if is_instance_valid(Progress): Progress.save()
		if is_instance_valid($Game): $Game.board.cancel_input()

func _unhandled_key_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		if $Settings.visible: $Settings.hide()
		elif $Game.visible: $Game._on_back()
		elif $Reward.visible: _gallery()
