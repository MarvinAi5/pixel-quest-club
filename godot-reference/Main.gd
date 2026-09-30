extends Node2D
# Small reference game. Uses simple shapes so beginners can inspect every rule.
# Main owns position, score and state; later lessons split these into scenes.
var player := Vector2(90, 225)
var treasures: Array[Vector2] = [Vector2(210,100), Vector2(350,320), Vector2(470,120), Vector2(600,340), Vector2(710,180)]
var hazard := Vector2(410,225)
var score := 0
var state := "playing"
var speed := 220.0
var font: Font = ThemeDB.fallback_font

func _ready():
    add_action("move_left", KEY_LEFT, KEY_A, JOY_AXIS_LEFT_X, -1.0)
    add_action("move_right", KEY_RIGHT, KEY_D, JOY_AXIS_LEFT_X, 1.0)
    add_action("move_up", KEY_UP, KEY_W, JOY_AXIS_LEFT_Y, -1.0)
    add_action("move_down", KEY_DOWN, KEY_S, JOY_AXIS_LEFT_Y, 1.0)
    if not InputMap.has_action("restart"):
        InputMap.add_action("restart")
        var key := InputEventKey.new()
        key.physical_keycode = KEY_R
        InputMap.action_add_event("restart", key)
        var button := InputEventJoypadButton.new()
        button.button_index = JOY_BUTTON_A
        InputMap.action_add_event("restart", button)

func add_action(action: String, arrow: int, letter: int, axis: int, value: float):
    if InputMap.has_action(action):
        return
    InputMap.add_action(action, 0.2)
    for code in [arrow, letter]:
        var key := InputEventKey.new()
        key.physical_keycode = code
        InputMap.action_add_event(action, key)
    var motion := InputEventJoypadMotion.new()
    motion.axis = axis
    motion.axis_value = value
    InputMap.action_add_event(action, motion)

func _process(delta):
    if Input.is_action_just_pressed("restart"):
        get_tree().reload_current_scene()
    if state == "playing":
        var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
        player += direction * speed * delta
        player.x = clampf(player.x, 24, 776)
        player.y = clampf(player.y, 70, 420)
        for i in range(treasures.size() - 1, -1, -1):
            if player.distance_to(treasures[i]) < 30:
                treasures.remove_at(i)
                score += 1
        if player.distance_to(hazard) < 40:
            state = "lost"
        elif score == 5:
            state = "won"
    queue_redraw()

func _draw():
    draw_rect(Rect2(0,0,800,450), Color("fff9ed"))
    draw_string(font, Vector2(24,36), "Pixel Quest Collector   |   Score: %s / 5" % score, HORIZONTAL_ALIGNMENT_LEFT, -1, 23, Color("18223b"))
    draw_circle(hazard, 24, Color("bc581d"))
    for treasure in treasures:
        draw_circle(treasure, 14, Color("ffbf42"))
    draw_circle(player, 21, Color("007f83"))
    draw_string(font, Vector2(24,443), "Arrows / WASD / left stick to move. R or controller A to restart.", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("18223b"))
    if state != "playing":
        var message := "You win!" if state == "won" else "Try another route!"
        draw_rect(Rect2(230,190,340,70), Color("18223b"))
        draw_string(font, Vector2(255,235), message + "  R / A to replay", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color.WHITE)
