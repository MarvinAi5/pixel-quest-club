extends CharacterBody2D
@export var speed: float = 220.0
var enabled := true

func _physics_process(_delta: float) -> void:
    if not enabled:
        velocity = Vector2.ZERO
        return
    var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
    velocity = direction * speed
    move_and_slide()
    position.x = clampf(position.x, 24.0, 776.0)
    position.y = clampf(position.y, 70.0, 420.0)
