extends Control
signal continue_requested
signal admire_requested
var art: ArtworkData

func celebrate(value: ArtworkData) -> void:
	art = value
	$ArtPanel/Preview.play(art)
	$Title.text = art.title
	$RewardText.text = "%d masterpieces · Your collection is blooming!" % Progress.completed_count()
	if Progress.completed_count() in [3, 6]:
		$RewardText.text = "New artwork unlocked! Your world just got brighter."
	$Confetti.position = size * Vector2(.5, .36)
	$Confetti.restart()
	$Confetti.emitting = true
	Sound.play("win")
	$ArtPanel.pivot_offset = $ArtPanel.size * .5
	$ArtPanel.scale = Vector2.ONE * .88
	create_tween().tween_property($ArtPanel, "scale", Vector2.ONE, .6).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)

func _on_continue() -> void:
	continue_requested.emit()

func _on_admire() -> void:
	admire_requested.emit()
