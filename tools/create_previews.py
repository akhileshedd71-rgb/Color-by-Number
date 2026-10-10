#!/usr/bin/env python3
"""Add presentation-only paint gradients to thumbnails; puzzle sources stay flat."""
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def adjust(h,amount):
 rgb=[int(h[i:i+2],16) for i in (1,3,5)]
 return '#'+''.join(f'{round(v+(255-v)*amount) if amount>=0 else round(v*(1+amount)):02x}' for v in rgb)
for path in (ROOT/'content/svg').glob('*.svg'):
 source=path.read_text();root=ET.fromstring(source)
 colors=list(dict.fromkeys(e.get('fill') for e in root if e.get('fill')))
 defs='<defs>'
 for i,c in enumerate(colors):
  defs+=f'<radialGradient id="paint{i}" cx="32%" cy="24%" r="90%"><stop stop-color="{adjust(c,.35)}"/><stop offset=".48" stop-color="{c}"/><stop offset="1" stop-color="{adjust(c,-.24)}"/></radialGradient>'
  source=source.replace(f'fill="{c}"',f'fill="url(#paint{i})"')
 defs+='</defs>'
 source=source.replace('stroke-width="2.2"','stroke-width="1.7"')
 pos=source.index('>')+1;source=source[:pos]+defs+source[pos:]
 (ROOT/'assets/art'/f'{path.stem}_preview.svg').write_text(source)
print('Created 14 painted preview illustrations')
