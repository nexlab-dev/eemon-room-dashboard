#!/usr/bin/env python3
"""Render 10 original EEMON typographic vertical shorts (no external assets).

No real product photographs, video footage, music, or invented prices used.
Animated editorial motion cards with an original synth bed, not an AI-video promise.
Requires pillow/numpy/ffmpeg. Source is editable in normal Chat and Work.
"""
import argparse
import json
import math
import pathlib
import subprocess
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=pathlib.Path(__file__).resolve().parent.parent
FONT_BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
FONT_REG='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
W,H=1080,1920
DURATION=12.0
FPS=24
PALETTES=[
 ('#103830','#f96c48','#cbef90','#faf7ed'),
 ('#22283a','#d4f377','#ff8971','#faf7ed'),
 ('#30404c','#f7cc79','#e6a8a3','#fffafa'),
 ('#332b4a','#c8f0b2','#eab9dd','#fff8f7'),
 ('#183a39','#efb6a4','#d9f0a8','#fbfbf4'),
 ('#3b302b','#d2e98e','#f0bc9b','#fffbf2'),
 ('#263842','#ff9d72','#b5ddca','#fffbf5'),
 ('#254448','#f9c98d','#d1eebf','#fffdf8'),
 ('#423026','#f4cc75','#f49c94','#fffaf3'),
 ('#203a32','#cbed8d','#fb9a7d','#fff8e8')
]

def rgb(h):return tuple(int(h[i:i+2],16) for i in (1,3,5))
def f(size,bold=True):return ImageFont.truetype(FONT_BOLD if bold else FONT_REG,size)
def rr(draw, rect, radius, fill, outline=None, width=1):draw.rounded_rectangle(rect,radius,fill=fill,outline=outline,width=width)
def txt(draw,xy,s,font,fill,anchor='la',spacing=5):draw.multiline_text(xy,s,font=font,fill=fill,anchor=anchor,spacing=spacing,stroke_width=0)
def lines_center(draw,ls,top,font,fg,accent=None):
    sizes=[draw.textbbox((0,0),line,font=font)[2] for line in ls]
    for i,line in enumerate(ls):
        x=(W-sizes[i])/2
        txt(draw,(x,top+i*int(font.size*1.46)),line,font,accent if i==1 and accent else fg)

def paint_icon(d,name,cx,cy,color,scale=1):
    # Pure vector: no trademark or commercial photo. Decorative flat pictograms.
    r=lambda v:int(v*scale)
    c=color
    if name in ('shopping','sale'):
        d.rounded_rectangle((cx-r(120),cy-r(55),cx+r(120),cy+r(115)),radius=r(20),outline=c,width=r(13))
        d.arc((cx-r(56),cy-r(128),cx+r(56),cy+r(17)),180,360,fill=c,width=r(14))
        if name=='sale':d.line((cx-r(35),cy-r(20),cx+r(40),cy+r(68)),fill=c,width=r(10))
    elif name=='printer':
        d.rounded_rectangle((cx-r(130),cy-r(50),cx+r(130),cy+r(115)),r(20),outline=c,width=r(13))
        d.rectangle((cx-r(80),cy-r(124),cx+r(80),cy-r(40)),outline=c,width=r(12))
        d.rectangle((cx-r(75),cy+r(80),cx+r(75),cy+r(142)),fill=c)
    elif name=='bed':
        d.line((cx-r(130),cy+r(90),cx+r(130),cy+r(90)),fill=c,width=r(16));d.line((cx-r(120),cy+r(90),cx-r(120),cy+r(135)),fill=c,width=r(13));d.line((cx+r(120),cy+r(90),cx+r(120),cy+r(135)),fill=c,width=r(13));rr(d,(cx-r(105),cy-r(38),cx+r(105),cy+r(85)),r(19),c)
    elif name=='plug':
        rr(d,(cx-r(64),cy-r(20),cx+r(64),cy+r(100)),r(23),c);d.line((cx-r(36),cy-r(88),cx-r(36),cy-r(155)),fill=c,width=r(16));d.line((cx+r(36),cy-r(88),cx+r(36),cy-r(155)),fill=c,width=r(16));d.arc((cx-r(120),cy-r(115),cx+r(120),cy+r(110)),190,350,fill=c,width=r(12))
    elif name=='vacuum':
        d.line((cx-r(85),cy-r(130),cx+r(60),cy+r(90)),fill=c,width=r(15));rr(d,(cx-r(5),cy+r(55),cx+r(128),cy+r(120)),r(25),c);d.ellipse((cx-r(43),cy+r(100),cx+r(2),cy+r(145)),fill=c)
    elif name=='storage':
        rr(d,(cx-r(125),cy-r(100),cx+r(125),cy+r(125)),r(12),None,outline=c,width=r(15));d.line((cx-r(120),cy-r(35),cx+r(120),cy-r(35)),fill=c,width=r(14));d.line((cx-r(120),cy+r(50),cx+r(120),cy+r(50)),fill=c,width=r(14));d.ellipse((cx-r(10),cy-r(70),cx+r(10),cy-r(50)),fill=c)
    elif name=='car':
        rr(d,(cx-r(140),cy-r(20),cx+r(140),cy+r(90)),r(30),c);d.polygon(((cx-r(100),cy-r(20)),(cx-r(60),cy-r(95)),(cx+r(65),cy-r(95)),(cx+r(105),cy-r(20))),fill=c);d.ellipse((cx-r(100),cy+r(58),cx-r(43),cy+r(123)),fill='#132f30');d.ellipse((cx+r(43),cy+r(58),cx+r(100),cy+r(123)),fill='#132f30')
    elif name=='humidifier':
        rr(d,(cx-r(88),cy-r(10),cx+r(88),cy+r(115)),r(30),c);d.arc((cx-r(80),cy-r(160),cx-r(10),cy-r(35)),130,310,fill=c,width=r(12));d.arc((cx+r(10),cy-r(160),cx+r(80),cy-r(35)),130,310,fill=c,width=r(12))
    else:
        rr(d,(cx-r(120),cy-r(110),cx+r(120),cy+r(115)),r(18),None,outline=c,width=r(14));d.line((cx-r(60),cy-r(20),cx-r(10),cy+r(35),cx+r(76),cy-r(65)),fill=c,width=r(15),joint='curve')

def fitfont(draw, words, wanted, limit=924):
    words=words.split('\n')
    size=wanted
    while size>35:
        ff=f(size)
        if all(draw.textbbox((0,0),line,font=ff)[2]<=limit for line in words):
            return ff
        size-=2
    return f(size)

def draw_scene(reel,palette,phase):
    deep,orange,lime,white=palette
    img=Image.new('RGB',(W,H),rgb(deep));d=ImageDraw.Draw(img)
    # Graphic grain-like array and orbital curves, only vector originals.
    d.ellipse((W-520,-380,W+320,460),fill=rgb('#224b45'))
    d.ellipse((-400,H-430,440,H+420),fill=rgb('#244c47'))
    for i in range(10):
        x=90+i*105
        d.line((x,0,x,H),fill=rgb('#1c433e'),width=2)
    # header and logo
    rr(d,(72,95,162,185),28,rgb(orange));txt(d,(92,97),'え',f(64),rgb(white))
    txt(d,(185,102),'EEMON  /  BUY BETTER',f(32),rgb(white))
    txt(d,(185,151),'買い物に、ちゃんと理由を。',f(21,False),rgb(lime))
    for j in range(4):rr(d,(73+j*105,246,159+j*105,261),5,rgb(orange if j==phase else '#56736b'))
    txt(d,(72,310),reel['slides'][phase]['kicker'],f(32),rgb(lime))
    if phase==0:
        # hero question
        p=reel['slides'][phase]
        txt(d,(76,425),p['headline'],fitfont(d,p['headline'],100),rgb(white),spacing=44)
        d.ellipse((W-480,835,W-100,1215),fill=rgb(orange))
        paint_icon(d,reel['icon'],W-292,1010,rgb(deep),.82)
        rr(d,(77,1270,865,1374),26,rgb(white))
        txt(d,(112,1287),'知っておきたい買い物の落とし穴',f(39),rgb(deep))
    elif phase==1:
        p=reel['slides'][phase]
        txt(d,(76,408),p['headline'],fitfont(d,p['headline'],92),rgb(white),spacing=34)
        # floating tilted education cards
        rr(d,(88,940,1003,1320),44,rgb(white))
        paint_icon(d,reel['icon'],350,1100,rgb(deep),.79)
        rr(d,(632,1023,914,1136),32,rgb(lime));txt(d,(684,1040),'CHECK',f(47),rgb(deep))
        txt(d,(641,1160),'WHY?',f(54),rgb(orange))
    elif phase==2:
        p=reel['slides'][phase]
        txt(d,(77,421),p['headline'],fitfont(d,p['headline'],86),rgb(white),spacing=35)
        txt(d,(77,835),'CHECK LIST',f(43),rgb(lime))
        checks=[s.strip() for s in p['headline'].replace('\n','・').split('・') if s.strip()]
        # Ensure 3 legible items even when copy is 2 lines
        for i,word in enumerate(checks[:3]):
            y=928+i*147
            rr(d,(75,y,1004,y+121),26,rgb(white))
            rr(d,(99,y+31,166,y+94),18,rgb(orange))
            txt(d,(118,y+39),'✓',f(46),rgb(white))
            txt(d,(197,y+31),word,fitfont(d,word,49,750),rgb(deep))
    else:
        p=reel['slides'][phase]
        txt(d,(76,430),p['headline'],fitfont(d,p['headline'],93),rgb(white),spacing=30)
        d.ellipse((206,845,874,1513),fill=rgb(lime))
        txt(d,(310,1045),'ええもん',f(85),rgb(deep))
        txt(d,(317,1180),'探しパパ',f(83),rgb(deep))
        rr(d,(191,1490,884,1578),43,rgb(orange))
        txt(d,(313,1508),'あとで見返してな  ↗',f(42),rgb(white))
    # Keep footer in safe zone, no pricing claims
    d.line((77,1683,1004,1683),fill=rgb('#6e9185'),width=3)
    txt(d,(77,1721),f"EEMON   •   EP.{reel['number']:02d}",f(29),rgb(white))
    txt(d,(77,1773),'この動画には広告リンクなし',f(26,False),rgb('#b2d0bf'))
    return img

def make_audio(path, no):
    # Newly composed short 4-bar chord pattern; no copied musical recording.
    sr=44100; t=np.arange(int(DURATION*sr))/sr; out=np.zeros(len(t),dtype=np.float64)
    tempo=115+no%7; beat=60/tempo; rng=np.random.default_rng(1940+no)
    chords=[[196,246.94,293.66],[174.61,220,261.63],[164.81,207.65,246.94],[196,246.94,329.63]]
    for i in range(int(DURATION/(beat/2))):
        start=int((i*beat/2)*sr);length=min(int(0.31*sr),len(t)-start)
        if length<=0:break
        tt=np.arange(length)/sr; freq=chords[(i//4)%4][i%3]*2
        env=(1-np.exp(-tt*35))*np.exp(-tt*11)
        pluck=(np.sin(2*np.pi*freq*tt)+.3*np.sin(2*np.pi*2*freq*tt))*.055*env
        out[start:start+length]+=pluck
    for k in range(int(DURATION/beat)+1):
        start=int(k*beat*sr);length=min(int(.15*sr),len(t)-start)
        if length<=0:break
        tt=np.arange(length)/sr;env=np.exp(-tt*39)
        out[start:start+length]+= .065*np.sin(2*np.pi*(88+65*np.exp(-tt*42))*tt)*env
        if k%2:
            noise=rng.normal(size=length)*.011*np.exp(-tt*40)
            out[start:start+length]+=noise
    out=np.tanh(out*1.5)
    fadin=np.minimum(1,np.arange(len(t))/(sr*.12));fadout=np.minimum(1,(len(t)-np.arange(len(t)))/(sr*.42))
    out*=fadin*fadout
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((out*32767).astype('<i2').tobytes())

def render_one(reel,output_dir,no_audio=False):
    palette=PALETTES[(reel['number']-1)%len(PALETTES)];output_dir.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='eemon-') as tmp:
        temp=pathlib.Path(tmp)
        imgs=[]
        for scene in range(4):
            path=temp/f'scene{scene}.png';draw_scene(reel,palette,scene).save(path,optimize=True);imgs.append(path)
        audio=temp/'original.wav';make_audio(audio,reel['number'])
        args=['ffmpeg','-hide_banner','-loglevel','error','-y']
        for img in imgs:args+=['-loop','1','-framerate',str(FPS),'-t','3','-i',str(img)]
        args+=['-i',str(audio)]
        filters=[]
        for i in range(4):
            # subtle kinetic push-in, independent of source frames
            filters.append(f'[{i}:v]scale=1140:2030,crop=1080:1920:x=\'(iw-ow)/2+12*sin(n/42)\':y=\'(ih-oh)/2+10*sin(n/53)\',fps={FPS},trim=duration=3,setpts=PTS-STARTPTS,fade=t=in:st=0:d=0.2,fade=t=out:st=2.78:d=0.22[v{i}]')
        filters.append(''.join(f'[v{i}]' for i in range(4))+'concat=n=4:v=1:a=0[v]')
        args+=['-filter_complex',';'.join(filters),'-map','[v]']
        if not no_audio:args+=['-map','4:a','-c:a','aac','-b:a','128k','-af','afade=t=out:st=11.5:d=0.5']
        args+=['-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart','-r',str(FPS),'-t','12','-metadata',f'title=EEMON EP.{reel["number"]:02d}',str(output_dir/(reel['id']+'.mp4'))]
        subprocess.run(args,check=True,timeout=180)
    print('RENDERED',reel['id'],(output_dir/(reel['id']+'.mp4')).stat().st_size)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--only',type=int);ap.add_argument('--no-audio',action='store_true');args=ap.parse_args()
    data=json.loads((ROOT/'content/reels.json').read_text(encoding='utf8'))
    reels=data['reels'];reels=[r for r in reels if r['number']==args.only] if args.only else reels
    if not reels:ap.error('episode not found')
    for r in reels:render_one(r,ROOT/'site/media/reels',args.no_audio)
if __name__=='__main__':main()