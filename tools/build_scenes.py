#!/usr/bin/env python3
"""Author the checked-in, editable Godot scenes and shared theme. Not run by the game."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]

def color(h):
 h=h.lstrip('#'); return 'Color('+', '.join(str(round(int(h[i:i+2],16)/255,4)) for i in (0,2,4))+', 1)'
def style(id,bg,r=20,border=None,shadow=None):
 s=f'[sub_resource type="StyleBoxFlat" id="{id}"]\nbg_color = {color(bg)}\n'
 for edge in ('top_left','top_right','bottom_left','bottom_right'):s+=f'corner_radius_{edge} = {r}\n'
 if border:
  for edge in ('left','top','right','bottom'):s+=f'border_width_{edge} = 2\n'
  s+=f'border_color = {color(border)}\n'
 if shadow:s+=f'shadow_color = {color(shadow)}\nshadow_size = 2\nshadow_offset = Vector2(0, 5)\n'
 s+='content_margin_left = 12.0\ncontent_margin_right = 12.0\ncontent_margin_top = 9.0\ncontent_margin_bottom = 9.0\n'
 return s+'\n'
class Scene:
 def __init__(self):self.ext=[];self.sub=[];self.nodes=[];self.cons=[]
 def resource(self,type,path):
  i=str(len(self.ext)+1);self.ext.append(f'[ext_resource type="{type}" path="res://{path}" id="{i}"]');return f'ExtResource("{i}")'
 def node(self,name,type='Control',parent=None,props='',instance=None):
  head=f'[node name="{name}"'
  if type:head+=f' type="{type}"'
  if parent is not None:head+=f' parent="{parent}"'
  if instance:head+=f' instance={instance}'
  self.nodes.append(head+']\n'+props+'\n')
 def connect(self,sig,src,to,method):self.cons.append(f'[connection signal="{sig}" from="{src}" to="{to}" method="{method}"]')
 def save(self,path):
  (R/path).write_text(f'[gd_scene load_steps={len(self.ext)+len(self.sub)+1} format=3]\n\n'+'\n'.join(self.ext)+'\n\n'+''.join(self.sub)+'\n'.join(self.nodes)+'\n'+'\n'.join(self.cons)+'\n')
FULL='layout_mode = 1\nanchors_preset = 15\nanchor_right = 1.0\nanchor_bottom = 1.0\ngrow_horizontal = 2\ngrow_vertical = 2\n'
def rect(x,y,w,h):return f'offset_left = {x}.0\noffset_top = {y}.0\noffset_right = {x+w}.0\noffset_bottom = {y+h}.0\n'
def label(s,name,parent,text,size=20,props='',col='45345F',head=False):
 p=f'text = "{text}"\ntheme_override_font_sizes/font_size = {size}\ntheme_override_colors/font_color = {color(col)}\nmouse_filter = 2\n'
 if head:p+=f'theme_override_fonts/font = {s.heading}\n'
 s.node(name,'Label',parent,p+props)
def btn(s,name,parent,text,props='',variant='normal',icon=None):
 p=f'text = "{text}"\nscript = {s.juice}\nmouse_default_cursor_shape = 2\n'
 if variant!='normal':p+=f'theme_type_variation = &"{variant}"\n'
 if icon and variant == 'PurpleButton':icon += '_light'
 if icon:p+=f'icon = {s.resource("Texture2D","assets/icons/"+icon+".svg")}\nexpand_icon = true\ntheme_override_constants/icon_max_width = 25\n'
 s.node(name,'Button',parent,p+props)
def base(s):
 s.heading=s.resource('FontVariation','assets/fonts/Heading.tres');s.juice=s.resource('Script','scripts/ui/juicy_button.gd');return s.resource('Theme','resources/game_theme.tres')

# One shared theme; type variations stay editable in the Inspector.
theme='[gd_resource type="Theme" load_steps=15 format=3]\n\n[ext_resource type="FontVariation" path="res://assets/fonts/Body.tres" id="1"]\n\n'
for spec in [('normal','FFFFFF',18,'EAE1FA','DDD1EF'),('hover','F8F3FF',18,'D9C6F7','DDD1EF'),('pressed','EBE0FB',18,None,None),('pink','F04FAB',22,None,'C53588'),('pink_hover','FC69BB',22,None,'C53588'),('pink_down','D84194',22,None,None),('purple','7950D5',20,None,'5C37AD'),('purple_hover','9168E8',20,None,'5C37AD'),('purple_down','653ABF',20,None,None),('panel','FFFFFF',24,None,'E1D7F1'),('progress_bg','E6DEF4',6,None,None),('progress_fill','ED58B2',6,None,None),('empty','F3EDFD',20,None,None)]:theme+=style(*spec)
theme+='[resource]\ndefault_font = ExtResource("1")\ndefault_font_size = 18\n'
for kind,styles,fg in [('Button',['normal','hover','pressed'],'665081'),('PrimaryButton',['pink','pink_hover','pink_down'],'FFFFFF'),('PurpleButton',['purple','purple_hover','purple_down'],'FFFFFF'),('TabButton',['empty','hover','pressed'],'755996')]:
 if kind!='Button':theme+=f'{kind}/base_type = &"Button"\n'
 for state,st in zip(['normal','hover','pressed'],styles):theme+=f'{kind}/styles/{state} = SubResource("{st}")\n'
 for state in ['font_color','font_hover_color','font_pressed_color']:theme+=f'{kind}/colors/{state} = {color(fg)}\n'
 theme+=f'{kind}/font_sizes/font_size = 18\n'
theme+='PanelContainer/styles/panel = SubResource("panel")\nPanel/styles/panel = SubResource("panel")\nProgressBar/styles/background = SubResource("progress_bg")\nProgressBar/styles/fill = SubResource("progress_fill")\nLabel/colors/font_color = '+color('493861')+'\n'
(R/'resources/game_theme.tres').write_text(theme)

s=Scene();script=s.resource('Script','scripts/game/region.gd');font=s.resource('FontVariation','assets/fonts/Body.tres');shader=s.resource('Shader','scripts/game/paint.gdshader');s.sub.append('[sub_resource type="ShaderMaterial" id="paint"]\nshader = '+shader+'\n\n')
s.node('ColorRegion','Node2D',props='script = '+script);s.node('Polygon','Polygon2D','.', 'material = SubResource("paint")\nantialiased = true');s.node('Outline','Line2D','.', 'width = 1.8\nclosed = true\nantialiased = true\njoint_mode = 2');s.node('Number','Label','.',f'offset_right = 36.0\noffset_bottom = 32.0\ntext = "1"\nhorizontal_alignment = 1\nvertical_alignment = 1\nmouse_filter = 2\ntheme_override_fonts/font = {font}\ntheme_override_font_sizes/font_size = 17');s.save('scenes/game/region.tscn')
s=Scene();star=s.resource('Texture2D','assets/icons/spark.svg');s.node('FillBurst','CPUParticles2D',props=f'emitting = false\namount = 12\nlifetime = 0.7\none_shot = true\nexplosiveness = 1.0\ntexture = {star}\nemission_shape = 1\nemission_sphere_radius = 4.0\ndirection = Vector2(0, -1)\nspread = 180.0\ngravity = Vector2(0, 110)\ninitial_velocity_min = 38.0\ninitial_velocity_max = 115.0\nscale_amount_min = 0.05\nscale_amount_max = 0.14\nangular_velocity_min = -180.0\nangular_velocity_max = 180.0');s.save('scenes/game/fill_burst.tscn')
s=Scene();scr=s.resource('Script','scripts/game/board.gd');stars=s.resource('Script','scripts/ui/starfield.gd');ring=s.resource('Script','scripts/ui/hint_ring.gd');s.node('ColoringBoard',props=FULL+'clip_contents = true\nscript = '+scr);s.node('Backdrop',parent='.',props=FULL+'script = '+stars+'\ndark = true\nmouse_filter = 2');s.node('Artwork','Node2D','.');s.node('HintRing',parent='.',props='visible = false\noffset_right = 70.0\noffset_bottom = 70.0\nmouse_filter = 2\nscript = '+ring);s.node('RoundedFrame',parent='.',props=FULL+'mouse_filter = 2\nscript = '+s.resource('Script','scripts/ui/rounded_frame.gd'));s.save('scenes/game/board.tscn')

# Artwork tile scene is instantiated by the gallery for catalog data.
s=Scene();th=base(s);scr=s.resource('Script','scripts/ui/art_card.gd');stars=s.resource('Script','scripts/ui/starfield.gd')
s.node('ArtCard','Button',props='custom_minimum_size = Vector2(232, 272)\nsize_flags_horizontal = 3\nclip_contents = true\ntheme = '+th+'\nscript = '+scr+'\nmouse_default_cursor_shape = 2\n')
s.node('PreviewPanel','Panel','.',rect(6,6,220,205)+'clip_contents = true\nmouse_filter = 2\n');s.node('PreviewBG',parent='PreviewPanel',props=FULL+'script = '+stars+'\ndark = true');s.node('Preview','TextureRect','PreviewPanel',FULL+'offset_left = 5.0\noffset_top = 3.0\noffset_right = -5.0\noffset_bottom = -3.0\nexpand_mode = 1\nstretch_mode = 5\nmouse_filter = 2\n');label(s,'Title','.', 'Cosmic Peony',20,rect(16,216,206,25),head=True);label(s,'Detail','.', 'Medium · 7 min',13,rect(16,243,206,20),col='7D648F');label(s,'Badge','PreviewPanel','NEW',11,rect(10,9,100,20),col='FFEBB0');s.node('RoundedFrame',parent='PreviewPanel',props=FULL+'mouse_filter = 2\nradius = 15.0\nframe_color = Color(1, 1, 1, 1)\nscript = '+s.resource('Script','scripts/ui/rounded_frame.gd'));s.save('scenes/ui/art_card.tscn')

# Palette chip scene.
s=Scene();th=base(s);scr=s.resource('Script','scripts/ui/color_chip.gd');s.node('ColorChip','Button',props='custom_minimum_size = Vector2(60, 68)\nsize_flags_vertical = 4\ntheme = '+th+'\nscript = '+scr+'\nmouse_default_cursor_shape = 2\n');s.save('scenes/ui/color_chip.tscn')

# Gallery, with real editable Control nodes for every major layout.
s=Scene();th=base(s);scr=s.resource('Script','scripts/ui/gallery.gd');stars=s.resource('Script','scripts/ui/starfield.gd');pip=s.resource('Texture2D','assets/icons/pip.svg');hero=s.resource('Texture2D','assets/art/featured_bloom.png')
s.node('Gallery',props=FULL+'theme = '+th+'\nscript = '+scr);s.node('Backdrop',parent='.',props=FULL+'script = '+stars)
s.node('Header','HBoxContainer','.', 'layout_mode = 1\nanchor_right = 1.0\noffset_left = 22.0\noffset_top = 20.0\noffset_right = -22.0\noffset_bottom = 86.0\ntheme_override_constants/separation = 10');s.node('Pip','TextureRect','Header',f'custom_minimum_size = Vector2(50, 60)\ntexture = {pip}\nexpand_mode = 1\nstretch_mode = 5');s.node('Brand','VBoxContainer','Header','size_flags_horizontal = 3\ntheme_override_constants/separation = -4');label(s,'Name','Header/Brand','prism bloom',29,head=True);label(s,'Tagline','Header/Brand','COLOR YOUR HAPPY',11,col='7D648F');btn(s,'Stars','Header','0', 'custom_minimum_size = Vector2(73, 45)\nsize_flags_vertical = 4',icon='star');btn(s,'Settings','Header','', 'custom_minimum_size = Vector2(46, 45)\nsize_flags_vertical = 4',icon='settings')
s.node('Scroll','ScrollContainer','.', 'layout_mode = 1\nanchor_right = 1.0\nanchor_bottom = 1.0\noffset_left = 22.0\noffset_top = 105.0\noffset_right = -22.0\noffset_bottom = -94.0\nhorizontal_scroll_mode = 0');s.node('Content','VBoxContainer','Scroll','size_flags_horizontal = 3\ntheme_override_constants/separation = 17')
label(s,'Greeting','Scroll/Content','A little color. A little joy.',27,head=True)
s.node('Feature','Panel','Scroll/Content','custom_minimum_size = Vector2(0, 246)\nclip_contents = true');s.node('Image','TextureRect','Scroll/Content/Feature',FULL+f'texture = {hero}\nexpand_mode = 1\nstretch_mode = 6\nmouse_filter = 2');label(s,'Eyebrow','Scroll/Content/Feature','A MOMENT OF MAGIC',11,rect(20,22,250,20),col='D6BDF8');label(s,'Title','Scroll/Content/Feature','Let your\ncolors bloom.',31,rect(20,55,225,90),col='FFFFFF',head=True);label(s,'Subtitle','Scroll/Content/Feature','One number at a time.',13,rect(20,143,200,25),col='E2CFF8');btn(s,'Play','Scroll/Content/Feature','Let’s color',rect(20,183,156,42),'PrimaryButton')
s.node('CategoryScroll','ScrollContainer','Scroll/Content','custom_minimum_size = Vector2(0, 47)\nvertical_scroll_mode = 0\nhorizontal_scroll_mode = 3');s.node('Categories','HBoxContainer','Scroll/Content/CategoryScroll','theme_override_constants/separation = 8')
for name in ['All','Florals','Animals','Mandalas','Places']:btn(s,name,'Scroll/Content/CategoryScroll/Categories',name,'custom_minimum_size = Vector2(64, 38)\nsize_flags_vertical = 4\ntheme_override_font_sizes/font_size = 15','TabButton')
s.node('Section','HBoxContainer','Scroll/Content');label(s,'Title','Scroll/Content/Section','Find your next favorite',23,'size_flags_horizontal = 3',head=True);label(s,'Count','Scroll/Content/Section','12 FREE',11,'vertical_alignment = 1',col='8C5FA4')
s.node('Grid','GridContainer','Scroll/Content','columns = 2\nsize_flags_horizontal = 3\ntheme_override_constants/h_separation = 14\ntheme_override_constants/v_separation = 17')
label(s,'Empty','Scroll/Content','Your story starts with one color.\nChoose an artwork from the Library.',18,'visible = false\ncustom_minimum_size = Vector2(0, 130)\nhorizontal_alignment = 1\nvertical_alignment = 1',col='917DA8')
label(s,'Footer','Scroll/Content','Made for unhurried moments. Made for you.',13,'custom_minimum_size = Vector2(0, 44)\nhorizontal_alignment = 1',col='866C99')
s.node('Navigation','Panel','.', 'layout_mode = 1\nanchor_top = 1.0\nanchor_right = 1.0\nanchor_bottom = 1.0\noffset_left = 16.0\noffset_top = -83.0\noffset_right = -16.0\noffset_bottom = -12.0');s.node('Tabs','HBoxContainer','Navigation',FULL+'offset_left = 10.0\noffset_top = 8.0\noffset_right = -10.0\noffset_bottom = -9.0\ntheme_override_constants/separation = 6')
for name,title,icon in [('Library','Library','gallery'),('Daily','Daily','calendar'),('MyArt','My art','star')]:btn(s,name,'Navigation/Tabs',title,'size_flags_horizontal = 3\ntheme_override_font_sizes/font_size = 15','TabButton',icon)
s.connect('pressed','Header/Settings','.','_on_settings');s.connect('pressed','Scroll/Content/Feature/Play','.','_on_feature');s.node('RoundedFrame',parent='Scroll/Content/Feature',props=FULL+'mouse_filter = 2\nscript = '+s.resource('Script','scripts/ui/rounded_frame.gd'));s.save('scenes/ui/gallery.tscn')

s=Scene();th=base(s);scr=s.resource('Script','scripts/game/game.gd');board=s.resource('PackedScene','scenes/game/board.tscn')
s.node('Game',props=FULL+'theme = '+th+'\nscript = '+scr)
s.node('Header','HBoxContainer','.', 'layout_mode = 1\nanchor_right = 1.0\noffset_left = 18.0\noffset_top = 22.0\noffset_right = -18.0\noffset_bottom = 79.0\ntheme_override_constants/separation = 14');btn(s,'Back','Header','','custom_minimum_size = Vector2(48, 48)\nsize_flags_vertical = 4',icon='back');s.node('Names','VBoxContainer','Header','size_flags_horizontal = 3\ntheme_override_constants/separation = -1');label(s,'Title','Header/Names','Cosmic Peony',25,head=True);label(s,'Subtitle','Header/Names','Florals · Medium',13,col='7E6694');btn(s,'Settings','Header','','custom_minimum_size = Vector2(48, 48)\nsize_flags_vertical = 4',icon='settings')
s.node('Progress','ProgressBar','.', 'layout_mode = 1\nanchor_right = 1.0\noffset_left = 24.0\noffset_top = 105.0\noffset_right = -78.0\noffset_bottom = 115.0\nshow_percentage = false');label(s,'Percent','.','0%',15,'layout_mode = 1\nanchor_left = 1.0\nanchor_right = 1.0\noffset_left = -66.0\noffset_top = 96.0\noffset_right = -18.0\noffset_bottom = 123.0',col='A64AB6');label(s,'Instruction','.','Pick a color. Tap its matching numbers.',14,'layout_mode = 1\nanchor_right = 1.0\noffset_left = 20.0\noffset_top = 137.0\noffset_right = -20.0\noffset_bottom = 160.0\nhorizontal_alignment = 1',col='78608E')
s.node('Board',None,'.',FULL+'offset_left = 14.0\noffset_top = 176.0\noffset_right = -14.0\noffset_bottom = -229.0',instance=board)
s.node('Controls','HBoxContainer','.', 'layout_mode = 1\nanchor_top = 1.0\nanchor_right = 1.0\nanchor_bottom = 1.0\noffset_left = 22.0\noffset_top = -210.0\noffset_right = -22.0\noffset_bottom = -162.0\ntheme_override_constants/separation = 10');btn(s,'Hint','Controls','Find a spot','size_flags_horizontal = 3','PurpleButton','hint');btn(s,'Fit','Controls','Fit','custom_minimum_size = Vector2(85, 48)',icon='reset');btn(s,'Zoom','Controls','','custom_minimum_size = Vector2(53, 48)',icon='zoom')
s.node('PalettePanel','Panel','.', 'layout_mode = 1\nanchor_top = 1.0\nanchor_right = 1.0\nanchor_bottom = 1.0\noffset_left = 14.0\noffset_top = -143.0\noffset_right = -14.0\noffset_bottom = -13.0');label(s,'Caption','PalettePanel','YOUR COLORS',11,rect(18,11,160,20),col='7B6094');label(s,'Remaining','PalettePanel','45 little moments to go',11,'layout_mode = 1\nanchor_left = 1.0\nanchor_right = 1.0\noffset_left = -243.0\noffset_top = 11.0\noffset_right = -18.0\noffset_bottom = 31.0\nhorizontal_alignment = 2',col='7B6094');s.node('Scroll','ScrollContainer','PalettePanel',FULL+'offset_left = 13.0\noffset_top = 40.0\noffset_right = -13.0\noffset_bottom = -10.0\nvertical_scroll_mode = 0\nhorizontal_scroll_mode = 3');s.node('Colors','HBoxContainer','PalettePanel/Scroll','theme_override_constants/separation = 7')
s.connect('pressed','Header/Back','.','_on_back');s.connect('pressed','Header/Settings','.','_on_settings');s.connect('pressed','Controls/Hint','.','_on_hint');s.connect('pressed','Controls/Fit','Board','reset_view');s.connect('pressed','Controls/Zoom','.','_on_zoom');s.connect('region_filled','Board','.','_on_filled');s.connect('wrong_color','Board','.','_on_wrong');s.save('scenes/game/game.tscn')

s=Scene();th=base(s);scr=s.resource('Script','scripts/ui/reward.gd');stars=s.resource('Script','scripts/ui/starfield.gd');pip=s.resource('Texture2D','assets/icons/pip.svg');conf=s.resource('PackedScene','scenes/game/fill_burst.tscn')
s.node('Reward',props=FULL+'theme = '+th+'\nscript = '+scr);s.node('Background',parent='.',props=FULL+'script = '+stars);label(s,'Eyebrow','.','A LITTLE PATIENCE. A LOT OF MAGIC.',11,'layout_mode = 1\nanchor_right = 1.0\noffset_top = 41.0\noffset_bottom = 62.0\nhorizontal_alignment = 1',col='AC76BA');label(s,'Headline','.','Look what you\nbrought to life!',36,'layout_mode = 1\nanchor_right = 1.0\noffset_top = 76.0\noffset_bottom = 168.0\nhorizontal_alignment = 1',head=True)
s.node('ArtPanel','Panel','.', 'clip_contents = true\nlayout_mode = 1\nanchor_right = 1.0\nanchor_bottom = 1.0\noffset_left = 43.0\noffset_top = 199.0\noffset_right = -43.0\noffset_bottom = -306.0');s.node('Backdrop',parent='ArtPanel',props=FULL+'script = '+stars+'\ndark = true');s.node('Preview','Control','ArtPanel',FULL+'offset_left = 8.0\noffset_top = 8.0\noffset_right = -8.0\noffset_bottom = -8.0\nmouse_filter = 2\nscript = '+s.resource('Script','scripts/ui/reveal.gd'));s.node('Artwork','Node2D','ArtPanel/Preview')
s.node('Pip','TextureRect','.',f'layout_mode = 1\nanchor_left = 1.0\nanchor_right = 1.0\nanchor_top = 1.0\nanchor_bottom = 1.0\noffset_left = -136.0\noffset_top = -345.0\noffset_right = -37.0\noffset_bottom = -226.0\ntexture = {pip}\nexpand_mode = 1\nstretch_mode = 5')
label(s,'Title','.','Cosmic Peony',26,'layout_mode = 1\nanchor_top = 1.0\nanchor_right = 1.0\nanchor_bottom = 1.0\noffset_top = -282.0\noffset_bottom = -247.0\nhorizontal_alignment = 1',head=True);label(s,'Details','.','Every little piece, beautifully you.',15,'layout_mode = 1\nanchor_top = 1.0\nanchor_right = 1.0\nanchor_bottom = 1.0\noffset_top = -236.0\noffset_bottom = -204.0\nhorizontal_alignment = 1',col='9176A5');label(s,'RewardText','.','+1 masterpiece · Collection growing!',16,'layout_mode = 1\nanchor_top = 1.0\nanchor_right = 1.0\nanchor_bottom = 1.0\noffset_top = -189.0\noffset_bottom = -157.0\nhorizontal_alignment = 1',col='BE60A9')
btn(s,'Continue','.','Keep the colors coming','layout_mode = 1\nanchor_top = 1.0\nanchor_right = 1.0\nanchor_bottom = 1.0\noffset_left = 45.0\noffset_top = -130.0\noffset_right = -45.0\noffset_bottom = -75.0','PrimaryButton');btn(s,'Admire','.','Admire my artwork','layout_mode = 1\nanchor_top = 1.0\nanchor_right = 1.0\nanchor_bottom = 1.0\noffset_left = 90.0\noffset_top = -59.0\noffset_right = -90.0\noffset_bottom = -15.0\nflat = true')
s.node('Confetti',None,'.','position = Vector2(270, 330)\namount = 65\ncolor = Color(1, 0.76, 0.33, 1)\nlifetime = 2.8\ninitial_velocity_min = 80.0\ninitial_velocity_max = 320.0\nscale_amount_min = 0.08\nscale_amount_max = 0.22',instance=conf);s.connect('pressed','Continue','.','_on_continue');s.connect('pressed','Admire','.','_on_admire');s.node('RoundedFrame',parent='ArtPanel',props=FULL+'mouse_filter = 2\nscript = '+s.resource('Script','scripts/ui/rounded_frame.gd'));s.save('scenes/ui/reward.tscn')

s=Scene();th=base(s);scr=s.resource('Script','scripts/ui/settings.gd');s.node('Settings',props=FULL+'theme = '+th+'\nscript = '+scr+'\nmouse_filter = 0');s.node('Shade','ColorRect','.',FULL+'color = Color(0.10, 0.04, 0.22, 0.7)');s.node('Center','CenterContainer','.',FULL);s.node('Panel','PanelContainer','Center','custom_minimum_size = Vector2(414, 400)');s.node('Content','VBoxContainer','Center/Panel','theme_override_constants/separation = 18');label(s,'Title','Center/Panel/Content','Your happy place',29,'horizontal_alignment = 1',head=True);label(s,'Subtitle','Center/Panel/Content','Settle in. Make it yours.',16,'horizontal_alignment = 1',col='9982B0');s.node('Sound','CheckButton','Center/Panel/Content','custom_minimum_size = Vector2(0, 52)\ntext = "Sound effects"');s.node('Haptics','CheckButton','Center/Panel/Content','custom_minimum_size = Vector2(0, 52)\ntext = "Gentle haptics"');label(s,'Note','Center/Panel/Content','Your progress saves with every color.\nNo timers. No pressure. Just you and color.',13,'horizontal_alignment = 1',col='9277A6');btn(s,'Close','Center/Panel/Content','Back to the magic','custom_minimum_size = Vector2(0, 48)','PurpleButton');s.connect('pressed','Center/Panel/Content/Close','.','_on_close');s.connect('toggled','Center/Panel/Content/Sound','.','_on_sound');s.connect('toggled','Center/Panel/Content/Haptics','.','_on_haptics');s.save('scenes/ui/settings.tscn')

s=Scene();th=base(s);scr=s.resource('Script','scripts/main.gd');s.node('PrismBloom',props=FULL+'theme = '+th+'\nscript = '+scr)
s.node('Background','ColorRect','.',FULL+'color = '+color('F5F0FF')+'\nmouse_filter = 2')
for name,path in [('Gallery','scenes/ui/gallery.tscn'),('Game','scenes/game/game.tscn'),('Reward','scenes/ui/reward.tscn'),('Settings','scenes/ui/settings.tscn')]:s.node(name,None,'.',FULL+('visible = false' if name!='Gallery' else ''),instance=s.resource('PackedScene',path))
s.node('Toast','PanelContainer','.', 'visible = false\nlayout_mode = 1\nanchor_left = 0.5\nanchor_top = 0.5\nanchor_right = 0.5\nanchor_bottom = 0.5\noffset_left = -230.0\noffset_top = -35.0\noffset_right = 230.0\noffset_bottom = 35.0\nmouse_filter = 2');label(s,'Text','Toast','Saved',17,'horizontal_alignment = 1\nautowrap_mode = 2')
s.connect('art_selected','Gallery','.','_open_art');s.connect('settings_requested','Gallery','.','_settings');s.connect('message','Gallery','.','_toast');s.connect('back_requested','Game','.','_gallery');s.connect('settings_requested','Game','.','_settings');s.connect('completed','Game','.','_complete');s.connect('continue_requested','Reward','.','_gallery');s.connect('admire_requested','Reward','.','_admire');s.save('scenes/main.tscn')
for file in (R/'scenes').rglob('*.tscn'):
 file.write_text(file.read_text().rstrip()+'\n')
print('Authored theme and 10 editable scenes.')
