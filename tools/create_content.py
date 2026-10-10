#!/usr/bin/env python3
"""Reproducible original vector illustrations and UI assets for Prism Bloom."""
import math, random, wave, struct
from pathlib import Path
from import_svg import compile_svg
ROOT=Path(__file__).resolve().parents[1]
PINK=['#F75BA6','#FF9AC9','#9957DE','#BBA2FF','#36D4D9','#117FAD','#FFD36C','#FF955F']
DAWN=['#FF878E','#FFC0BB','#F45590','#B97CDD','#68DCCD','#259CAF','#FFE499','#F5AD61']
NIGHT=['#906AFF','#CEAEFF','#F068B5','#FCACDF','#63DAD8','#367BBC','#FFCF70','#FF9180']

def pt(r,a,c=(300,300)): return (c[0]+r*math.cos(a),c[1]+r*math.sin(a))
def xy(p):return f'{p[0]:.2f},{p[1]:.2f}'
class Art:
 def __init__(self,palette):self.palette=palette;self.shapes=[]
 def path(self,d,c):self.shapes.append(f'<path id="region_{len(self.shapes):03}" fill="{self.palette[c%8]}" d="{d}"/>')
 def poly(self,points,c): self.shapes.append(f'<polygon id="region_{len(self.shapes):03}" fill="{self.palette[c%8]}" points="'+ ' '.join(xy(p) for p in points)+'"/>')
 def ellipse(self,x,y,rx,ry,c): self.shapes.append(f'<ellipse id="region_{len(self.shapes):03}" fill="{self.palette[c%8]}" cx="{x}" cy="{y}" rx="{rx}" ry="{ry}"/>')
 def gem(self,x,y,r,c):self.poly([(x,y-r),(x+r*.62,y),(x,y+r),(x-r*.62,y)],c)
 def leaf(self,start,end,width,c):
  x,y=start;ex,ey=end;dx,dy=ex-x,ey-y;l=math.hypot(dx,dy);nx,ny=-dy/l*width,dx/l*width
  self.path(f'M {xy(start)} Q {x+dx*.3+nx},{y+dy*.3+ny} {xy(end)} Q {x+dx*.55-nx},{y+dy*.55-ny} {xy(start)} Z',c)
 def save(self,name):
  p=ROOT/'content/svg'/f'{name}.svg'
  p.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" stroke="#30234E" stroke-width="2.2" stroke-linejoin="round">'+''.join(self.shapes)+'</svg>')
  return compile_svg(p,ROOT/'resources/levels'/f'{name}.json')

def flower(a,variant=0):
 center=(300,288)
 for i in range(8):
  angle=i*math.tau/8+.15
  a.leaf(pt(145,angle,center),pt(270,angle,center),48,4+i%2)
 for layer,(inner,outer,n) in enumerate([(95,224,12),(45,150,9),(16,84,7)]):
  for i in range(n):
   t=i*math.tau/n+layer*.21+variant*.05; half=math.pi/n
   p0=pt(inner,t-half,center);p1=pt(outer,t-half*.72,center);p2=pt(outer*1.08,t+half*.66,center);p3=pt(inner,t+half,center)
   a.path(f'M {xy(p0)} C {xy(pt(outer*.90,t-half*1.15,center))} {xy(pt(outer*1.08,t-half*.72,center))} {xy(pt(outer,t,center))} C {xy(pt(outer*1.08,t+half*.72,center))} {xy(pt(outer*.9,t+half*1.15,center))} {xy(p3)} Q {xy(pt(inner*.74,t,center))} {xy(p0)} Z',(i+layer+variant)%4)
 a.ellipse(300,288,28,28,6)
 a.ellipse(300,288,14,14,7)
 for x,y in [(78,75),(521,93),(76,513),(517,507),(300,553)]:a.gem(x,y,20,6 if x<300 else 4)

def butterfly(a,v=0):
 # Wings are separate closed curved ribbons, all with visible interiors.
 for side in [-1,1]:
  def tr(p):return (300+side*p[0],p[1])
  def path(points,c):
   p=[tr(x) for x in points]
   a.path(f'M {xy(p[0])} C {xy(p[1])} {xy(p[2])} {xy(p[3])} C {xy(p[4])} {xy(p[5])} {xy(p[6])} Z',c)
  path([(12,283),(45,126),(169,60),(221,111),(259,226),(141,324),(12,318)],2)
  path([(15,320),(158,290),(257,366),(153,503),(100,548),(45,444),(15,341)],3)
  for j in range(4):
   x=50+j*37;y=159+j*2
   path([(16+j*12,284),(x-7,y),(x+30,y-42),(x+25,y+4),(x+36,y+66),(x+5,y+128),(16+j*12,303)],(j+v)%4)
  for j in range(3):
   path([(25,343),(89+j*27,318+j*27),(182-j*12,352+j*30),(122-j*20,433+j*19),(96-j*14,458),(46,402),(25,343)],j%2+4)
  for j in range(5):
   p=tr((180-j*18,158+j*24));a.ellipse(*p,8,10,6)
  p=tr((100,409));a.ellipse(*p,16,23,0)
  a.leaf(tr((4,234)),tr((45,165)),10,6)
 a.ellipse(300,318,16,82,5);a.ellipse(300,236,22,24,6)
 for y in [286,318,350]:a.ellipse(300,y,9,9,7)
 for x,y in [(88,479),(500,491),(300,108),(86,86)]:a.gem(x,y,23,6)

def fox(a,v=0):
 # Celestial fox sitting on a crescent of leaves.
 for x,y,e in [(120,463,(48,373)),(456,462,(546,349)),(180,506,(82,529)),(408,506,(520,537))]:a.leaf((x,y),e,36,4)
 a.path('M 267,460 C 82,541 71,319 167,354 C 256,379 170,419 279,403 Z',0)
 a.path('M 164,355 C 90,324 99,451 155,476 Q 124,422 201,402 Z',1)
 a.path('M 228,301 C 157,404 203,516 302,513 C 397,509 433,428 369,301 Z',2 if v else 7)
 a.path('M 300,329 C 207,338 227,466 300,488 C 383,466 393,338 300,329 Z',1)
 a.path('M 168,238 L 164,101 Q 173, seventy 250,181 Z'.replace('seventy','70'),0)
 a.path('M 432,238 L 436,101 Q 427,70 350,181 Z',0)
 a.poly([(182,130),(186,218),(229,188)],3);a.poly([(418,130),(414,218),(371,188)],3)
 a.path('M 168,219 Q 298,118 432,219 Q 451,298 300,368 Q 149,298 168,219 Z',0 if not v else 2)
 a.path('M 177,230 Q 260,215 293,348 Q 189,315 177,230 Z',1)
 a.path('M 423,230 Q 340,215 307,348 Q 411,315 423,230 Z',1)
 a.poly([(300,204),(324,243),(300,273),(276,243)],6)
 for x in [235,365]:
  a.ellipse(x,271,18,24,5);a.ellipse(x-4,265,6,9,4)
 a.poly([(280,323),(320,323),(300,341)],5)
 for x in [259,341]:a.ellipse(x,480,26,17,0)
 for x,y,r in [(76,230,18),(515,239,20),(300,80,27),(89,86,13),(493,87,16)]:a.gem(x,y,r,6)
 for x in [91,511]:a.ellipse(x,305,11,11,3)

def landscape(a,v=0):
 a.ellipse(402,156,74,74,6)
 a.ellipse(385,139,47,47,7)
 a.path('M 45,340 L 171,145 L 313,339 Z',2)
 a.poly([(124,216),(171,145),(225,217),(193,205),(171,226),(146,207)],3)
 a.path('M 217,356 L 370,211 L 549,354 Z',5)
 a.poly([(326,253),(370,211),(419,251),(385,246),(372,264),(355,249)],4)
 a.path('M 40,356 Q 160,271 303,350 Q 437,287 559,356 L 559,425 L 40,425 Z',0)
 a.path('M 40,410 Q 172,351 300,391 Q 440,342 559,410 L 559,501 L 40,501 Z',2)
 a.path('M 40,471 Q 199,394 320,459 Q 441,407 559,469 L 559,548 L 40,548 Z',5)
 a.path('M 320,358 Q 265,387 345,410 Q 423,440 283,475 Q 221,494 374,548 L 193,548 Q 109,491 269,458 Q 370,437 286,408 Q 223,377 320,358 Z',4)
 for x,y,s in [(98,372,1),(496,387,1.1),(156,450,.8),(454,494,1.3),(72,497,.7)]:
  a.poly([(x-4,y),(x+4,y),(x+4,y+36*s),(x-4,y+36*s)],7)
  for j in range(3):a.poly([(x,y-75*s+j*22*s),(x-24*s-j*4,y-30*s+j*22*s),(x+24*s+j*4,y-30*s+j*22*s)],(j%2)+2)
 for x,y in [(88,118),(292,81),(522,158)]:a.gem(x,y,16,6)

def mandala(a,v=0):
 n=12 if v==0 else (16 if v==1 else 26)
 rings=[(190,270),(124,191),(65,125),(22,65)] if v==0 else ([(200,270),(140,202),(87,142),(43,89),(18,45)] if v==1 else [(238,282),(201,240),(167,203),(134,169),(103,136),(74,105),(45,76),(18,47)])
 for layer,(ri,ro) in enumerate(rings):
  for i in range(n):
   t=math.tau*i/n+layer*math.pi/n;h=math.pi/n
   a.path(f'M {xy(pt(ri,t-h))} Q {xy(pt(ro*1.04,t-h*.6))} {xy(pt(ro,t))} Q {xy(pt(ro*1.04,t+h*.6))} {xy(pt(ri,t+h))} Q {xy(pt(ri*.89,t))} {xy(pt(ri,t-h))} Z',(i%2+layer*2)%8)
 a.ellipse(300,300,24,24,6)

def garden(a,v=0):
 for i in range(7):
  x=65+i*77;y=400+(i%3)*32
  a.leaf((300,530),(x,190+(i%2)*50),24,4+i%2)
 for x,y,s in [(150,230,.7),(444,231,.78),(300,384,1.0)]:
  for i in range(8):
   t=i*math.tau/8
   a.leaf((x,y),pt(98*s,t,(x,y)),42*s,i%4)
  a.ellipse(x,y,25*s,25*s,6)
 for x,y in [(75,83),(320,110),(514,478),(130,481)]:a.gem(x,y,17,6)

ARTS=[('cosmic_peony','Cosmic Peony','Florals',flower,0,PINK,0),('moonwing','Moonwing','Animals',butterfly,0,NIGHT,0),('dream_fox','Dream Fox','Animals',fox,0,DAWN,0),('starlit_valley','Starlit Valley','Places',landscape,0,NIGHT,0),('sugar_mandala','Sugar Mandala','Mandalas',mandala,0,PINK,0),('coral_garden','Coral Garden','Florals',garden,0,DAWN,0),('golden_hour','Golden Hour','Florals',flower,1,DAWN,0),('aurora_wings','Aurora Wings','Animals',butterfly,1,PINK,0),('velvet_fox','Velvet Fox','Animals',fox,1,NIGHT,0),('candy_mountains','Candy Mountains','Places',landscape,1,DAWN,0),('jewel_wheel','Jewel Wheel','Mandalas',mandala,1,NIGHT,0),('orchid_party','Orchid Party','Florals',garden,1,NIGHT,0),('nebula_lotus','Nebula Lotus','Mandalas',mandala,2,PINK,3),('rosewater','Rosewater','Florals',flower,2,NIGHT,6)]

def assets():
 icons={
 'star':'<path d="M32 4 40 23 61 25 45 39 50 60 32 49 14 60 19 39 3 25 24 23Z" fill="#FFD66E" stroke="#EBA543" stroke-width="2"/><path d="m32 10 5 15-12 4Z" fill="#FFF3BB"/>',
 'back':'<path d="m38 14-18 18 18 18"/>',
 'hint':'<path d="M22 44C22 36 13 35 13 24a19 19 0 0 1 38 0c0 11-9 12-9 20ZM23 51h18M27 58h10M27 25l5 9 7-14"/>',
 'home':'<path d="m9 29 23-20 23 20M16 26v29h12V39h9v16h12V26"/>',
 'gallery':'<rect x="9" y="10" width="46" height="44" rx="9"/><path d="m12 46 15-18 11 12 8-10 8 13"/><circle cx="42" cy="22" r="4"/>',
 'calendar':'<rect x="9" y="14" width="46" height="42" rx="9"/><path d="M10 27h44M22 7v14M43 7v14m-22 18 8 8 15-13"/>',
 'sound':'<path d="M10 25h12L37 12v40L22 39H10ZM44 23q12 9 0 18M49 14q21 18 0 36"/>',
 'settings':'<path d="m25 7 14 0 3 9 9 3 6 12-6 12-9 3-3 11H25l-3-11-9-3-6-12 6-12 9-3Z"/><circle cx="32" cy="32" r="9"/>',
 'check':'<path d="m13 32 12 13 27-29"/>',
 'reset':'<path d="M13 25a21 21 0 1 1 1 19M10 8v18h18"/>',
 'zoom':'<circle cx="28" cy="27" r="17"/><path d="m42 42 14 14M28 18v18M19 27h18"/>',
 'lock':'<rect x="14" y="27" width="36" height="29" rx="7"/><path d="M22 27V17a10 10 0 0 1 20 0v10M32 38v7"/>',
 }
 for name,body in icons.items():
  (ROOT/'assets/icons'/f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none" stroke="#65508E" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round">{body}</svg>')
 for name in ['hint','gallery','calendar']:
  source=(ROOT/'assets/icons'/f'{name}.svg').read_text()
  (ROOT/'assets/icons'/f'{name}_light.svg').write_text(source.replace('#65508E','#FFFFFF'))
 mascot='''<defs><linearGradient id="a" x2="0.7" y2="1"><stop stop-color="#A3FFFF"/><stop offset=".5" stop-color="#41DEDF"/><stop offset="1" stop-color="#5384EA"/></linearGradient></defs><path d="M82 5C94 51 129 55 132 96c4 52-40 66-70 61-37-6-55-37-47-66C22 61 59 57 82 5Z" fill="url(#a)" stroke="#5670BC" stroke-width="4"/><ellipse cx="52" cy="103" rx="11" ry="17" fill="#2F275F"/><ellipse cx="103" cy="103" rx="11" ry="17" fill="#2F275F"/><ellipse cx="49" cy="98" rx="4" ry="6" fill="white"/><ellipse cx="100" cy="98" rx="4" ry="6" fill="white"/><ellipse cx="35" cy="122" rx="12" ry="6" fill="#FB91CB"/><ellipse cx="119" cy="122" rx="12" ry="6" fill="#FB91CB"/><path d="M67 122q10 12 21 0" fill="none" stroke="#424174" stroke-width="4" stroke-linecap="round"/><path d="m78 52 5 10 11 1-8 8 2 11-10-5-10 5 2-11-8-8 11-1Z" fill="#FFE28A"/><path d="M33 83q9-19 22-20" fill="none" stroke="#D3FFFF" stroke-width="7" stroke-linecap="round"/>'''
 (ROOT/'assets/icons/pip.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 170">'+mascot+'</svg>')
 (ROOT/'assets/icons/app_icon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 170 190"><rect width="170" height="190" rx="42" fill="#6944C7"/><g transform="translate(10 10)">'+mascot+'</g></svg>')
 # Original synthesized chimes, no runtime sound library dependencies.
 for name,notes,duration in [('fill',[659.25,987.77],.24),('tap',[523.25],.1),('win',[523.25,659.25,783.99,1046.5],1.4),('hint',[880,1174.66],.45)]:
  samples=[];rate=22050
  for j in range(int(rate*duration)):
   t=j/rate; val=0
   for k,f in enumerate(notes):
    dt=t-k*(.13 if name=='win' else .035)
    if dt>=0:val+=math.sin(math.tau*f*dt)*math.exp(-dt*7)*min(1,dt*100)*.20/len(notes)
   samples.append(int(max(-1,min(1,val))*32767))
  with wave.open(str(ROOT/'assets/audio'/f'{name}.wav'),'wb') as w:
   w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(struct.pack('<'+'h'*len(samples),*samples))

if __name__=='__main__':
 assets()
 for idx,(id,title,cat,fn,var,pal,unlock) in enumerate(ARTS):
  a=Art(pal);fn(a,var);data=a.save(id);count=len(data['shapes']);difficulty='Intricate' if count>=180 else 'Medium' if count>50 else 'Easy'
  (ROOT/'resources/levels'/f'{id}.tres').write_text(f'''[gd_resource type="Resource" script_class="ArtworkData" load_steps=3 format=3]

[ext_resource type="Script" path="res://scripts/game/artwork_data.gd" id="1"]
[ext_resource type="Texture2D" path="res://assets/art/{id}_preview.svg" id="2"]

[resource]
script = ExtResource("1")
id = "{id}"
title = "{title}"
category = "{cat}"
difficulty = "{difficulty}"
minutes = {max(3,round(count/7))}
unlock_after = {unlock}
regions_path = "res://resources/levels/{id}.json"
thumbnail = ExtResource("2")
background = Color(0.12, 0.075, 0.26, 1)
''')
  print(id,count,'regions',flush=True)
