#!/usr/bin/env python3
"""Compile a deliberate SVG subset to numbered Godot puzzle data.

Supports absolute/relative M L H V C Q Z closed single-contour paths,
polygons, ellipses and circles. Colors are clustered deterministically by
RGB distance. Explicitly rejects transforms, holes, arcs, external styles,
and compound paths: flatten/expand these in your vector editor first.
Labels use a visible interior distance search, accounting for layers above.
"""
import argparse, json, math, re, xml.etree.ElementTree as ET
from pathlib import Path

TOKEN = re.compile(r'[a-zA-Z]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?')

def flatten(d, steps=16):
    tokens=TOKEN.findall(d); i=0; cmd=''; p=(0.,0.); start=None; out=[]; closed=False
    def pair(values, relative):
        return (float(values[0])+(p[0] if relative else 0), float(values[1])+(p[1] if relative else 0))
    while i<len(tokens):
        if tokens[i].isalpha(): cmd=tokens[i]; i+=1
        rel=cmd.islower(); c=cmd.upper()
        if c=='Z':
            closed=True
            if i != len(tokens): raise ValueError('Compound paths are unsupported; split each contour.')
            break
        n={'M':2,'L':2,'H':1,'V':1,'C':6,'Q':4}.get(c)
        if n is None: raise ValueError('Unsupported SVG command '+cmd+'; convert to M/L/C/Q/Z.')
        values=tokens[i:i+n]; i+=n
        if c in ('M','L'):
            p=pair(values,rel)
            if c=='M':
                if start is not None: raise ValueError('Compound paths are unsupported.')
                start=p; cmd='l' if rel else 'L'
            out.append(p)
        elif c=='H': p=(float(values[0])+(p[0] if rel else 0),p[1]); out.append(p)
        elif c=='V': p=(p[0],float(values[0])+(p[1] if rel else 0)); out.append(p)
        else:
            origin=p; a=pair(values[:2],rel); b=pair(values[2:4],rel)
            end=pair(values[4:6],rel) if c=='C' else b
            for j in range(1,steps+1):
                t=j/steps; u=1-t
                if c=='C': pt=tuple(u*u*u*origin[k]+3*u*u*t*a[k]+3*u*t*t*b[k]+t*t*t*end[k] for k in (0,1))
                else: pt=tuple(u*u*origin[k]+2*u*t*a[k]+t*t*end[k] for k in (0,1))
                out.append(pt)
            p=end
    if not closed: raise ValueError('Every coloring path must be closed with Z.')
    if len(out)>1 and math.dist(out[0],out[-1])<0.01: out.pop()
    return out

def inside(p, poly):
    x,y=p; hit=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]: hit=not hit
    return hit

def edge_distance(p, poly):
    best=1e12
    for a,b in zip(poly,poly[1:]+poly[:1]):
        dx,dy=b[0]-a[0],b[1]-a[1]; denom=dx*dx+dy*dy
        t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/denom)) if denom else 0
        best=min(best,math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy))
    return best

def interior(poly, above):
    xs,ys=zip(*poly); bounds=(min(xs),min(ys),max(xs),max(ys))
    # Limit occluders by bounding boxes; keeps even intricate puzzles quick.
    above=[q for q in above if min(x for x,y in q)<=bounds[2] and max(x for x,y in q)>=bounds[0] and min(y for x,y in q)<=bounds[3] and max(y for x,y in q)>=bounds[1]]
    best=None; score=-1.; x0,y0,x1,y1=bounds
    for refinement in range(3):
        sx=(x1-x0)/12; sy=(y1-y0)/12
        for iy in range(13):
            for ix in range(13):
                pt=(x0+sx*ix,y0+sy*iy)
                if not inside(pt,poly) or any(inside(pt,q) for q in above): continue
                dist=min([edge_distance(pt,poly)]+[edge_distance(pt,q) for q in above])
                if dist>score: best=pt; score=dist
        if best is None: continue
        x0,y0,x1,y1=best[0]-sx,best[1]-sy,best[0]+sx,best[1]+sy
    if best is None or score<2: raise ValueError('Region has no accessible visible interior.')
    return [round(v,2) for v in best], round(score, 2)

def compile_svg(source, target, cluster=0):
    root=ET.parse(source).getroot(); view=[float(x) for x in root.get('viewBox','0 0 600 600').split()]
    palette=[]; shapes=[]
    for el in root.iter():
        tag=el.tag.split('}')[-1]
        if el.get('data-decoration')=='true': continue
        if el.get('transform'): raise ValueError('Apply SVG transforms before import.')
        if tag in ('svg','g','title','desc','metadata'): continue
        if tag not in ('path','polygon','circle','ellipse'): raise ValueError('Unsupported SVG element: '+tag)
        fill=el.get('fill','')
        if not re.fullmatch(r'#[\da-fA-F]{6}',fill): raise ValueError('Use explicit six-digit flat hex fills.')
        if tag=='path': pts=flatten(el.attrib['d'])
        elif tag=='polygon':
            nums=[float(n) for n in TOKEN.findall(el.attrib['points'])]; pts=list(zip(nums[::2],nums[1::2]))
        else:
            cx=float(el.get('cx','0')); cy=float(el.get('cy','0')); rx=float(el.get('rx',el.get('r','0'))); ry=float(el.get('ry',el.get('r','0')))
            pts=[(cx+rx*math.cos(t*math.tau/48),cy+ry*math.sin(t*math.tau/48)) for t in range(48)]
        if len(pts)<3: raise ValueError('Degenerate region')
        rgb=lambda h:tuple(int(h[i:i+2],16) for i in (1,3,5))
        matches=[i for i,c in enumerate(palette) if math.dist(rgb(c),rgb(fill))<=cluster]
        if matches: ci=matches[0]
        else: ci=len(palette); palette.append(fill)
        shapes.append({'id':el.get('id',f'region_{len(shapes):03}'),'color':ci,'points':[[round(x,2),round(y,2)] for x,y in pts]})
    ids=[s['id'] for s in shapes]
    if len(ids)!=len(set(ids)): raise ValueError('Region IDs must be unique')
    for i,s in enumerate(shapes): s['label'],s['label_radius']=interior(s['points'],[s2['points'] for s2 in shapes[i+1:]])
    result={'version':1,'canvas_size':view[2:],'palette':palette,'shapes':shapes}
    Path(target).write_text(json.dumps(result,separators=(',',':'))+'\n')
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('svg'); ap.add_argument('json'); ap.add_argument('--cluster',type=float,default=0)
    args=ap.parse_args(); result=compile_svg(args.svg,args.json,args.cluster)
    print(f"Compiled {len(result['shapes'])} regions, {len(result['palette'])} colors → {args.json}")
