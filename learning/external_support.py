from pathlib import Path
from learning.godot_guides import main_script
ROOT=Path(__file__).resolve().parents[1]
SCRATCH={
15:('Open Scratch Create. Find the Stage on the right, sprite list below it, and Code workspace. Rename a sprite Player. File → Save to your computer downloads an editable .sb3.', 'Player: choose any costume\nFile → Save to your computer\nFile → Load from your computer', 'The .sb3 reopens and you can identify the stage, sprite list and Code tab.'),
16:('Select Player. Events has the yellow green-flag and key hats; Motion has blue positioning blocks. Stack the position block under the green flag. Make a separate key-event stack.', 'Player:\nwhen green flag clicked\ngo to x: -150 y: 0\n\nwhen [right arrow] key pressed\nchange x by 10', 'Green flag restores x=-150, y=0. One right-key press changes x by 10.'),
17:('Replace the separate key-event stack from yesterday with this forever-loop stack; keeping both would move the player twice. Control has orange forever and if blocks; Sensing has the key reporter.', 'Player:\nwhen green flag clicked\ngo to x: -150 y: 0\nforever\n  if <key [right arrow] pressed?> then\n    change x by 4', 'Holding right moves continuously; releasing it stops movement.'),
18:('Add a Treasure sprite. Position it near Player. Wait 0.1 seconds after show so the player and score can reset before collision checks. Use one wait-until pickup stack rather than a forever loop that could keep responding after the sprite hides. Select the actual Player name in touching.', 'Treasure:\nwhen green flag clicked\nshow\nwait 0.1 seconds\nwait until <touching [Player]?>\nhide', 'Treasure hides once on contact and returns when the green flag is pressed.'),
19:('Variables → Make a Variable → score → For all sprites. Reset it once, on the Stage. Add change score by 1 immediately before hide in the Treasure stack.', 'Stage:\nwhen green flag clicked\nset [score] to 0\n\nTreasure:\nwhen green flag clicked\nshow\nwait 0.1 seconds\nwait until <touching [Player]?>\nchange [score] by 1\nhide', 'One treasure increases score once. Green flag resets score and shows it again.'),
20:('Write or draw your player, action, goal and hazard. Keep five treasures and one stationary hazard as the small reference design. You may choose different art without changing the rules.', 'Plan:\nPlayer: your character\nAction: move with arrows\nGoal: collect 5 treasures\nChallenge: avoid 1 hazard\nReplay: green flag', 'Your plan names the controls, five-pickup goal, one challenge and replay.'),
21:('Select Player. Add left, up and down conditions inside the same forever loop, next to right. Each is a separate if, so diagonal input is possible.', 'Player: inside forever\nif <key [right arrow] pressed?> then change x by 4\nif <key [left arrow] pressed?> then change x by -4\nif <key [up arrow] pressed?> then change y by 4\nif <key [down arrow] pressed?> then change y by -4', 'All four directions work; green flag restores the starting position.'),
22:('Right-click a tested Treasure sprite and duplicate it four times. Move the five sprites to different positions. Each sprite needs its own show/wait-until/change-score/hide stack. Keep the one Stage score reset.', 'Each of 5 Treasure sprites:\nwhen green flag clicked\nshow\nwait 0.1 seconds\nwait until <touching [Player]?>\nchange [score] by 1\nhide', 'Five distinct pickups produce score 5; standing still cannot count one twice.'),
23:('Create playing for all sprites. Stage sets it to 1 on green flag. Put all Player direction conditions inside if playing=1. In each Treasure, guard the score increment with playing=1. Hazard waits for contact once and broadcasts Lose. Stage receives Lose and sets playing=0.', 'Stage:\nwhen green flag clicked → set [playing] to 1\nwhen I receive [Lose] → set [playing] to 0\n\nPlayer: inside forever\nif <playing = 1> then\n  [all four direction checks]\n\nEach Treasure: after wait until touching Player\nif <playing = 1> then change [score] by 1\nhide\n\nHazard:\nwhen green flag clicked\nwait 0.1 seconds\nwait until <touching [Player]?>\nbroadcast [Lose]\n\nPlayer:\nwhen I receive [Lose]\nsay [Try another route! Green flag to replay.]', 'A hazard broadcasts Lose once. Movement and scoring stop until green flag.'),
24:('On Stage, add a separate green-flag stack that waits for score=5 then broadcasts Win. Receive Win to set playing=0. Player receives Win and says the message. Test green flag after each ending.', 'Stage:\nwhen green flag clicked\nwait until <score = 5>\nbroadcast [Win]\n\nwhen I receive [Win]\nset [playing] to 0\n\nPlayer:\nwhen I receive [Win]\nsay [You win! Green flag to replay.]\n\nExisting green-flag stacks reset score, playing, Player and every Treasure.', 'Winning stops movement; green flag restores score, start position and all five treasures after win or loss.'),
25:('Add a short Say instruction under a separate Player green flag. Explain controls, goal, hazard and replay. Ask a player to begin without coaching.', 'Player:\nwhen green flag clicked\nsay [Arrows move. Collect 5. Avoid orange. Green flag replays.]', 'A new player can find the controls and goal. Human playtest still needed.'),
26:('Keep a dated .sb3 backup. Choose one missing essential, not an extra feature. Replay one pickup, hazard loss, full win and green-flag replay.', 'Checklist: controls → pickup → loss → win → replay\nFile → Save to your computer', 'The chosen essential works and a working .sb3 is saved.'),
27:('Ask two people to play. Record where they get stuck and what they understand. This is an observation task; automated tests cannot replace the people.', 'Observe: start, controls, goal, loss, replay\nWrite two observations; do not coach the first attempt.', 'Two human observations are recorded and one improvement is chosen.'),
28:('Fix one issue from the playtest. Change one value or rule at a time. Replay a missed pickup, a hazard, all five pickups and restart. Keep the earlier .sb3.', 'Regression checklist:\nmissed pickup leaves score unchanged\nhazard stops play\n5 pickups broadcast Win\ngreen flag resets everything', 'The fix works without breaking win, loss or replay.'),
29:('File → Save to your computer creates the editable .sb3. Give it a dated name. File → Load from your computer reopens it; test it again.', 'File → Save to your computer\nFile → Load from your computer\nGreen flag → test movement/pickup/replay', 'The saved .sb3 loads with the same sprites and functioning rules.'),
30:('Show your game. Point to the score variable, forever loop and if condition. Change a speed value, test the change, then save the new version.', 'Explain: score, forever, if\nChange x/y movement value 4 → 3\nTest → Save .sb3', 'Your game runs and you can explain and change a rule. Human explanation is still required.')}
GODOT_NOTES={
8:'Godot 4 Standard → New Project → Compatibility. In the 2D workspace, add Node2D named Main, save Main.tscn, and use F5 to select it as main scene. F6 runs the currently open scene.',
9:'New scene → CharacterBody2D named Player. Add Polygon2D named Art and draw a small square, plus CollisionShape2D with a CircleShape2D radius 18. Save Player.tscn; drag it into Main. Move it away from the origin so it is visible.',
10:'Select Player and attach Player.gd. Project → Project Settings → Input Map: add move_left/right/up/down. Bind arrows and WASD, plus left-stick negative/positive X/Y axes with deadzone 0.2. F5 tests Main, not just the standalone Player scene.',
11:'New scene → Area2D named Treasure. Add visible art and CollisionShape2D (circle radius 12). Player is on collision layer 1; Treasure mask includes layer 1. Connect body_entered once: the reference uses code in _ready; do not also connect it in the Signals panel. Save Treasure.tscn, drag one instance into Main, and name that instance Treasure1.',
12:'Main owns score. Add CanvasLayer → Score (Label) and Message (Label), with those exact names. Treasure declares signal collected; The Main.gd example below connects any child with a collected signal to add_score in _ready. Replace Main.gd with this day’s complete example when comparing; keep earlier source backups. The connection must exist before the first pickup.',
13:'Save Treasure.tscn. Drag five instances into Main, name them Treasure1 through Treasure5, and give them distinct reachable positions. The Main.gd example below discovers and connects all five signals. Edit the original Treasure scene to change every instance.',
14:'Save all scenes/scripts. Copy the entire project folder, including project.godot and scenes, or commit the source. Reopen the copy and replay movement and one pickup. Exported files are not source backups.',
15:'Create Hazard.tscn as Area2D with visible art and CollisionShape2D. Its body_entered emits hit for a CharacterBody2D. Instance it in Main; Main connects Hazard.hit to lose. Use the Main.gd file in the day-15 reference below as well as Hazard.gd. Use layer 1 in the detection mask.',
16:'Main has one enum State { PLAYING, WON, LOST }. finish changes state once, disables Player.enabled, stops RoundTimer and updates Message. add_score returns early after an ending.',
17:'Add Timer named RoundTimer under Main. Set One Shot on; connect timeout to lose once. Start it with 60 seconds in _ready. Both finish paths stop it. Test a short limit, then restore 60.',
18:'Add restart input action with physical R key and controller A. _process checks is_action_just_pressed and reloads the current scene. Add a Button named Restart under CanvasLayer, set its text to Replay, and use the example’s pressed connection to restart. The input event is optional; the physical Retroid APK test needs a parent.',
19:'Add AudioStreamPlayer named PickupSound and a short original or licensed stream. Play it on pickup. Mute CheckButton toggles muted; scoring and visible messages must still work while muted. Downloaded reference uses an original generated tone.',
20:'Write player, action, goal, challenge and replay. Draw five reachable pickups and one avoidable hazard. Keep a single level; choose your own theme or simple art.',
21:'Use your own project or checkpoint. Test Player movement and one Treasure body_entered signal before adding more objects. Say aloud what each script does.',
22:'Place five Treasure scene instances. Player bounds are clamped inside the 800×450 viewport; keep objects within those reachable limits. Test every pickup, including corners.',
23:'Use one hazard and leave a route around it. Adjust the Hazard CollisionShape2D radius and Player speed separately; test loss and the safe route after each change.',
24:'finish(WON, ...) happens at target; lose calls finish(LOST, ...). Both stop scoring and movement. Use Replay after each ending and confirm all treasures, score and timer reset.',
25:'Set Button/CheckButton Focus Mode to All. Set focus neighbors between Replay and Mute, and grab_focus on Replay at start. Godot built-in ui_accept accepts keyboard/controller input. Test focus navigation on a real controller separately.',
26:'Save a working source copy. Fix one essential and remove an unfinished optional feature. Retest movement, pickup, both endings and replay.',
27:'Run on computer and on your Retroid with a parent. Record controller bindings, text size, sound and performance. Automated desktop tests cannot complete this hardware activity.',
28:'Fix the most serious reproduced issue first. Replay win/loss/restart and try starting without help. Keep a known-good source copy.',
29:'Save the entire Godot source. With an adult, follow the linked Android export documentation for current SDK/JDK requirements, install export templates and export a test APK. Test that APK on the Retroid. Back up signing keys privately.',
30:'Show your game, explain a function, signal and state, then change one rule and rebuild. Your own explanation and a physical export remain human/device checks.'}

GODOT_RESULTS={
8:'Main.tscn saves and F5 opens the empty main scene without errors.',
9:'Your visible Player has a CollisionShape2D and appears as an instance in Main.',
10:'Arrow/WASD actions move the Player in four directions; releasing input stops movement.',
11:'Touching Treasure removes it once through body_entered.',
12:'One pickup increments Main.score once and changes the Score label.',
13:'Five separate Treasure instances can each be collected once, producing score 5.',
14:'The copied source project opens and the pickup route still works.',
15:'Touching Hazard changes the round to LOST and displays a losing message.',
16:'Won and lost states stop movement and scoring until replay.',
17:'The real Timer causes a loss on timeout and stops when the player wins.',
18:'Replay restores score, treasures, player position and timer. An adult must test the APK on Retroid.',
19:'Pickup sound is optional; with Mute on, score and messages still work.',
20:'Your written plan names a player, action, goal, challenge and replay.',
21:'The core movement-and-pickup loop works before decoration is added.',
22:'All five pickups are reachable within the level bounds and count once.',
23:'A player can avoid the hazard, and contact produces a clear loss. Fairness needs a human playtest.',
24:'Win and loss both work; a second round works after either ending.',
25:'Replay and Mute accept focus and UI input. A physical controller check is still required.',
26:'One essential issue is fixed and a known-good source copy is saved.',
27:'A parent and child record results on a real computer and Retroid; this is a hardware activity.',
28:'The chosen fix is followed by successful win, loss and replay tests.',
29:'The source is backed up and a test APK exports. Installing and playing it on Retroid is a device check.',
30:'You demonstrate and explain a function, signal and state, change one rule, and rebuild.'}

def enrich_external(l):
 d=l['day']
 if l['mode']=='scratch':
  note,recipe,result=SCRATCH[d];l.update(walkthrough=[note,'Use the recipe below with the named sprites. It describes blocks to assemble; it is not code to paste.','The optional .sb3 checkpoint is for comparing a working pattern. Build and change your own version.'],guideCode=recipe,success=result,checkpoint=f'scratch-day-{d}.sb3')
 elif l['mode']=='godot':
  file='Player.gd' if d in (9,10,21,22,23) else 'Treasure.gd' if d==11 else 'Hazard.gd' if d==15 else 'Main.gd'
  l.update(walkthrough=[GODOT_NOTES[d],'The optional reference uses these same node names. The Main.gd examples below include only the features learned so far; named child nodes must exist. Select Main → Course Day in Inspector to compare the feature set for this lesson.','Build in your own project. Use the reference to locate the pattern, rather than copying a finished game without understanding it.'],guideCode=main_script(d) if file=='Main.gd' else (ROOT/'godot-reference'/file).read_text(),guideMain=main_script(d),guideFile=file,success=GODOT_RESULTS[d])
 return l
