# The World in One Image - Saturday 21 November 2026.
# Pure-stdlib Python. Draws a newspaper front page summing up the day's
# real world news and writes it to <output>/entry.png. Deterministic:
# no clock, no randomness, no network, no model calls.
# 1024x1024 PNG, 45 stories, UTC timeline, date check.

import os
import struct
import zlib

W = 1024
H = 1024

# ---- palette ---------------------------------------------------------
PAPER = (250, 247, 238)
INK = (18, 18, 18)
RED = (178, 34, 28)
NAVY = (16, 42, 78)
TEAL = (14, 92, 96)
GOLD = (184, 134, 22)
GREY = (110, 110, 108)
LIGHT = (232, 228, 218)
RULE = (160, 156, 146)

FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": (".#...", ".#...", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "&": (".###.", "#...#", "#...#", ".#.#.", "#.#..", "#.#..", ".##.#"),
    "%": ("##..#", "##.#.", "..#..", ".#...", "#..##", "#..##", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "✓": (".....", ".....", "....#", "#..#.", ".#.#.", "..#..", "....."),
}


# ---- the day's news (all reported on Sat 21 Nov 2026) ----------------
LEAD = [
    ("RUSSIA LAUNCHES ITS BIGGEST ATTACKS OF THE YEAR",
     "MORE THAN 400 DRONES AND 110 MISSILES HIT UKRAINE OVERNIGHT. "
     "EIGHT KILLED IN KYIV. MISSILES ALSO LAND IN POLAND."),
    ("AI SELL-OFF DRAGS S AND P 500 AND DOW INTO CORRECTION",
     "NASDAQ FALLS 5.3% ON FRIDAY. TECH'S WORST WEEK SINCE COVID AS "
     "DOUBT GROWS OVER AI SPENDING. $4TN WIPED OUT THIS WEEK."),
    ("UN COURT: MYANMAR COMMITTED GENOCIDE",
     "THE HAGUE HOLDS A STATE RESPONSIBLE FOR GENOCIDE FOR THE FIRST "
     "TIME, OVER THE ROHINGYA."),
]

COLS = [
    [  # column 1 - WORLD
        ("WORLD", "RUSSIA HITS UKRAINE WITH 400 DRONES, 110 MISSILES"),
        ("WORLD", "MISSILES LAND IN POLAND; TUSK CALLS IT PROVOCATION"),
        ("WORLD", "SAUDI COALITION DOWNS 3 HOUTHI MISSILES"),
        ("WORLD", "GEN Z PROTESTS SWEEP 25 EUROPEAN COUNTRIES"),
        ("WORLD", "TRUMP, XI AND PUTIN MEET IN SHENZHEN"),
        ("WORLD", "TRUMP THREATENS TAX ON AI CENTRES ABROAD"),
        ("WORLD", "TRUMP URGES NVIDIA TO REINSTATE HUANG"),
        ("WORLD", "US DECLASSIFIES MORE UFO FOOTAGE"),
        ("WORLD", "ANC FIGHTS TO HOLD SOUTH AFRICA CITIES"),
        ("WORLD", "NEPAL PM BALEN HEADS TO DELHI ON FIRST VISIT"),
        ("WORLD", "JAPAN AND INDIA HOLD FOURTH 2+2 MEETING"),
        ("WORLD", "US SANCTIONS FOUR IRANIANS OVER OIL"),
        ("WORLD", "AUSTRIA FOREIGN MINISTRY WEBSITE HACKED"),
        ("WORLD", "FBI PROBES SECOND ATTACK ON CRIME DATABASE"),
    ],
    [  # column 2 - WORLD continued + ECONOMY
        ("WORLD", "INDIAN MAN JAILED 19 YEARS OVER MURDER PLOT"),
        ("WORLD", "BOAT CAPSIZES IN NIGERIA; 4 MOURNERS KILLED"),
        ("WORLD", "ISRAELI DRONE STRIKES KILL 7 IN CENTRAL GAZA"),
        ("WORLD", "BOLSONARO HOSPITALISED UNDER HOUSE ARREST"),
        ("WORLD", "UK AND EU STRIKE THREE POST-BREXIT DEALS"),
        ("WORLD", "COP31 TALKS STALL ON CLIMATE PLAN"),
        ("WORLD", "MAGNITUDE 6.8 QUAKE SHAKES CENTRAL PERU"),
        ("WORLD", "CYCLONE AKVAN MAKES LANDFALL IN ODISHA"),
        ("WORLD", "MAMDANI SETS 2032 DATE TO CLOSE RIKERS"),
        ("WORLD", "TWO SALVADORAN SOLDIERS KILLED IN HAITI"),
        ("WORLD", "US LAWMAKERS PUSH TOUGHER AI CHIP RULES"),
        ("ECONOMY", "ANTHROPIC SHARES SLIDE AFTER RECORD IPO"),
        ("ECONOMY", "NVIDIA SHARES DROP 14% AS SEC OPENS PROBE"),
        ("ECONOMY", "RECORD SUM POURS INTO INDIA SHARES"),
    ],
    [  # column 3 - ECONOMY continued + TECH + SPORT
        ("ECONOMY", "INDIA'S NSE NOW WORLD'S 5TH-LARGEST EXCHANGE"),
        ("ECONOMY", "AFRICA CREDIT RATING AGENCY LAUNCHES"),
        ("ECONOMY", "GTA VI SETS RECORD: $3.8BN FIRST-DAY SALES"),
        ("ECONOMY", "BINANCE HACKER MOVES $600M IN ETH"),
        ("ECONOMY", "JAPAN TOURISM HITS RECORD 3.91M IN OCTOBER"),
        ("TECH", "NEURALINK IMPLANT LETS PARALYSED MAN PLAY GTA VI"),
        ("TECH", "AI CLAIMS PROOF OF 167-YEAR-OLD RIEMANN PUZZLE"),
        ("TECH", "THINKING MACHINES LAB SHIPS INKLING 2 MINI"),
        ("TECH", "OPENAI LAUNCHES MEDCHEMBENCH FOR DRUG CHEMISTRY"),
        ("TECH", "AWS UNVEILS TEXTRACT INSIGHTS FOR DOCUMENT AI"),
        ("TECH", "PANCREATIC CANCER PILL MAKES TUMOURS UNDETECTABLE"),
        ("SPORT", "KL RAHUL MAKES HISTORY IN WELLINGTON"),
        ("SPORT", "POCHETTINO TAKES OVER MAN UNITED IN FREEFALL"),
        ("SPORT", "CHHETRI REACHES 200 ISL APPEARANCES AT 42"),
    ],
]

TIMELINE = [
    ("00:00", "SAUDI COALITION DOWNS HOUTHI MISSILES"),
    ("00:55", "POCHETTINO TO TAKE MAN UTD HELM"),
    ("01:12", "DENMARK EXPELS RUSSIAN DIPLOMAT"),
    ("01:44", "COP31 DEAL STALLS"),
    ("02:27", "KRYVYI RIH: 2 DEAD, 42 HURT"),
    ("02:49", "GEN Z RALLIES IN 25 COUNTRIES"),
    ("03:21", "NEURALINK SHOWS GTA VI BY THOUGHT"),
    ("03:34", "US SANCTIONS FOUR IRANIANS"),
    ("05:21", "PERU QUAKE DAMAGE REPORTED"),
    ("05:45", "IRAQ POWER STATION FIRE KILLS 4"),
]


def draw_rect(px, x, y, w, h, col):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    r, g, b = col
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            o = base + (xx - x0) * 3
            px[o] = r
            px[o + 1] = g
            px[o + 2] = b


def draw_text(px, x, y, text, scale, col):
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is None:
            glyph = FONT["?"]
        for row in range(7):
            bits = glyph[row]
            for bit in range(5):
                if bits[bit] == "#":
                    draw_rect(px, cx + bit * scale, y + row * scale,
                              scale, scale, col)
        cx += 6 * scale
    return cx - x


def text_w(text, scale):
    return len(text) * 6 * scale


def wrap(text, scale, max_w):
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def png_bytes(px):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw.extend(px[y * stride:(y + 1) * stride])
    comp = zlib.compress(bytes(raw), 6)

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        c += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


SEC_COL = {"WORLD": NAVY, "ECONOMY": TEAL, "TECH": GOLD, "SPORT": RED}


def circle_outline(px, cx, cy, r, col):
    import math
    for deg in range(0, 360, 2):
        a = math.radians(deg)
        x = int(cx + r * math.cos(a))
        y = int(cy + r * math.sin(a))
        draw_rect(px, x, y, 2, 2, col)


def ellipse_outline(px, cx, cy, rx, ry, col):
    import math
    for deg in range(0, 360, 2):
        a = math.radians(deg)
        x = int(cx + rx * math.cos(a))
        y = int(cy + ry * math.sin(a))
        draw_rect(px, x, y, 2, 2, col)


def render(px):
    # ---- masthead ---------------------------------------------------
    draw_rect(px, 0, 0, W, 4, RED)
    title = "THE WORLD IN ONE IMAGE"
    draw_text(px, (W - text_w(title, 5)) // 2, 10, title, 5, NAVY)
    date = "SATURDAY 21 NOVEMBER 2026"
    draw_text(px, (W - text_w(date, 2)) // 2, 52, date, 2, RED)
    draw_rect(px, 16, 76, W - 32, 2, RULE)

    # ---- lead story -------------------------------------------------
    draw_text(px, 16, 86, "KYIV - UKRAINE", 2, RED)
    head = wrap(LEAD[0][0], 3, 580)
    y = 104
    for line in head:
        draw_text(px, 16, y, line, 3, INK)
        y += 24
    deck = wrap(LEAD[0][1], 2, 580)
    y += 8
    for line in deck:
        draw_text(px, 16, y, line, 2, INK)
        y += 16
    draw_rect(px, 16, 240, 580, 2, RED)

    # ---- at-a-glance panel ------------------------------------------
    draw_rect(px, 616, 84, 392, 156, NAVY)
    draw_text(px, 632, 92, "AT A GLANCE", 2, (255, 255, 255))
    circle_outline(px, 688, 172, 46, (255, 255, 255))
    ellipse_outline(px, 688, 172, 20, 46, (180, 200, 220))
    ellipse_outline(px, 688, 172, 36, 46, (180, 200, 220))
    draw_rect(px, 646, 172, 84, 2, (180, 200, 220))
    draw_rect(px, 700, 140, 6, 6, RED)
    draw_rect(px, 664, 190, 6, 6, RED)
    draw_rect(px, 712, 182, 6, 6, RED)
    stats = ["400+ DRONES", "-5.3% NASDAQ", "6.8 PERU QUAKE"]
    y = 120
    for s in stats:
        draw_text(px, 764, y, s, 2, (255, 255, 255))
        y += 32
    draw_text(px, 764, 220, "THE DAY IN NUMBERS", 1, (180, 200, 220))

    # ---- lead 2 and 3 ------------------------------------------------
    draw_rect(px, 16, 250, W - 32, 2, RULE)
    draw_text(px, 16, 258, "MARKETS", 1, RED)
    lines = wrap(LEAD[1][0], 2, 480)
    y = 272
    for line in lines:
        draw_text(px, 16, y, line, 2, INK)
        y += 16
    draw_text(px, 16, 308, "NASDAQ -5.3% FRIDAY. $4TN WIPED OUT.", 1, GREY)
    draw_text(px, 520, 258, "JUSTICE", 1, RED)
    lines = wrap(LEAD[2][0], 2, 480)
    y = 272
    for line in lines:
        draw_text(px, 520, y, line, 2, INK)
        y += 16
    draw_text(px, 520, 308, "FIRST TIME A STATE IS HELD RESPONSIBLE.", 1, GREY)
    draw_rect(px, 16, 322, W - 32, 2, RULE)

    # ---- UTC timeline -------------------------------------------------
    draw_text(px, 16, 332, "THE DAY IN UTC", 2, NAVY)
    draw_text(px, 700, 334, "ALL TIMES UTC, SAT 21 NOV 2026", 1, GREY)
    for i, (t, label) in enumerate(TIMELINE):
        col = i % 5
        row = i // 5
        x = 16 + col * 198
        y = 356 + row * 36
        draw_text(px, x, y, t, 2, RED)
        lines = wrap(label, 1, 190)
        yy = y + 16
        for line in lines[:2]:
            draw_text(px, x, yy, line, 1, INK)
            yy += 8
    draw_rect(px, 16, 428, W - 32, 2, RULE)

    # ---- story grid ---------------------------------------------------
    for ci, col in enumerate(COLS):
        x = 16 + ci * 336
        y = 440
        cur_sec = None
        for sec, headline in col:
            if sec != cur_sec:
                cur_sec = sec
                draw_rect(px, x, y, 320, 18, SEC_COL[sec])
                draw_text(px, x + 6, y + 5, sec, 1, (255, 255, 255))
                y += 24
            lines = wrap(headline, 2, 320)[:2]
            yy = y
            for line in lines:
                draw_text(px, x, yy, line, 2, INK)
                yy += 16
            y += 35
        draw_rect(px, x + 320, 440, 1, 556, LIGHT)

    # ---- footer --------------------------------------------------------
    draw_rect(px, 16, 1004, W - 32, 2, RULE)
    draw_text(px, 16, 1010, "SOURCES: BBC, REUTERS, AL JAZEERA, FT, AP, IANS",
              1, GREY)
    check = "DATE CHECK: SATURDAY 21 NOVEMBER 2026 ✓"
    draw_text(px, W - 16 - text_w(check, 1), 1010, check, 1, TEAL)


def add_grain(px):
    state = 123456789
    for i in range(W * H):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        n = (state >> 16) % 13 - 6
        if n:
            o = i * 3
            for c in range(3):
                v = px[o + c] + n
                px[o + c] = 0 if v < 0 else (255 if v > 255 else v)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    px = bytearray(W * H * 3)
    for i in range(W * H):
        px[i * 3] = PAPER[0]
        px[i * 3 + 1] = PAPER[1]
        px[i * 3 + 2] = PAPER[2]
    render(px)
    add_grain(px)
    data = png_bytes(px)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)
    print("wrote %s (entry.png, %d bytes, %dx%d)"
          % (out_dir, len(data), W, H))


if __name__ == "__main__":
    main()
