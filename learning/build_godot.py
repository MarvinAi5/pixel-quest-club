from pathlib import Path
import struct,math,zipfile
ROOT=Path(__file__).resolve().parents[1];G=ROOT/'godot-reference'
def shape_scene(name,kind,color,radius,script):
 return f'''[gd_scene load_steps=3 format=3]
[ext_resource type="Script" path="res://{script}" id="1"]
[sub_resource type="CircleShape2D" id="Shape"]
radius = {radius}.0
[node name="{name}" type="{kind}"]
script = ExtResource("1")
[node name="Art" type="Polygon2D" parent="."]
polygon = PackedVector2Array(-{radius}, -{radius}, {radius}, -{radius}, {radius}, {radius}, -{radius}, {radius})
color = Color({color})
[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("Shape")
'''
def build():
 for name,kind,color,radius in [('Player','CharacterBody2D','0, 0.5, 0.52, 1',18),('Treasure','Area2D','1, 0.75, 0.25, 1',12),('Hazard','Area2D','0.74, 0.34, 0.11, 1',24)]:
  (G/f'{name}.tscn').write_text(shape_scene(name,kind,color,radius,f'{name}.gd'))
 data=bytearray()
 for i in range(3308):data.extend(struct.pack('<h',int(6000*math.sin(2*math.pi*660*i/22050)*(1-i/3308))))
 wav='[gd_resource type="AudioStreamWAV" format=3]\n[resource]\nformat = 1\nmix_rate = 22050\ndata = PackedByteArray('+', '.join(map(str,data))+')\n'
 (G/'PickupSound.tres').write_text(wav)
 main='''[gd_scene load_steps=6 format=3]
[ext_resource type="Script" path="res://Main.gd" id="1"]
[ext_resource type="PackedScene" path="res://Player.tscn" id="2"]
[ext_resource type="PackedScene" path="res://Treasure.tscn" id="3"]
[ext_resource type="PackedScene" path="res://Hazard.tscn" id="4"]
[ext_resource type="AudioStream" path="res://PickupSound.tres" id="5"]
[node name="Main" type="Node2D"]
script = ExtResource("1")
[node name="Player" parent="." instance=ExtResource("2")]
position = Vector2(90, 225)
'''
 for i,(x,y) in enumerate([(210,100),(350,320),(470,120),(600,340),(710,180)],1):main+=f'[node name="Treasure{i}" parent="." instance=ExtResource("3")]\nposition = Vector2({x}, {y})\n'
 main+='''[node name="Hazard" parent="." instance=ExtResource("4")]
position = Vector2(410,225)
[node name="RoundTimer" type="Timer" parent="."]
one_shot = true
[node name="PickupSound" type="AudioStreamPlayer" parent="."]
stream = ExtResource("5")
[node name="CanvasLayer" type="CanvasLayer" parent="."]
[node name="Score" type="Label" parent="CanvasLayer"]
offset_left = 24.0
offset_top = 12.0
theme_override_colors/font_color = Color(0.1,0.13,0.23,1)
theme_override_font_sizes/font_size = 24
[node name="Message" type="Label" parent="CanvasLayer"]
offset_left = 24.0
offset_top = 44.0
theme_override_colors/font_color = Color(0.1,0.13,0.23,1)
theme_override_font_sizes/font_size = 18
[node name="Restart" type="Button" parent="CanvasLayer"]
offset_left = 24.0
offset_top = 400.0
offset_right = 144.0
offset_bottom = 442.0
text = "Replay"
[node name="Mute" type="CheckButton" parent="CanvasLayer"]
theme_override_colors/font_color = Color(0.1,0.13,0.23,1)
theme_override_colors/font_hover_color = Color(0.1,0.13,0.23,1)
theme_override_colors/font_pressed_color = Color(0.1,0.13,0.23,1)
theme_override_colors/font_hover_pressed_color = Color(0.1,0.13,0.23,1)
theme_override_colors/font_focus_color = Color(0.1,0.13,0.23,1)
offset_left = 170.0
offset_top = 400.0
offset_right = 290.0
offset_bottom = 442.0
text = "Mute"
'''
 (G/'Main.tscn').write_text(main)
 (G/'README.txt').write_text('''Godot 4 scene-based reference for October Game Developers.
Open project.godot using Godot 4 Standard, Compatibility. F5 runs Main.
Player is CharacterBody2D, pickups and Hazard are Area2D scenes. Main owns score/state.
Select Main and change Course Day (8–30) in Inspector to compare the rules introduced on each day. This reference demonstrates the technical patterns; design your own layout and art. Follow the website for today's lesson.
Arrows/WASD or left stick move. R/controller A/Replay restarts. Mute toggles pickup sound.
Automated engine tests cover movement, physics signals, score, endings, timer, replay, focus and muted feedback. Physical controller, Android export and real Retroid play still need an adult's device check.
''')
 with zipfile.ZipFile(ROOT/'public/starter-godot.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(G.iterdir()):
   if p.is_file() and p.suffix in ('.gd','.tscn','.godot','.txt','.tres'):z.writestr(p.name,p.read_bytes())
if __name__=='__main__':build()
