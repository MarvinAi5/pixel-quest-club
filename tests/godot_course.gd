extends SceneTree
var checks: Array = []
var failures: Array = []
var day := 8
func _initialize() -> void:
    call_deferred("run_course")
func verify(value: bool, message: String) -> void:
    if not value:
        failures.append("dev-%s: %s" % [day, message])
func frames(count: int = 4) -> void:
    for _i in range(count):
        await physics_frame
        await process_frame
func fresh(d: int):
    var game = load("res://Main.tscn").instantiate()
    game.course_day = d
    root.add_child(game)
    current_scene = game
    await frames()
    return game
func run_course() -> void:
    for d in range(8, 31):
        day = d
        var game = await fresh(d)
        var item := {"id": "dev-%s" % d, "checks": ["Main scene and scripts load in Godot"]}
        verify(game.score == 0, "initial score zero")
        if d >= 10:
            var start_x: float = game.player.position.x
            Input.action_press("move_right")
            await frames(8)
            Input.action_release("move_right")
            verify(game.player.position.x > start_x, "physics movement from Input Map")
            item.checks.append("Input action and CharacterBody2D movement")
        if d >= 11:
            var treasure = game.get_node("Treasure1")
            game.player.position = treasure.position
            await frames(6)
            verify(not is_instance_valid(treasure), "body_entered removes pickup")
            if d >= 12:
                verify(game.score == 1, "collected signal scores once")
                verify(game.get_node("CanvasLayer/Score").text.begins_with("Score: 1"), "score label updates")
            item.checks.append("Physics pickup, signal and score label")
        if d >= 13:
            for i in range(2, 6):
                game.player.position = game.get_node("Treasure%s" % i).position
                await frames(6)
            verify(game.score == 5, "five pickups")
            if d >= 16:
                verify(game.state == game.State.WON, "winning state")
                verify(not game.player.enabled, "movement disabled after win")
                verify(game.round_timer.is_stopped(), "timer stopped after win")
            item.checks.append("Five reusable pickups and winning state")
        game.queue_free()
        await frames()
        if d >= 15:
            game = await fresh(d)
            game.player.position = game.get_node("Hazard").position
            await frames(6)
            verify(game.state == game.State.LOST, "hazard losing state")
            var old_score: int = game.score
            game.add_score()
            verify(game.score == old_score, "score frozen after ending")
            item.checks.append("Hazard, losing state and scoring guard")
            game.queue_free()
            await frames()
        if d >= 17:
            game = await fresh(d)
            game.round_timer.start(0.05)
            await create_timer(0.15).timeout
            verify(game.state == game.State.LOST, "timeout losing state")
            item.checks.append("Actual Timer timeout")
            if d >= 18:
                game.get_node("CanvasLayer/Restart").pressed.emit()
                await frames(8)
                game = current_scene
                verify(game.score == 0 and game.state == game.State.PLAYING, "scene reload restores state")
                verify(game.has_node("Treasure1"), "scene reload restores treasures")
                item.checks.append("Replay button and actual scene reload")
            if d >= 19:
                game.get_node("CanvasLayer/Mute").button_pressed = true
                verify(game.muted, "mute toggled signal")
                game.add_score()
                verify(game.score == 1, "muted pickup still scores")
                item.checks.append("Mute and visual score feedback")
            if d >= 25:
                verify(game.get_node("CanvasLayer/Restart").has_focus(), "initial keyboard/controller UI focus")
                verify(game.get_node("CanvasLayer/Restart").focus_neighbor_right == NodePath("../Mute"), "focus neighbor")
                item.checks.append("Focusable menu and focus neighbor")
            game.queue_free()
            await frames()
        item["status"] = "technical-pattern-passed"
        checks.append(item)
        print("PASS Godot dev-%s" % d)
    var output := {"status": "passed" if failures.is_empty() else "failed", "engine": Engine.get_version_info(), "lessons": checks, "failures": failures, "limits": "Headless desktop engine tests; no actual Retroid, controller or human playtest."}
    var file = FileAccess.open("res://../qa-artifacts/godot-results.json", FileAccess.WRITE)
    file.store_string(JSON.stringify(output, "  "))
    for failure in failures:
        push_error(failure)
    quit(0 if failures.is_empty() else 1)
