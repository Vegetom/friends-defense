"""Draw the original Friends Defense enemy atlas. Authoring only; requires Pillow.

Rows group the six roles by terrain; columns are the four animation frames.
Use --embed to update the standalone game, or --output to inspect the atlas.
"""
import argparse
import base64
import io
from pathlib import Path
import re

from PIL import Image, ImageDraw

SIZE = 48
INK = "#171a2b"
# Skin, armour, faction light, textile shadow. Accent colours are differentiated by shape too.
FACTIONS = [
    ("#a5d56a", "#567b3f", "#eee794", "#344a42"),
    ("#bba9df", "#625a91", "#eed6ff", "#373658"),
    ("#8ed39e", "#406960", "#aafca8", "#2a4647"),
    ("#abe8f7", "#3980a5", "#d5fffc", "#24415f"),
    ("#ec9667", "#a14743", "#ffce70", "#5d2d37"),
    ("#c7a9ec", "#654281", "#ffe29c", "#3f2d55"),
    ("#c7dfd6", "#3f5a63", "#8bffd6", "#263c4a"),
]


def tone(colour, percent):
    rgb = tuple(int(colour[k:k+2], 16) for k in (1, 3, 5))
    return tuple(round(v+(255-v)*percent) if percent > 0 else round(v*(1+percent)) for v in rgb) + (255,)


def sprite(stage, role, frame):
    im=Image.new("RGBA", (SIZE, SIZE))
    pen=ImageDraw.Draw(im)
    skin, shell, light, cloth=FACTIONS[stage]
    shade=tone(shell,-.28)
    glint=tone(shell,.32)
    dark_skin=tone(skin,-.30)
    pale=tone(skin,.40)
    fast=role==1
    tank=role==2
    air=role==3
    boss=role>=4
    final=role==5
    lift=([0,-1,-1,0] if air else [0,-1,0,-1])[frame]
    # Motion is built into the silhouette: feet alternate, wings fold and sweep.
    def poly(colour, points, edge=INK):
        pen.polygon([(x,y+lift) for x,y in points], fill=colour, outline=edge)
    def box(colour,x0,y0,x1,y1):
        pen.rectangle((x0,y0+lift,x1,y1+lift), fill=colour)
    def lit(colour, points):
        poly(colour,points,None)
    def gem(x,y,colour=light,r=3):
        poly(colour,[(x,y-r),(x+r,y),(x,y+r),(x-r,y)])
        box("#fff6dc",x-1,y-1,x,y)

    if air:
        sweep=[-6,-2,4,0][frame]
        for side in (-1,1):
            def wing(points):
                return [(24+side*x,y) for x,y in points]
            poly(cloth,wing([(6,28),(13,16+sweep),(22,11+sweep),(22,20+sweep),(18,27),(9,35)]))
            poly(shell,wing([(7,27),(13,18+sweep),(22,11+sweep),(19,22+sweep),(11,30)]))
            lit(light,wing([(13,18+sweep),(22,12+sweep),(18,20+sweep),(13,24)]))
            lit(glint,wing([(10,25),(14,22),(13,29),(9,31)]))
        poly(shade,[(17,29),(31,29),(33,35),(28,40),(24,42),(20,40),(15,35)])
        gem(24,36,r=4)
    else:
        stride=[-2,0,2,0][frame] if not tank else [-1,0,1,0][frame]
        stance=8 if tank or boss else 5
        for side in (-1,1):
            x=24+side*stance
            dy=stride*side
            poly(cloth,[(x-4,34),(x+4,34),(x+4,42+dy),(x+6,44+dy),(x+5,45+dy),(x-5,45+dy),(x-6,42+dy)])
            box(glint,x-3,40+dy,x+2,41+dy)
        if boss:
            if stage in (0,2,4,6):
                # Cape, asymmetric plates, and a jagged hem distinguish the commanders.
                poly(cloth,[(10,21),(34,21),(39,29),(43,43),(36,40),(33,44),(25,39),(17,42),(7,40),(10,32)])
                lit(shade,[(14,25),(22,25),(19,38),(11,40)])
            else:
                poly(shade,[(12,21),(36,21),(42,34),(43,40),(35,44),(12,44),(5,41),(7,31)])
            if final:
                for x in (8,39):
                    gem(x,13,r=3)
        if fast:
            poly(light,[(17,23),(12,23),(7,26),(2,24),(5,30),(12,31),(19,28)])
        width=14 if boss else 13 if tank else 8 if fast else 10
        for side in (-1,1):
            x=24+side*(width+1)
            y=29+(([0,2,0,-2][frame])*side if fast else 0)
            points=[(x-4,y-4),(x+3,y-4),(x+4,y+1),(x+3,y+6),(x-4,y+6),(x-5,y+1)]
            poly(skin,points)
            poly(glint,[(x-5,y-4),(x+4,y-4),(x+4,y),(x-5,y+2)])
            box(dark_skin,x-2,y+4,x+2,y+5)
        poly(shell,[(24-width,26),(24+width,26),(24+width-1,35),(29,40),(19,40),(25-width,35)])
        lit(glint,[(25-width,28),(29,28),(28,31),(25-width,32)])
        lit(shade,[(27,29),(22+width,29),(22+width,34),(28,38),(21,38)])
        box(INK,18,36,30,38)
        box(light,22,36,25,37)
        if tank or boss:
            for x in (7,33):
                poly(shell,[(x,24),(x+4,20),(x+8,20),(x+11,24),(x+9,31),(x+1,31)])
                lit(glint,[(x+1,25),(x+5,22),(x+8,22),(x+10,25),(x+4,26)])
                box(light,x+2,27,x+7,28)
        if boss:
            gem(24,33,r=4)
        elif not fast and not tank:
            box(light,19,31,21,32)

    w=13 if boss else 11 if tank else 9 if fast or air else 10
    top=10 if boss else 12 if not air else 16
    jaw=30 if boss else 29 if not air else 32
    center=24
    poly(skin,[(center-w,top+6),(center-w+3,top+1),(19,top-1),(29,top-1),
      (center+w-3,top+1),(center+w,top+6),(center+w-1,jaw-5),(29,jaw),(19,jaw),(center-w+1,jaw-5)])
    lit(pale,[(center-w+2,top+5),(19,top+1),(27,top+1),(24,top+9),(center-w+2,top+10)])
    lit(dark_skin,[(30,top+4),(center+w-1,top+7),(center+w-2,jaw-5),(28,jaw-1),(20,jaw-1),(25,jaw-5)])
    # Each faction keeps a signature crown, face plate or headpiece.
    if stage==0:
        poly(shade,[(center-w,top+5),(center-w-1,top),(17,top+1),(20,top-4),
                    (25,top-2),(29,top-5),(30,top),(center+w+1,top-2),
                    (center+w,top+5),(27,top+3),(22,top+7),(20,top+4)])
        lit(glint,[(18,top+2),(21,top-2),(25,top),(22,top+4)])
    elif stage==1:
        poly(shell,[(center-w-1,top+9),(center-w-1,top+2),(18,top-2),(30,top-2),
                    (center+w+1,top+2),(center+w+1,top+9),(29,top+6),(19,top+6)])
        box(light,18,top+3,30,top+4)
        box(glint,20,top,27,top+1)
    elif stage==2:
        poly(shade,[(center-w-1,top+7),(center-w-3,top+1),(17,top+2),
                    (20,top-3),(24,top-5),(27,top-1),(31,top+2),
                    (center+w+3,top+1),(center+w+1,top+8),(28,top+5),(20,top+6)])
        gem(24,top+2,r=3)
    elif stage==3:
        poly(shell,[(center-w-2,jaw-7),(center-w-3,top+5),(17,top-1),
                   (24,top-4),(33,top),(center+w+3,top+6),(center+w+2,jaw-7),
                   (center+w-2,top+9),(28,top+4),(21,top+4),(center-w+2,top+10)])
        box(light,22,top-1,26,top)
    elif stage==4:
        poly(light,[(center-w,top+10),(center-w-4,top-4),(18,top+2),(20,top+5),
        (28,top+5),(30,top+2),(center+w+4,top-4),(center+w,top+10)])
        box(cloth,21,top+3,27,top+6)
    elif stage==5:
        poly(shell,[(center-w-1,top+7),(center-w-1,top-2),(19,top+1),(24,top-6),
            (29,top+1),(center+w+1,top-2),(center+w+1,top+7),(27,top+5),(21,top+5)])
        gem(24,top+2,r=3)
    else:
        poly(cloth,[(center-w-1,jaw-3),(center-w-2,top-3),(18,top+1),(24,top-5),
        (30,top+1),(center+w+2,top-3),(center+w+1,jaw-3),(29,jaw-2),(24,jaw+1),(19,jaw-2)])
        box("#ddf5ee",21,jaw-3,26,jaw-1)

    eye=top+9
    poly(INK,[(center-w+2,eye-1),(21,eye+1),(21,eye+4),(center-w+3,eye+4)],None)
    poly(INK,[(center+w-2,eye-1),(27,eye+1),(27,eye+4),(center+w-3,eye+4)],None)
    box("#fff4de" if stage<3 else light,18,eye+1,20,eye+2)
    box("#fff4de" if stage<3 else light,28,eye+1,30,eye+2)
    box(INK,22,jaw-3,25,jaw-2)
    if tank:
        poly(shade,[(11,25),(17,25),(20,29),(28,29),(31,25),(37,25),(35,31),(31,33),(17,33),(13,31)])
        box(light,20,30,27,30)
    if boss:
        # A different crest profile for each faction, with a larger V10 silhouette.
        silhouettes = [
            [(9,12),(9,6),(14,7),(15,1),(22,6),(24,2),(27,6),(33,1),(35,7),(39,5),(38,12)],
            [(9,12),(6,2),(15,6),(18,9),(30,9),(33,6),(42,2),(39,12)],
            [(10,12),(12,4),(18,5),(23,0),(29,5),(35,4),(38,12)],
            [(9,14),(7,8),(14,5),(20,3),(24,1),(29,3),(35,5),(42,9),(38,13)],
            [(10,13),(5,1),(15,7),(22,8),(29,7),(43,1),(37,13)],
            [(10,13),(9,5),(15,5),(15,8),(21,8),(21,2),(27,2),(27,8),(33,8),(33,5),(39,5),(38,13)],
            [(9,13),(9,1),(14,6),(20,8),(24,4),(28,8),(34,6),(39,1),(39,13)],
        ]
        points=silhouettes[stage]
        if final:
            points=[(24+round((x-24)*1.07),max(0,y-1)) for x,y in points]
        poly(light if final else cloth,points)
        gem(24,8,r=4 if final else 3)
        if stage==6:
            box(light,14,31,17,32)
            box(light,31,31,34,32)
        elif stage==2:
            for x,y in [(7,31),(41,31)]:
                gem(x,y,r=3)
    return im


def atlas():
    result=Image.new("RGBA",(4*SIZE,len(FACTIONS)*6*SIZE))
    for stage in range(len(FACTIONS)):
        for role in range(6):
            for frame in range(4):
                result.paste(sprite(stage,role,frame),(frame*SIZE,(stage*6+role)*SIZE))
    return result


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--embed",type=Path,help="update the atlas in index.html")
    parser.add_argument("--output",type=Path,help="save a standalone PNG for review")
    args=parser.parse_args()
    target=atlas()
    if args.output:
        target.save(args.output,optimize=True)
    if args.embed:
        buffer=io.BytesIO()
        target.save(buffer,format="PNG",optimize=True)
        uri="data:image/png;base64,"+base64.b64encode(buffer.getvalue()).decode("ascii")
        original=args.embed.read_text()
        updated,count=re.subn(r"(const ENEMY_ATLAS_URI=')[^']*(');",lambda m:m[1]+uri+m[2]+";",original)
        if count!=1:
            parser.error("expected exactly one ENEMY_ATLAS_URI declaration")
        args.embed.write_text(updated)
