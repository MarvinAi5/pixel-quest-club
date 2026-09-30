"""Complete, staged Main scripts matching the nodes introduced in each lesson."""
def main_script(day):
 if day<12:return 'extends Node2D\n\nfunc _ready() -> void:\n    print("Main scene is running")\n'
 state=day>=15;timer=day>=17;replay=day>=18;sound=day>=19;win=day>=16
 s='extends Node2D\nvar score := 0\nvar target := 5\n'
 if state:s+='enum State { PLAYING, WON, LOST }\nvar state: State = State.PLAYING\n'
 if sound:s+='var muted := false\n'
 s+='\nfunc _ready() -> void:\n    for child in get_children():\n        if child.has_signal("collected"):\n            child.collected.connect(add_score)\n'
 if state:s+='    $Hazard.hit.connect(lose)\n'
 if timer:s+='    $RoundTimer.timeout.connect(lose)\n    $RoundTimer.start(60.0)\n'
 if replay:s+='    $CanvasLayer/Restart.pressed.connect(restart)\n'
 if sound:s+='    $CanvasLayer/Mute.toggled.connect(set_muted)\n'
 if day>=25:s+='    $CanvasLayer/Restart.focus_neighbor_right = NodePath("../Mute")\n    $CanvasLayer/Mute.focus_neighbor_left = NodePath("../Restart")\n    $CanvasLayer/Restart.grab_focus()\n'
 s+='    update_score()\n\nfunc add_score() -> void:\n'
 if state:s+='    if state != State.PLAYING:\n        return\n'
 s+='    score += 1\n    update_score()\n'
 if sound:s+='    if not muted:\n        $PickupSound.play()\n'
 if win:s+='    if score >= target:\n        finish(State.WON, "You win! Replay to try again.")\n'
 s+='\nfunc update_score() -> void:\n    $CanvasLayer/Score.text = "Score: %s / %s" % [score, target]\n'
 if state:
  s+='\nfunc finish(next_state: State, message: String) -> void:\n    if state != State.PLAYING:\n        return\n    state = next_state\n    $Player.enabled = false\n'
  if timer:s+='    $RoundTimer.stop()\n'
  s+='    $CanvasLayer/Message.text = message\n\nfunc lose() -> void:\n    finish(State.LOST, "Try another route! Replay to restart.")\n'
 if replay:s+='\nfunc restart() -> void:\n    get_tree().reload_current_scene()\n\nfunc _process(_delta: float) -> void:\n    if Input.is_action_just_pressed("restart"):\n        restart()\n'
 if sound:s+='\nfunc set_muted(value: bool) -> void:\n    muted = value\n'
 return s
