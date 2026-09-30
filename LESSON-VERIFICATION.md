# October lesson verification — September 30, 2026

**All 90 lessons reviewed; all authored technical reference checks passed.** This does not mean a learner completed every creative activity, optional extension or human/device task.

## Evidence

- [Final curriculum run](https://github.com/MarvinAi5/pixel-quest-club/actions/runs/36779397541): generated site, 51 browser activity walkthroughs, 90 guide pages, 16 Scratch checkpoints, 23 Godot feature checkpoints and the early GDScript comparisons.
- [General browser/account/load run](https://github.com/MarvinAi5/pixel-quest-club/actions/runs/36779397530): buttons, accounts, saving, five touch layouts and 100-session stress fixture.
- [ARM64 Android export run](https://github.com/MarvinAi5/pixel-quest-club/actions/runs/36778639837): actual debug APK export, Android manifest, ARM64 libraries and signature verification.

Curriculum source tested at commit `1693ebe2463eb503617f6a4275b04c727da405ed`. The reference APK uses the same native project as that commit. The browser run retained **0 old Stage instances** after the calendar walkthrough and recorded no uncaught JavaScript errors. Scratch and Godot reports recorded no test failures. Native playing/winning screenshots were inspected, including menu contrast.

## What PASS means

- **Browser:** an authored activity path executed via the actual UI, with runtime assertions for movement, timing, speech, events, score, conditions, scenes or saving as appropriate. Completion gating and return visits were checked. All three themes rendered; the detailed activity walkthrough uses Halloween. Practice fixtures provide known starting layouts. Independent creations can differ.
- **Scratch engine:** the lesson’s editable block checkpoint loaded and ran in official Scratch VM 5.0.300, renderer 2.2.84 and storage 6.2.1 in Chromium. Tests use real sprite collision sensing, inputs, broadcasts, score and .sb3 serialization. They do not drag every block in Scratch’s own editor GUI.
- **Godot engine:** matching feature checkpoints and actual printed staged Main.gd examples compile and run in Godot 4.7.2. Movement, real physics signals, labels, states, timeout, scene reload, mute and UI focus are checked where applicable. Visual screenshots use the native renderer. Editor installation/UI setup on the family computer and a physical controller are separate checks.

Instructions, hints, recall prompts, optional challenges, starting conditions and official help links were reviewed. Optional challenges are not all executed end to end. Family playtests, learner explanations, personal design choices, and physical Fire/Retroid tasks cannot be completed by automated reference tests. Completing QA checkboxes in a disposable test session is not evidence of learner mastery.

## Corrections made

- Added lesson-specific block and typed examples, visible starting conditions, walkthroughs and expected-result checks. Fresh learners start with an empty program.
- Added safe, explicit practice-stage replacement with a backup warning; preserve appropriate example commands when Scene 2 is selected.
- Replaced generic external recipes with staged Scratch and complete Godot guide patterns that match the named nodes. Added 16 editable Scratch comparison files and a scene-based Godot reference.
- Fixed generated checkpoint download URLs.
- Prevented Scratch pickup/hazard checks from racing player initialization during replay.
- Removed image listeners that retained old website stages; fixed native Mute text contrast.
- Enabled and documented the Android ETC2/ASTC import setting, then successfully exported and signature-checked a 28,268,229-byte ARM64 debug APK with a disposable debug key. No production signing key is used or distributed.

## Every lesson

| Path | Day | Lesson | Technical verification | Expected result | Human/device follow-up |
| --- | --- | --- | --- | --- | --- |
| Story Makers | 1 | Meet your companion | PASS — browser activity | Companion 1 moves right by one step (60 stage units). | Explain the result and make your own choices. |
| Story Makers | 2 | A bigger step | PASS — browser activity | 4 moves farther than 2, unless the character reaches an edge. | Explain the result and make your own choices. |
| Story Makers | 3 | First, then next | PASS — browser activity | Movement happens before the greeting. | Explain the result and make your own choices. |
| Story Makers | 4 | Up and down | PASS — browser activity | The character finishes one step lower than it began. | Explain the result and make your own choices. |
| Story Makers | 5 | Change the order | PASS — browser activity | The greeting happens before movement in one version and after it in the other. | Explain the result and make your own choices. |
| Story Makers | 6 | Take a breath | PASS — browser activity | The greeting stays visible for one second before Goodbye. | Explain the result and make your own choices. |
| Story Makers | 7 | Show what you know | PASS — browser activity | A move, speech and wait sequence runs in the order you chose. | Explain the result and make your own choices. |
| Story Makers | 8 | Do it again | PASS — browser activity | A repeat with count 3 ends in the same place as three one-step moves. | Explain the result and make your own choices. |
| Story Makers | 9 | Count the repeats | PASS — browser activity | Count 3 moves one step farther up than count 2. | Explain the result and make your own choices. |
| Story Makers | 10 | Say it your way | PASS — browser activity | Only the speech text changes; the character stays in the same place. | Explain the result and make your own choices. |
| Story Makers | 11 | Two companions | PASS — browser activity | Companion 2 greets and Companion 1 answers. | Explain the result and make your own choices. |
| Story Makers | 12 | When I tap | PASS — browser activity | Nothing runs until you press Run and tap Companion 1. | Explain the result and make your own choices. |
| Story Makers | 13 | A little tune | PASS — browser activity | The greeting and movement still work when sound is off. | Explain the result and make your own choices. |
| Story Makers | 14 | Fix the mix-up | PASS — browser activity | Hello comes before Goodbye after you fix the order. | Explain the result and make your own choices. |
| Story Makers | 15 | A new scene | PASS — browser activity | Both scenes keep separate programs; the theme belongs to the whole project. | Explain the result and make your own choices. |
| Story Makers | 16 | Go to the next scene | PASS — browser activity | Next scene changes to Scene 2 and runs its program. | Explain the result and make your own choices. |
| Story Makers | 17 | Send a message | PASS — browser activity | Send message runs Scene 2 only when its trigger is Message arrives. | Explain the result and make your own choices. |
| Story Makers | 18 | Hide and reveal | PASS — browser activity | Companion 2 is hidden during the wait, then appears. | Explain the result and make your own choices. |
| Story Makers | 19 | Choose a beginning | PASS — browser activity | Reset followed by Run repeats the same clear beginning. | Explain the result and make your own choices. |
| Story Makers | 20 | Choose your story | PASS — browser activity | Your three actions match the beginning you planned. | Personal design / real family playtest or explanation. |
| Story Makers | 21 | Build the beginning | PASS — browser activity | Your greeting and movement introduce the character. | Explain the result and make your own choices. |
| Story Makers | 22 | Build the middle | PASS — browser activity | A repeat, wait or second-character action adds a middle. | Explain the result and make your own choices. |
| Story Makers | 23 | Build the ending | PASS — browser activity | The entire story reaches a clear ending. | Explain the result and make your own choices. |
| Story Makers | 24 | Make it tappable | PASS — browser activity | Run arms the tap event; tapping Companion 1 reveals the other character. | Explain the result and make your own choices. |
| Story Makers | 25 | Make it readable | PASS — browser activity | Each short line remains visible long enough to read; sound is optional. | Explain the result and make your own choices. |
| Story Makers | 26 | Catch-up and play | PASS — browser activity | One small improvement works in your existing story. | Personal design / real family playtest or explanation. |
| Story Makers | 27 | Test with a friend | PASS — browser activity | A test player can begin and you record one confusing part. | Personal design / real family playtest or explanation. |
| Story Makers | 28 | Fix one thing | PASS — browser activity | Your chosen fix works when you replay the entire story. | Personal design / real family playtest or explanation. |
| Story Makers | 29 | Save your creation | PASS — browser activity | A downloaded project reopens with the same title, scenes and commands. | Explain the result and make your own choices. |
| Story Makers | 30 | Creator showcase | PASS — browser activity | Both scenes work; you can explain the repeat and event and change one command. | Personal design / real family playtest or explanation. |
| Game Makers | 1 | Meet the game lab | PASS — browser activity | The character moves right two steps. | Explain the result and make your own choices. |
| Game Makers | 2 | Positions on the stage | PASS — browser activity | Right changes x; up decreases the stage y position. | Explain the result and make your own choices. |
| Game Makers | 3 | Events start actions | PASS — browser activity | Start runs immediately; tap waits for Run and a character tap. | Explain the result and make your own choices. |
| Game Makers | 4 | Variables remember | PASS — browser activity | Each of the three treasures increases score once; Reset returns score to zero. | Explain the result and make your own choices. |
| Game Makers | 5 | Collect a treasure | PASS — browser activity | The score changes when the moving character touches the placed treasure. | Explain the result and make your own choices. |
| Game Makers | 6 | Conditions choose | PASS — browser activity | The condition stays silent below target and speaks after reaching target. | Explain the result and make your own choices. |
| Game Makers | 7 | Build without a recipe | PASS — browser activity | An original route collects three treasures and says a win message. | Explain the result and make your own choices. |
| Game Makers | 8 | Loops save repetition | PASS — browser activity | Three single moves and a repeat with count 3 end at the same place. | Explain the result and make your own choices. |
| Game Makers | 9 | Tune the speed | PASS — browser activity | Speed changes elapsed movement time, not final distance. | Explain the result and make your own choices. |
| Game Makers | 10 | Tap controls | PASS — browser activity | Direction buttons and arrow keys move the player after Run. | Explain the result and make your own choices. |
| Game Makers | 11 | A fair obstacle | PASS — browser activity | Touching a hazard ends the round; a different route can avoid it. | Explain the result and make your own choices. |
| Game Makers | 12 | An ending and replay | PASS — browser activity | Winning displays the goal; Reset restores score and all treasures. | Explain the result and make your own choices. |
| Game Makers | 13 | Your own small game | PASS — browser activity | The player can read your goal and play your small layout. | Explain the result and make your own choices. |
| Game Makers | 14 | Test your rules | PASS — browser activity | You observe a missed pickup, a loss, a win and a successful restart. | Explain the result and make your own choices. |
| Game Makers | 15 | Meet Scratch | PASS — Scratch engine | The .sb3 reopens and you can identify the stage, sprite list and Code tab. | Explain the result and make your own choices. |
| Game Makers | 16 | Move a Scratch sprite | PASS — Scratch engine | Green flag restores x=-150, y=0. One right-key press changes x by 10. | Explain the result and make your own choices. |
| Game Makers | 17 | Scratch repetition | PASS — Scratch engine | Holding right moves continuously; releasing it stops movement. | Explain the result and make your own choices. |
| Game Makers | 18 | Scratch treasure | PASS — Scratch engine | Treasure hides once on contact and returns when the green flag is pressed. | Explain the result and make your own choices. |
| Game Makers | 19 | Scratch score | PASS — Scratch engine | One treasure increases score once. Green flag resets score and shows it again. | Explain the result and make your own choices. |
| Game Makers | 20 | Plan the finished game | PASS — Scratch engine | Your plan names the controls, five-pickup goal, one challenge and replay. | Personal design / real family playtest or explanation. |
| Game Makers | 21 | Build the player | PASS — Scratch engine | All four directions work; green flag restores the starting position. | Explain the result and make your own choices. |
| Game Makers | 22 | Build collectibles | PASS — Scratch engine | Five distinct pickups produce score 5; standing still cannot count one twice. | Explain the result and make your own choices. |
| Game Makers | 23 | Build the hazard | PASS — Scratch engine | A hazard broadcasts Lose once. Movement and scoring stop until green flag. | Explain the result and make your own choices. |
| Game Makers | 24 | Win and restart | PASS — Scratch engine | Winning stops movement; green flag restores score, start position and all five treasures after win or loss. | Explain the result and make your own choices. |
| Game Makers | 25 | Explain the controls | PASS — Scratch engine | A new player can find the controls and goal. Human playtest still needed. | Personal design / real family playtest or explanation. |
| Game Makers | 26 | Catch-up day | PASS — Scratch engine | The chosen essential works and a working .sb3 is saved. | Personal design / real family playtest or explanation. |
| Game Makers | 27 | Family playtest | PASS — Scratch engine | Two human observations are recorded and one improvement is chosen. | Personal design / real family playtest or explanation. |
| Game Makers | 28 | Fix and balance | PASS — Scratch engine | The fix works without breaking win, loss or replay. | Personal design / real family playtest or explanation. |
| Game Makers | 29 | Save the source | PASS — Scratch engine | The saved .sb3 loads with the same sprites and functioning rules. | Explain the result and make your own choices. |
| Game Makers | 30 | Game night | PASS — Scratch engine | Your game runs and you can explain and change a rule. Human explanation is still required. | Personal design / real family playtest or explanation. |
| Game Developers | 1 | Your first instructions | PASS — browser activity | Changing the number changes movement distance. | Explain the result and make your own choices. |
| Game Developers | 2 | Variables and values | PASS — browser activity | Speed 6 reaches the same point sooner than speed 3; a GDScript variable names a value. | Explain the result and make your own choices. |
| Game Developers | 3 | Functions are reusable actions | PASS — browser activity | The same sequence works twice; the GDScript function has an indented body. | Explain the result and make your own choices. |
| Game Developers | 4 | If makes a decision | PASS — browser activity | ifwin speaks only after score meets the target. | Explain the result and make your own choices. |
| Game Developers | 5 | Loops repeat work | PASS — browser activity | Repeat produces the same endpoint as three moves; the GDScript loop runs three times. | Explain the result and make your own choices. |
| Game Developers | 6 | Debug a program | PASS — browser activity | The typo produces a line-numbered error; corrected code moves the character. | Explain the result and make your own choices. |
| Game Developers | 7 | Independent browser challenge | PASS — browser activity | Your typed repeat collects three treasures and the condition announces the win. | Explain the result and make your own choices. |
| Game Developers | 8 | Meet Godot | PASS — Godot engine and printed guide | Main.tscn saves and F5 opens the empty main scene without errors. | Explain the result and make your own choices. |
| Game Developers | 9 | Player scene | PASS — Godot engine and printed guide | Your visible Player has a CollisionShape2D and appears as an instance in Main. | Explain the result and make your own choices. |
| Game Developers | 10 | Move and test early | PASS — Godot engine and printed guide | Arrow/WASD actions move the Player in four directions; releasing input stops movement. | Explain the result and make your own choices. |
| Game Developers | 11 | A pickup area | PASS — Godot engine and printed guide | Touching Treasure removes it once through body_entered. | Explain the result and make your own choices. |
| Game Developers | 12 | Score and signals | PASS — Godot engine and printed guide | One pickup increments Main.score once and changes the Score label. | Explain the result and make your own choices. |
| Game Developers | 13 | Reusable scenes | PASS — Godot engine and printed guide | Five separate Treasure instances can each be collected once, producing score 5. | Explain the result and make your own choices. |
| Game Developers | 14 | Checkpoint and backup | PASS — Godot engine and printed guide | The copied source project opens and the pickup route still works. | Explain the result and make your own choices. |
| Game Developers | 15 | A hazard | PASS — Godot engine and printed guide | Touching Hazard changes the round to LOST and displays a losing message. | Explain the result and make your own choices. |
| Game Developers | 16 | Game states | PASS — Godot engine and printed guide | Won and lost states stop movement and scoring until replay. | Explain the result and make your own choices. |
| Game Developers | 17 | Timer and victory | PASS — Godot engine and printed guide | The real Timer causes a loss on timeout and stops when the player wins. | Explain the result and make your own choices. |
| Game Developers | 18 | Restart and handheld test | PASS — Godot engine and printed guide | Replay restores score, treasures, player position and timer. An adult must test the APK on Retroid. | Actual controller / Retroid install and play; adult assistance. |
| Game Developers | 19 | Art and sound | PASS — Godot engine and printed guide | Pickup sound is optional; with Mute on, score and messages still work. | Explain the result and make your own choices. |
| Game Developers | 20 | Design your own collector | PASS — Godot engine and printed guide | Your written plan names a player, action, goal, challenge and replay. | Own design / human playtest, explanation and rebuild. |
| Game Developers | 21 | Build the core | PASS — Godot engine and printed guide | The core movement-and-pickup loop works before decoration is added. | Explain the result and make your own choices. |
| Game Developers | 22 | Build the level | PASS — Godot engine and printed guide | All five pickups are reachable within the level bounds and count once. | Explain the result and make your own choices. |
| Game Developers | 23 | Add a fair challenge | PASS — Godot engine and printed guide | A player can avoid the hazard, and contact produces a clear loss. Fairness needs a human playtest. | Explain the result and make your own choices. |
| Game Developers | 24 | Finish the round | PASS — Godot engine and printed guide | Win and loss both work; a second round works after either ending. | Explain the result and make your own choices. |
| Game Developers | 25 | Controller-friendly UI | PASS — Godot engine and printed guide | Replay and Mute accept focus and UI input. A physical controller check is still required. | Actual controller / Retroid install and play; adult assistance. |
| Game Developers | 26 | Catch-up and scope cut | PASS — Godot engine and printed guide | One essential issue is fixed and a known-good source copy is saved. | Own design / human playtest, explanation and rebuild. |
| Game Developers | 27 | Playtest on real hardware | PASS — Godot engine and printed guide | A parent and child record results on a real computer and Retroid; this is a hardware activity. | Actual controller / Retroid install and play; adult assistance. |
| Game Developers | 28 | Fix the biggest bugs | PASS — Godot engine and printed guide | The chosen fix is followed by successful win, loss and replay tests. | Own design / human playtest, explanation and rebuild. |
| Game Developers | 29 | Release checklist | PASS — Godot engine and printed guide | The source is backed up and a test APK exports. Installing and playing it on Retroid is a device check. | Actual controller / Retroid install and play; adult assistance. |
| Game Developers | 30 | Developer showcase | PASS — Godot engine and printed guide | You demonstrate and explain a function, signal and state, change one rule, and rebuild. | Own design / human playtest, explanation and rebuild. |

## Before children use the hosted edition

1. On a real Fire 7 and HD 8 inside Amazon Kids: approve the site, then check Run, sound, keyboard, orientation, saving, return visits and downloads.
2. On the family computer: install Godot, open the supplied reference and test the actual keyboard/controller. For Scratch, verify editor loading, the block workspace and File → Load/Save on that browser.
3. With a parent, install a test APK on Retroid and check controls, text, sound, restart, suspend/resume and performance. The signed CI APK is an educational reference, not proof of physical compatibility.
4. Johnny5 should check the deployed HTTPS page, Caddy/Cloudflare headers and online saves. The automated suite uses disposable localhost services and never contacts the learning domain.
