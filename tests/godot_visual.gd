extends SceneTree
func _initialize() -> void:
    call_deferred("capture_game")
func settle() -> void:
    for _i in range(6):
        await physics_frame
        await process_frame
    await RenderingServer.frame_post_draw
func capture_game() -> void:
    var game = load("res://Main.tscn").instantiate()
    root.add_child(game)
    current_scene = game
    await settle()
    var out = ProjectSettings.globalize_path("res://").path_join("../qa-artifacts")
    root.get_texture().get_image().save_png(out.path_join("godot-playing.png"))
    for i in range(1, 6):
        game.player.position = game.get_node("Treasure%s" % i).position
        await settle()
    assert(game.state == game.State.WON)
    root.get_texture().get_image().save_png(out.path_join("godot-winning.png"))
    quit()
