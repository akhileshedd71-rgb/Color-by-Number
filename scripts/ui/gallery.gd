extends Control
signal art_selected(art: ArtworkData)
signal settings_requested
signal message(text: String)
const CARD = preload("res://scenes/ui/art_card.tscn")
var category := "All"
var mode := "Library"
@onready var grid: GridContainer = $Scroll/Content/Grid
@onready var content: VBoxContainer = $Scroll/Content

func _ready() -> void:
	for b in $Scroll/Content/CategoryScroll/Categories.get_children():
		b.pressed.connect(_filter.bind(b.name))
	for b in $Navigation/Tabs.get_children():
		b.pressed.connect(_navigate.bind(b.name))
	$Header/Stars.pressed.connect(func(): message.emit("%d masterpieces made. New art unlocks at 3 and 6!" % Progress.completed_count()))
	refresh()

func refresh() -> void:
	for child in grid.get_children():
		grid.remove_child(child)
		child.queue_free()
	$Header/Stars.text = str(Progress.completed_count())
	var daily := mode == "Daily"
	var collection := mode == "MyArt"
	content.get_node("Feature").visible = not collection
	content.get_node("CategoryScroll").visible = not daily
	content.get_node("Greeting").text = "A fresh reason to smile." if daily else ("Your color story." if collection else "A little color. A little joy.")
	content.get_node("Section/Title").text = "Today's little escape" if daily else ("Made with a little magic" if collection else "Find your next favorite")
	content.get_node("Feature/Eyebrow").text = "DAILY MOMENT · " + Time.get_date_string_from_system() if daily else "A MOMENT OF MAGIC"
	content.get_node("Feature/Title").text = "A new day.\nA new hue." if daily else "Let your\ncolors bloom."
	var total := 0
	for art in Progress.catalog:
		if daily and art.id != Progress.daily_art().id: continue
		if not daily and category != "All" and art.category != category: continue
		if collection and Progress.filled_ids(art.id).is_empty(): continue
		var card := CARD.instantiate()
		grid.add_child(card)
		card.configure(art)
		card.chosen.connect(_choose)
		total += 1
	content.get_node("Section/Count").text = "ONE FOR TODAY" if daily else (str(total) + " ARTWORKS")
	content.get_node("Empty").visible = total == 0
	for b in $Navigation/Tabs.get_children():
		b.theme_type_variation = &"PurpleButton" if b.name == mode else &"TabButton"
		if b.name in ["Library", "Daily"]:
			var icon_name := "gallery" if b.name == "Library" else "calendar"
			b.icon = load("res://assets/icons/" + icon_name + ("_light" if b.name == mode else "") + ".svg")
	for b in $Scroll/Content/CategoryScroll/Categories.get_children():
		b.theme_type_variation = &"PurpleButton" if b.name == category else &"TabButton"

func _filter(value: String) -> void:
	category = value
	refresh()

func _navigate(value: String) -> void:
	mode = value
	category = "All"
	$Scroll.scroll_vertical = 0
	refresh()

func _choose(art: ArtworkData) -> void:
	if not Progress.is_unlocked(art):
		message.emit("Complete %d more artworks to unlock %s." % [maxi(0, art.unlock_after - Progress.completed_count()), art.title])
		return
	Sound.play("tap")
	art_selected.emit(art)

func _on_feature() -> void:
	_choose(Progress.daily_art() if mode == "Daily" else Progress.catalog[0])

func _on_settings() -> void:
	settings_requested.emit()
