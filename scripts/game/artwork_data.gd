class_name ArtworkData
extends Resource

@export var id: String
@export var title: String
@export_enum("Florals", "Animals", "Mandalas", "Places") var category: String = "Florals"
@export_enum("Easy", "Medium", "Intricate") var difficulty: String = "Easy"
@export var minutes: int = 5
@export var unlock_after: int = 0
@export_file("*.json") var regions_path: String
@export var thumbnail: Texture2D
@export var background: Color = Color("211449")

func read_regions() -> Dictionary:
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(regions_path))
	return data if data is Dictionary else {}
