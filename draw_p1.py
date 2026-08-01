from PIL import Image, ImageDraw, ImageFilter
import random, math

random.seed(42)
W, H = 1920, 1080

img = Image.new('RGBA', (W, H), (0, 0, 0, 255))
draw = ImageDraw.Draw(img)

# 1. Sky gradient: pink-lavender → purple → deep blue
for y in range(H):
    ty = y / H
    for x in range(W):
        tx = x / W
        r = int(170 - 110*ty - 20*tx)
        g = int(140 - 100*ty - 30*tx)
        b = int(210 - 40*ty + 30*tx)
        draw.point((x, y), fill=(max(30,r), max(30,g), max(80,b), 255))

# Top-left warm glow
glow = Image.new('RGBA', (W, H), (0,0,0,0))
gd = ImageDraw.Draw(glow)
for i in range(100):
    a = int(60*(1-i/100))
    gd.ellipse([50-i*3, 30-i*2, 550+i*3, 380+i*2], fill=(255,200,220,a//6))
glow = glow.filter(ImageFilter.GaussianBlur(60))
img = Image.alpha_composite(img, glow)

# 2. Distant forest silhouettes
forst = Image.new('RGBA', (W, H), (0,0,0,0))
fd = ImageDraw.Draw(forst)
for i in range(20):
    tx = random.randint(-100, W+100)
    tw = random.randint(80, 200)
    th = random.randint(250, 500)
    ty_base = H//2 + random.randint(-50, 100)
    fd.rectangle([tx+tw//2-6, ty_base-20, tx+tw//2+6, ty_base+80], fill=(40,25,70,160))
    for _ in range(6):
        cx = tx + tw//2 + random.randint(-tw//2, tw//2)
        cy = ty_base - random.randint(50, th//2)
        cr = random.randint(50, 110)
        fd.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], fill=(50-random.randint(0,20),35-random.randint(0,10),90-random.randint(0,20),140))
forst = forst.filter(ImageFilter.GaussianBlur(12))
img = Image.alpha_composite(img, forst)

# 3. Main horizontal branch
branch_top = int(H*0.30)
branch_bot = int(H*0.70)

branch_layer = Image.new('RGBA', (W, H), (0,0,0,0))
bd = ImageDraw.Draw(branch_layer)
bd.rounded_rectangle([-60, branch_top, W+60, branch_bot], radius=100, fill=(40,58,32,255))

# Moss texture
moss_tex = Image.new('RGBA', (W, H), (0,0,0,0))
md = ImageDraw.Draw(moss_tex)
for _ in range(2000):
    mx = random.randint(-50, W+50)
    zone = random.random()
    if zone < 0.4:  # top moss (brighter)
        my = random.randint(branch_top, branch_top+70)
        mc = random.choice([(90,155,65,200),(70,135,55,190),(110,175,75,170),(60,115,45,210)])
        ms = random.randint(3,12)
    elif zone < 0.7:  # sides (medium)
        my = random.randint(branch_top+70, branch_bot-80)
        mx = random.choice([random.randint(-50,100), random.randint(W-100,W+50)])
        mc = random.choice([(45,80,38,190),(35,65,30,200)])
        ms = random.randint(4,14)
    else:  # bottom (darker)
        my = random.randint(branch_bot-90, branch_bot+10)
        mc = random.choice([(25,50,22,200),(30,55,28,190)])
        ms = random.randint(4,16)
    md.ellipse([mx-ms,my-ms,mx+ms,my+ms], fill=mc)
moss_tex = moss_tex.filter(ImageFilter.GaussianBlur(2))
branch_layer = Image.alpha_composite(branch_layer, moss_tex)

# 4. Central nest/hollow
nest_cx, nest_cy = W//2, branch_top + 55
nest_rx, nest_ry = 170, 80

nest_layer = Image.new('RGBA', (W, H), (0,0,0,0))
nd = ImageDraw.Draw(nest_layer)
# Shadow/depth
nd.ellipse([nest_cx-nest_rx-15, nest_cy-nest_ry-5, nest_cx+nest_rx+15, nest_cy+nest_ry+70], fill=(28,52,25,235))
# Inner grass (bright green bowl)
for i in range(25):
    ins = i*3
    g = min(105+i*2, 140)
    nd.ellipse([nest_cx-nest_rx+ins, nest_cy-nest_ry+ins//2, nest_cx+nest_rx-ins, nest_cy+nest_ry+65-ins],
               fill=(50+i, g, 40+i//2, 250-i*3))
# Grass blades
for _ in range(200):
    gx = nest_cx + random.randint(-nest_rx+25, nest_rx-25)
    gy = nest_cy + random.randint(-nest_ry+15, nest_ry+50)
    gh = random.randint(6,22)
    gw = random.randint(1,2)
    gc = random.choice([(85,165,55),(65,140,45),(100,180,65),(55,125,38)])
    nd.line([(gx,gy),(gx+random.randint(-4,4),gy-gh)], fill=gc+(255,), width=gw)
# Rim moss clumps
for angle in range(0, 360, 3):
    rad = math.radians(angle)
    wob = 12*math.sin(angle*3)+8*math.sin(angle*6)
    px = nest_cx + (nest_rx+wob)*math.cos(rad)
    py = nest_cy + (nest_ry+wob*0.5)*math.sin(rad)
    ms = random.randint(6,16)
    mc = random.choice([(65,125,48,240),(82,148,58,230),(52,98,38,250),(95,158,65,220)])
    nd.ellipse([px-ms,py-ms,px+ms,py+ms], fill=mc)
nest_layer = nest_layer.filter(ImageFilter.GaussianBlur(1))
branch_layer = Image.alpha_composite(branch_layer, nest_layer)

# Nest soft glow
ng = Image.new('RGBA', (W, H), (0,0,0,0))
ngd = ImageDraw.Draw(ng)
for i in range(50):
    a = int(30*(1-i/50))
    ngd.ellipse([nest_cx-nest_rx-30+i*4, nest_cy-nest_ry-20+i*2,
                 nest_cx+nest_rx+30-i*4, nest_cy+nest_ry+40-i*2], fill=(130,210,110,a))
ng = ng.filter(ImageFilter.GaussianBlur(25))
branch_layer = Image.alpha_composite(branch_layer, ng)

# 5. Air plants (bromeliads)
brom = Image.new('RGBA', (W, H), (0,0,0,0))
brd = ImageDraw.Draw(brom)
brom_pos = [
    (nest_cx-nest_rx-70, branch_top+25),
    (nest_cx+nest_rx+90, branch_top+20),
    (280, branch_top+35),
    (W-320, branch_top+30),
    (nest_cx-40, branch_top-5),
    (nest_cx+nest_rx+200, branch_top+40),
]
for bcx, bcy in brom_pos:
    n = random.randint(7,12)
    for li in range(n):
        ang = (li/n)*360 + random.randint(-15,15)
        rad = math.radians(ang)
        llen = random.randint(18,45)
        lx = bcx + llen*math.cos(rad)
        ly = bcy + llen*0.5*math.sin(rad)
        lc = random.choice([(28,75,38,230),(38,95,48,220),(22,65,32,240)])
        brd.line([(bcx,bcy),(lx,ly)], fill=lc, width=random.randint(2,5))
brom = brom.filter(ImageFilter.GaussianBlur(0.5))
branch_layer = Image.alpha_composite(branch_layer, brom)

# 6. Mushrooms
def draw_shroom(layer, cx, cy, cap_r, stem_h):
    d = ImageDraw.Draw(layer)
    sw = max(3, cap_r//3)
    d.rounded_rectangle([cx-sw, cy-stem_h, cx+sw, cy+3], radius=sw//2, fill=(210,235,228,245))
    d.ellipse([cx-cap_r, cy-cap_r-stem_h+cap_r//4, cx+cap_r, cy-stem_h+cap_r//4+3], fill=(45,175,195,250))
    d.ellipse([cx-cap_r//2-2, cy-cap_r-stem_h+cap_r//4+3, cx-cap_r//4+2, cy-cap_r*2//3-stem_h+cap_r//4+8],
              fill=(210,255,255,170))
    return layer

# Mushroom glow
mglow = Image.new('RGBA', (W, H), (0,0,0,0))
mgd = ImageDraw.Draw(mglow)

# Left cluster
shroom_layer = Image.new('RGBA', (W, H), (0,0,0,0))
left_x, left_y = nest_cx-nest_rx-50, branch_top+45
left_shrooms = []
for _ in range(16):
    mx = left_x + random.randint(-60, 35)
    my = left_y + random.randint(-8, 25)
    mr = random.randint(7, 20)
    mh = random.randint(14, 32)
    left_shrooms.append((mx,my,mr,mh))
    draw_shroom(shroom_layer, mx, my, mr, mh)
    gr = mr*3
    for i in range(15):
        a = int(25*(1-i/15))
        mgd.ellipse([mx-gr+i*3, my-mh-gr//2+i*2, mx+gr-i*3, my-mh+gr//2-i*2], fill=(75,215,225,a))

# Right 3 large
right_shrooms = [
    (nest_cx+nest_rx+50, branch_top+40, 30, 42),
    (nest_cx+nest_rx+100, branch_top+30, 36, 52),
    (nest_cx+nest_rx+155, branch_top+42, 26, 38),
]
for mx,my,mr,mh in right_shrooms:
    draw_shroom(shroom_layer, mx, my, mr, mh)
    gr = mr*3
    for i in range(15):
        a = int(28*(1-i/15))
        mgd.ellipse([mx-gr+i*3, my-mh-gr//2+i*2, mx+gr-i*3, my-mh+gr//2-i*2], fill=(75,215,225,a))

# Gills under right mushrooms
sd = ImageDraw.Draw(shroom_layer)
for mx,my,mr,mh in right_shrooms:
    for gx in range(int(mx-mr+6), int(mx+mr-6), 5):
        sd.line([(gx,my-mh+mr//4),(gx,my-mh+mr//4+7)], fill=(225,255,250,140), width=1)

mglow = mglow.filter(ImageFilter.GaussianBlur(14))
branch_layer = Image.alpha_composite(branch_layer, mglow)
branch_layer = Image.alpha_composite(branch_layer, shroom_layer)

# 7. Hanging Spanish moss
hmoss = Image.new('RGBA', (W, H), (0,0,0,0))
hmd = ImageDraw.Draw(hmoss)
hang_pts = [
    (nest_cx-nest_rx-25, branch_top+65),
    (nest_cx-nest_rx+25, branch_top+75),
    (nest_cx+nest_rx-5, branch_top+70),
    (nest_cx+nest_rx+50, branch_top+60),
    (380, branch_top+85),
    (W-420, branch_top+80),
    (nest_cx-180, branch_bot-15),
    (nest_cx+160, branch_bot-10),
    (nest_cx+nest_rx+120, branch_bot-20),
]
for sx,sy in hang_pts:
    for _ in range(random.randint(3,7)):
        cx,cy = sx+random.randint(-15,15), sy
        slen = random.randint(70,220)
        for __ in range(slen//4):
            nx = cx+random.randint(-2,2)
            ny = cy+4
            g = random.randint(145,195)
            hmd.line([(cx,cy),(nx,ny)], fill=(g,g,g-8,random.randint(90,170)), width=random.randint(1,2))
            cx,cy = nx,ny
hmoss = hmoss.filter(ImageFilter.GaussianBlur(0.5))
branch_layer = Image.alpha_composite(branch_layer, hmoss)

img = Image.alpha_composite(img, branch_layer)

# 8. Foreground leaves
leaves = Image.new('RGBA', (W, H), (0,0,0,0))
ld = ImageDraw.Draw(leaves)

def leaf(d, cx, cy, sz, ang, dark=(8,32,16), light=(28,72,36)):
    rad = math.radians(ang)
    pts = []
    for a in range(0,360,8):
        ar = math.radians(a)
        x = cx + sz*0.4*math.cos(ar)*math.cos(rad) - sz*0.9*math.sin(ar)*math.sin(rad)
        y = cy + sz*0.4*math.cos(ar)*math.sin(rad) + sz*0.9*math.sin(ar)*math.cos(rad)
        pts.append((x,y))
    d.polygon(pts, fill=dark+(235,))
    ex = cx - sz*0.85*math.sin(rad)
    ey = cy + sz*0.85*math.cos(rad)
    d.line([(cx,cy),(ex,ey)], fill=light+(190,), width=max(1,sz//10))

for _ in range(22):
    lx = random.randint(-60, W+60)
    ly = random.randint(-100, 130)
    ls = random.randint(35, 110)
    la = random.randint(-35,35)+180
    dc = random.choice([(6,28,14),(10,40,19),(4,22,11)])
    lc = random.choice([(25,68,34),(35,82,42)])
    leaf(ld, lx, ly, ls, la, dc, lc)

for _ in range(18):
    lx = random.randint(-60, W+60)
    ly = random.randint(H-160, H+70)
    ls = random.randint(45, 130)
    la = random.randint(-25,25)
    dc = random.choice([(6,28,14),(4,22,11),(10,38,18)])
    lc = random.choice([(22,62,32),(30,75,38)])
    leaf(ld, lx, ly, ls, la, dc, lc)
leaves = leaves.filter(ImageFilter.GaussianBlur(1))
img = Image.alpha_composite(img, leaves)

# 9. Particles
parts = Image.new('RGBA', (W, H), (0,0,0,0))
pd = ImageDraw.Draw(parts)

# Dandelion seeds
for _ in range(70):
    px,py = random.randint(50,W-50), random.randint(50,H-50)
    ps = random.randint(2,4)
    br = random.randint(190,255)
    pd.ellipse([px-ps,py-ps,px+ps,py+ps], fill=(br,br,min(255,br+15),random.randint(160,230)))
    for h in range(5):
        ang = (h/5)*360+random.randint(-20,20)
        r = math.radians(ang)
        pd.line([(px,py-ps),(px+ps*2*math.cos(r),py-ps-ps*2+ps*math.sin(r))],
                fill=(255,255,225,random.randint(30,80)), width=1)

# Cyan fireflies
for _ in range(55):
    px,py = random.randint(0,W), random.randint(0,H)
    ps = random.randint(1,3)
    pd.ellipse([px-ps,py-ps,px+ps,py+ps], fill=(140,225,255,random.randint(160,250)))

# Golden sparks (lower right)
gold_glow = Image.new('RGBA', (W, H), (0,0,0,0))
ggd = ImageDraw.Draw(gold_glow)
for _ in range(45):
    px = random.randint(W-480, W-120)
    py = random.randint(H-280, H-60)
    ps = random.randint(1,3)
    pd.ellipse([px-ps,py-ps,px+ps,py+ps], fill=(255,200+random.randint(0,50),60+random.randint(0,80),random.randint(190,255)))
for i in range(35):
    a = int(40*(1-i/35))
    ggd.ellipse([W-430-i*7, H-230-i*4, W-170+i*7, H-90+i*4], fill=(255,175,50,a))
gold_glow = gold_glow.filter(ImageFilter.GaussianBlur(25))
parts = Image.alpha_composite(parts, gold_glow)
parts = parts.filter(ImageFilter.GaussianBlur(0.5))
img = Image.alpha_composite(img, parts)

# Ambient glow near mushrooms
amb = Image.new('RGBA', (W, H), (0,0,0,0))
ad = ImageDraw.Draw(amb)
for i in range(60):
    a = int(20*(1-i/60))
    ad.ellipse([left_x-130-i*2, left_y-90-i, left_x+80+i*2, left_y+70+i], fill=(75,200,215,a))
    ad.ellipse([nest_cx+nest_rx+20-i*2, branch_top+20-i, nest_cx+nest_rx+200+i*2, branch_bot-50+i], fill=(75,200,215,a))
amb = amb.filter(ImageFilter.GaussianBlur(35))
img = Image.alpha_composite(img, amb)

# Save
out = img.convert('RGB')
out.save('/workspace/starlight-carnival/assets/shadow-jungle-sloth.jpg', 'JPEG', quality=95)
print(f"Done! {out.size}")
