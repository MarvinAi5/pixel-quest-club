extends Node2D
# course_day selects the rules introduced by that day's checkpoint.
@export var course_day: int = 30
@export var time_limit: float = 60.0
@export var target: int = 5
var score := 0
enum State { PLAYING, WON, LOST }
var state: State = State.PLAYING
var muted := false
@onready var player: CharacterBody2D = $Player
@onready var round_timer: Timer = $RoundTimer

func _ready() -> void:
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
    player.visible = course_day >= 9
    player.enabled = course_day >= 10
    target = 1 if course_day < 13 else 5
    for i in range(1, 6):
        var treasure: Area2D = get_node("Treasure%s" % i)
        if course_day < 11 or (course_day < 13 and i > 1):
            treasure.queue_free()
        else:
            treasure.collected.connect(add_score)
    if course_day < 15:
        $Hazard.queue_free()
    else:
        $Hazard.hit.connect(lose)
    round_timer.timeout.connect(lose)
    if course_day >= 17:
        round_timer.start(time_limit)
    $CanvasLayer/Restart.pressed.connect(restart)
    $CanvasLayer/Restart.visible = course_day >= 18
    $CanvasLayer/Mute.toggled.connect(set_muted)
    $CanvasLayer/Mute.visible = course_day >= 19
    $CanvasLayer/Restart.focus_neighbor_right = NodePath("../Mute")
    $CanvasLayer/Mute.focus_neighbor_left = NodePath("../Restart")
    if course_day >= 25:
        $CanvasLayer/Restart.grab_focus()
    update_score()
    $CanvasLayer/Message.text = "Arrows / WASD / left stick: move. Collect the gold shapes."

func add_action(action: String, arrow: int, letter: int, axis: int, value: float) -> void:
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

func add_score() -> void:
    if state != State.PLAYING or course_day < 12:
        return
    score += 1
    update_score()
    if course_day >= 19 and not muted:
        $PickupSound.play()
    if score >= target and course_day >= 16:
        finish(State.WON, "You win! Press R / controller A or Replay.")

func update_score() -> void:
    $CanvasLayer/Score.text = "Score: %s / %s" % [score, target]

func finish(next_state: State, message: String) -> void:
    if state != State.PLAYING:
        return
    state = next_state
    player.enabled = false
    round_timer.stop()
    $CanvasLayer/Message.text = message

func lose() -> void:
    finish(State.LOST, "Try another route! Press R / controller A or Replay.")

func restart() -> void:
    get_tree().reload_current_scene()

func set_muted(value: bool) -> void:
    muted = value

func _process(_delta: float) -> void:
    if course_day >= 18 and Input.is_action_just_pressed("restart"):
        restart()
