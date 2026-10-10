extends Node

var players: Array[AudioStreamPlayer] = []
var sounds := {"fill": "res://assets/audio/fill.wav", "tap": "res://assets/audio/tap.wav", "hint": "res://assets/audio/hint.wav", "win": "res://assets/audio/win.wav"}
var voice := 0

func _ready() -> void:
	for key in sounds:
		sounds[key] = load(sounds[key])
	for i in range(4):
		var player := AudioStreamPlayer.new()
		add_child(player)
		players.append(player)

func play(kind: String, pitch: float = 1.0) -> void:
	if not Progress.setting("sound") or not sounds.has(kind):
		return
	var player := players[voice % players.size()]
	voice += 1
	player.stream = sounds[kind]
	player.pitch_scale = pitch
	player.volume_db = -7
	player.play()

func haptic() -> void:
	if Progress.setting("haptics") and OS.has_feature("mobile"):
		Input.vibrate_handheld(18)
