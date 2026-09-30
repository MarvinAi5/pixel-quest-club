extends Area2D
signal collected
var taken := false

func _ready() -> void:
    body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node2D) -> void:
    if body is CharacterBody2D and not taken:
        taken = true
        collected.emit()
        queue_free()
