from typing import Optional
from core.az_terminal import TERM_WIDTH, TERM_WIDTH, PR, PR_BR, PR_LN, PR_MID, PR_NEXT, STY, TERM_WIDTH_FULL, ansi, ansiHex, bgHex, getStrTable, vlen
from utils.util_json import render_json
from collections.abc import Mapping, Sequence
__all__ = [name for name in dir() if not name.startswith("_")]




"""
  ✖  ✔  ⚠︎  ✦  𝒊  ☢  🛈  ★  ✎ 🗐 ☑ ➤ 🕊 ▶
  「  」  ⌞  ⌝
  ⚠️  ✔️  ☑️  ❌  ♻️
  🕛🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚
  ◝◟◞◜◝◟  ◡ ○  ◴◷◶◵ ◐◓◑◒ ◴◷◶◵  ○ ◡  ◞◜◝◟◞◜  ◠ ○  ◶◴◵◷ ◑◒◐◓ ◶◴◵◷  ○ ◠ 
  

▏                      ▕    24

▏__0.5 /__0.5KB▕


▏              ▕

▏99.9% ████████▕    16

▏ ᴩʀᴏᴄ ᴄᴏᴍᴩʟᴇᴛᴇ ▕    16
◢ ◣ ◤ ◥
◐◑◒◓◕◴ ◵ ◶ ◷ ◧ ◩ ◳ ◲	◱	◰ 
█
▉
▊
▋
▌
▍
▎
▏


"""




# def PR_EXPORT_INIT(head: str, color: str, name: str, state: str = "pending"):
#     PR(f"{state}...", pre=STY(head, f"{color}", 'bold') + f" {name}")

# def PR_LN_FUNC(funcName: str, text = "", *, ic: str = "", depth = 0, ln = False):
#     d = ((" "*depth) + "⮡  ") if depth else ""
#     PR_MOVE(f"{STY(d, 'C')}{STY(funcName, '#219ffb')}", STY(str(text), '#00edff'), ic=ic, ln=ln)

def PR_PROC_INIT(procName: str, text = "", *, ic: str = "📚", ln = False): 
    PR_EXPORT_INIT(f"{ic} {procName}", "#ffd599", "", STY(str(text), '#f4ff5c'))
    # PR_MOVE(f"{STY(procName, '#ffd599')}", STY(str(text), '#f4ff5c'), ic=ic, ln=False)
    
def PR_PROC_DONE(procName: str, data, *, text = "items", ic: str = "📚"): 
    head = f"{ic} {procName}"
    color = "#8be88b"
    PR_LN(getStr_COUNT(color, data) + STY(" ✔  ", color) + text, pre=STY(head, color, 'bold'))
    # PR_EXPORT(f"{ic} {procName}", "#8be88b", "", STY(text, 'G'), data) #📔📚🗃️📦
    # PR_MOVE(f"{STY(procName, '#8be88b')}", STY(str(text), '#f4ff5c'), ic=ic, ln=True)

def PR_FUNC(funcName: str, text = "", *, ic: str = "", depth = 0, sup = False, ln = False):
    b = "━┯ " if sup else "━━ "
    d = (("  "*abs(depth)) + (f"┕{b}" if depth < 0 else f"┝{b}")) if depth else ""
    sty_name = ['#70cfef' if depth else '#a0efff'] # 40bfff 9cefff
    if depth == 0: sty_name.append('bold')
    # d = (("  " if abs(depth)>0 else "") + ("┆ "*abs(depth)) + (f"┕{b}" if depth < 0 else f"┝{b}")) if depth else ""
    PR_MOVE(f"{STY(d, '#70cfef80')}{STY(funcName, *sty_name)}", STY(str(text), '#70cfef'), ic=ic, ln=ln)

def PR_MOVE(textFrom, textTo, *, ic: str = "", ln = False): # ➡ ❯❯ ➜ ➔ ➟  
    c1 = f"{STY(ic, 'Y') if ic !='' else ''}  {STY(str(textTo), 'W')}".strip()
    pre = (STY(str(textFrom), 'W'))
    if ln: PR_LN(c1, pre=pre)
    else: PR(c1, pre=pre)


def PR_INIT(text, head: Optional[str] = None):
    pre = STY(str(head), 'WH', 'bold') if head is not None else None
    PR_LN(STY(str(text), 'W'), pre=pre)


def PR_TEMP(text, head: Optional[str] = None):
    pre = STY(str(head), 'WH', 'bold') if head is not None else None
    PR(STY(str(text), 'W'), pre=pre)
    
def getStr_COUNT(color: str, data, l: str = '[', r: str = ']'):
    if isinstance(data, dict): return STY(STY(l, f"{color}20") + STY(f"{len(data.keys())}", 'bold') + STY(r, f"{color}20"), 7)
    elif isinstance(data, list): return STY(STY(l, f"{color}20") + STY(f"{len(data)}", 'bold') + STY(r, f"{color}20"), 7)
    elif isinstance(data, int): return STY(STY(l, f"{color}20") + STY(f"{data}", 'bold') + STY(r, f"{color}20"), 7)
    return STY(STY(l, f"{color}20") + STY(f"???", 'bold') + STY(r, f"{color}20"), 7)


def strBrack(text, l: str, r: str, *, cb='#8c8680', wrap=True, rep=False):
    out = str(text)
    if rep: out = out.replace(l, STY(l, cb)).replace(r, STY(r, cb))
    if wrap: out = STY(l, cb) + out + STY(r, cb)
    return out



def strData(data, text: str = "", *, arw: str = "", w: str = 8, ic: str = "", c: str = '#64a3ff'):
    cg = '#8c8680'
    cs = '#DBDEDE' # '#ebddcd'
    cd = cg # f"{c}10" #204080
    arrow = ""
    if text and arw.lower() == "r": arrow = STY(f"➡  ", cg)
    if text and arw.lower() == "l": arrow = STY(f"⬅  ", cg)
    if text and arw.lower() == "u": arrow = STY(f"⬆  ", cg)
    if text and arw.lower() == "d": arrow = STY(f"⬇  ", cg)
    if text and arw.lower() == "x": arrow = STY(f"✖  ", cg) # ✖ ✘
    if text and arw.lower() == "c": arrow = STY(f"✔  ", cg)
    if text and arw.lower() == "w": arrow = STY(f"⚠︎  ", cg)
    if text and arw.lower() == "s": arrow = STY(f"✦  ", cg)
    if text and arw.lower() == "k": arrow = STY(f"⚿  ", cg)
    if text and arw.lower() == "f": arrow = STY(f"⛶  ", cg)
    if text and arw.lower() == "b": arrow = STY(f"⬚  ", cg) # ⯀ ⬚ ⛾ ⯐ ⛶
    # if arw.lower() == "total": arrow = STY(f" ᴛᴏᴛᴀʟ  ", c)
    if arw.lower() == "none": arrow = ""
    icon = STY(f"{ic}  ", c) if ic else ""
    suffix = icon + (STY(text, 'reset') if text else "")

    def _out(s: str, l: str = '[', r: str = ']'): 
        val = STY(s, 'bold', cs) if s != "0" else STY(s, cd)
        return STY(STY(l, cd) + val + STY(r, cd), w) + arrow + suffix
    
    if isinstance(data, dict): return _out(f"{len(data.keys())}", '{', '}')
    elif isinstance(data, list): return _out(f"{len(data)}", '[', ']')
    elif isinstance(data, int): return _out(f"{data}", '(', ')')
    elif isinstance(data, str): return STY(f"{data}", w) + arrow + suffix
    return STY(f"???", w) + arrow + suffix

def strDataIn(data, text: str = "", *, w: str = 7): strData(data, text, arw="l", w=w)
def strDataOut(data, text: str = "", *, w: str = 7): strData(data, text, arw="r", w=w)


def PR_EXPORT_INIT(head: str, color: str, name: str, state: str = "pending"):
    PR(state, pre=STY(head, color, 'bold') + f" {name}")
    
def PR_EXPORT(head: str, color: str, name: str, path: str, data, l: str = '[', r: str = ']'):
    # PR_LN(strDataOut(data, path), pre=STY(head, color, 'bold') + f" {name}")
    PR_LN(getStr_COUNT(color, data, l, r) + STY(" ➡  ",'#8c8680')+path, pre=STY(head, color, 'bold') + f" {name}")
    
def PR_IMPORT(head: str, color: str, name: str, path: str, data, l: str = '[', r: str = ']'):
    # PR_LN(strDataOut(data, path), pre=STY(head, color, 'bold') + f" {name}")
    PR_LN(getStr_COUNT(color, data, l, r) + STY(" ⬅  ",'#8c8680')+path, pre=STY(head, color, 'bold') + f" {name}")


def PR_LN_NOTICE(text, notes = None, *, head: Optional[str] = "NOTICE"):
    # PR_NEXT()
    PR_LN(pre=False, suf=False)
    hOut = f"  ⚠︎  {str(head)}  "
    w = TERM_WIDTH() - len(hOut)
    PR_LN(STY(hOut + ("▚" * w), 'BG_R', 'bold', '#FFF'), pre=False, suf=False)
    print("\n" + STY(str(text), '#FFF', 'bold'))
    if notes != None: print(f"\n{str(notes)}\n" + STY((" " * (len(hOut)-1)) + ("▚" * w), 'BG_R', 'bold', '#FFF') + "\n")
    # time.sleep(2)

def PR_LN_WARN(text, *, head: Optional[str] = "WARN", defTo = None):
    pre = STY(f"  ⚠︎  {str(head)}  ", 'BG_Y', 'bold', '#000') if head is not None else None
    PR_BR(STY(str(text), 'YH'), pre=pre)
    return defTo

def PR_LN_ERROR(text, e = None, *, head: Optional[str] = "FAIL", defTo = None):
    pre = STY(f"  ✖  {str(head)}  ", 'BG_R', 'bold') if head is not None else None
    PR_BR(STY(f"{str(text)}", 'italic', 'R'), pre=pre)
    if e != None: print(STY(str(e), 'RH'))
    return defTo

def PR_DONE(text, head: Optional[str] = '✦ EXPORTED'):
    pre = STY(str(head), 'bold', 'C') if head is not None else None
    PR_BR(STY(str(text), 'C'), pre=pre)

def PR_COMPLETE(text: str, head: str = '✔  COMPLETE'):
    pre = STY(str(head), 'CH', 'bold') if head is not None else None
    PR_NEXT()
    PR_BR(STY(text, 'CH', 'italic') , pre=pre, suf="")




def PR_DEBUG_KEYS(obj, text: str = "Keys", *, head: str = "DEBUG",
                  color: str = "#339955", preText: str = "", sufText: str = ""):
    w = TERM_WIDTH()
    col = [ ansiHex('#ccffdd'), ansiHex('#88ffaa'), ansiHex(color) ]
    sl1 = col[2] + ('█'*8) + ansi('reset')
    sl2 = col[2] + ('█'*w) + ansi('reset')
    start = col[2] + ('▄'*w) + ansi('reset')
    close = col[2] + ('▀'*w) + ansi('reset')
    txt = f"{col[1] + ansi('bold') + head + ansi('reset')}  {(col[0] + str(text) + ansi('reset')) if text else ''}".strip()
    mid = f"{sl1}  {txt}  "

    # Collect keys from obj or list of objs, preserving order and de-duplicating
    def _iter_keys(o):
        if isinstance(o, Mapping):
            for k in o.keys(): yield k
        elif isinstance(o, Sequence) and not isinstance(o, (str, bytes, bytearray)):
            for item in o:
                if isinstance(item, Mapping):
                    for k in item.keys(): yield k

    # Ordered, unique keys
    seen = set()
    keys = []
    for k in _iter_keys(obj):
        if k not in seen:
            seen.add(k)
            keys.append(k)

    PR_NEXT()
    PR_LN(f"{start}" + ansi('reset'), pre=False, suf=False)
    PR_LN(f"{mid}{sl2}", pre=False, suf=False)

    if preText: print(col[1] + preText + ansi('reset'))
    if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray)): print(col[0] + f"OBJECT IS LIST" + ansi('reset'))
    if isinstance(obj, Mapping): print(col[0] + f"OBJECT IS DICT" + ansi('reset'))
    if keys:
        for k in keys: print(col[0] + f"- {k}" + ansi('reset'))
    else: print(col[0] + "<no keys>" + ansi('reset'))

    if sufText: print(col[1] + sufText + ansi('reset'))

    PR_LN(f"{mid}{sl2}", pre=False, suf=False)
    PR_LN(f"{close}" + ansi('reset'), pre=False, suf=False)





def PR_DEBUG_OBJ(obj, text: str = "Object", 
                 *, 
                 head: str = "DEBUG", 
                 color: str = "#339955", color2: str = "#88ffaa", 
                 preText: str = "", sufText: str = ""):
    w = TERM_WIDTH()
    col = [ ansiHex('#ccffdd'), ansiHex(color2), ansiHex(color) ]
    sl1 = col[2] + ('█'*8) + ansi('reset')
    sl2 = col[2] + ('█'*w) + ansi('reset')
    start = col[2] + ('▄'*w) + ansi('reset')
    close = col[2] + ('▀'*w) + ansi('reset')
    txt = f"{col[1] + ansi('bold') + head + ansi('reset')}  {(col[0] + str(text) + ansi('reset')) if text else ''}".strip()
    mid = f"{sl1}  {txt}  "
    PR_NEXT()
    PR_LN(f"{start}" + ansi('reset'), pre=False, suf=False)
    PR_LN(f"{mid}{sl2}", pre=False, suf=False)
    if preText: print(col[1] + preText + ansi('reset'))
    print(col[0] + render_json(obj, oneLineLenMax=w) + ansi('reset'))
    if sufText: print(col[1] + sufText + ansi('reset'))
    PR_LN(f"{mid}{sl2}", pre=False, suf=False)
    PR_LN(f"{close}" + ansi('reset'), pre=False, suf=False)


def PR_DEBUG(text, head: str = "", *, color: str = "#88ffaa"):
    PR(f"", pre=False, suf=False) # ┃╱╱╱╱┃ 
    PR_LN(f"{STY(('████  ' + str(head)).strip(), 'bold', color+'80')}  {STY(str(text), color)}", pre=False, suf=False)



def PR_DEBUG_TABLE(*text, sep="┃", align="<", head="", color="#88ffaa", colors=None, ratio=None) -> str:
    if not text: return
    pre = STY(('████' + str(head)), 'bold') # ▌▐
    w = TERM_WIDTH()
    mid = getStrTable(*text, w=w, gap=2, pre=pre, sep=sep, suf="┃", align=align, color=color, colors=colors, ratio=ratio)
    PR(f"", pre=False, suf=False) # ┃╱╱╱╱┃ 
    PR_LN(mid, pre=False, suf=False)




def PRINT_DEPS(text: str):
    line = STY(('━'*4), '#ff7733')
    midh = f"{STY('COPYING ▶ ', 'bold', '#ffbb99')}"
    midt = f"{STY(str(text), 'W')}"
    PR_LN(f"", pre=False, suf=False)
    PR_LN(f"{line}  {midh + midt}  {line*128}", pre=False, suf=False)
    print("")


def getPreColors(text: str) -> list:
    dk = 'ac'
    colRaw = ['#b8b8ff', '#8585ff', f"8585ff{dk}"] # 240 
    # colRaw = ['#f5baf5', '#cc49cc', f"ad85ff{dk}"] # 300 
    colUnk = ['#f5bae1', '#f50aa6', f"f50aa6{dk}"] # 320 
    colDeps = ['#ffbb99', '#ff7733', f"ff7733{dk}"] # 20
    colInit = ['#ffee99', '#ffdd33', f"ffdd33{dk}"] # 50
    # colInit = ['#a6f57f', '#58f50a', f"58f50a{dk}"] # 100
    colProc = ['#7ff5ce', '#0af5a6', f"0af5a6{dk}"] # 160
    colType = ['#7fcef5', '#0aa6f5', f"0aa6f5{dk}"] # 200
    colTemp = ['#b8b8b8', '#8f8f8f', f"8f8f8f{dk}"] # 300 
    
    col = colUnk
    if text.startswith('raw'): col = colRaw
    if text.startswith('api'): col = colRaw
    if text.startswith('dep'): col = colDeps
    if text.startswith('init'): col = colInit
    if text.startswith('proc'): col = colProc
    if text.startswith('type'): col = colType
    if text.startswith('temp'): col = colTemp
    return col



def PRINT_RUN(text: str):
    cols = getPreColors(text)
    col = [ansiHex(cols[0]), ansiHex(cols[1]), ansiHex(cols[2])]
    b = col[1] + '┃' + ansi('reset') # █ ┃ │ ║ 
    sl1 = col[1] + ('╱'*4) + ansi('reset')
    sl2 = col[1] + ('╱'*256) + ansi('reset')
    run = col[0] + ansi('bold') + 'RUNNING ▶ ' + ansi('reset')
    mid = f"{sl1}  {run + STY(str(text), 'W')}  "

    print("\n")
    PR_LN(f"", pre=False, suf=False)
    PR_LN(f"{b}{col[2] + ('╱'*256) + ansi('reset')}", pre=False, suf=False)
    PR_LN(f"{b}{mid}{sl2}", pre=False, suf=False)
    PR_LN(f"{b}{col[2] + ('╱'*256) + ansi('reset')}", pre=False, suf=False)
    print("\n")



def PR_FINAL_GEN_COMPANION():
    # bd = ansiHex('2ec825') + '┃' + ansi('reset')
    # lh = ansiHex('39fa2e') + '╱'*(TERM_WIDTH()-2) + ansi('reset')
    # ld = ansiHex('23961c') + '╱'*(TERM_WIDTH()-2) + ansi('reset')
    # print(ansiHex('39fa2e') + "\n\n" + bd + lh + bd + "\n" + bd + ld + bd + ansi('reset'))
    bd = ansiHex('29abcc') + '┃' + ansi('reset')
    lh = ansiHex('33d6ff') + '╱'*(TERM_WIDTH()-2) + ansi('reset')
    ld = ansiHex('1f8199') + '╱'*(TERM_WIDTH()-2) + ansi('reset')
    print(ansiHex('33d6ff') + "\n\n" + bd + lh + bd + "\n" + bd + ld + bd + ansi('reset'))
    # print(ansiHex('16c60c') + ansi('bold') + f"\n ★ ★ ★   G E N   C O M P L E T E   ★ ★ ★" + ansi('reset'))
    # DUMP_LOGS()

def PR_INIT_GEN_COMPANION():
    bd = ansiHex('dac82c') + '┃' + ansi('reset') # │ ║ █ ╱
    lh = ansiHex('FFE710') + '╱'*(TERM_WIDTH()-2) + ansi('reset')
    ld = ansiHex('C9A101') + '╱'*(TERM_WIDTH()-2) + ansi('reset')
    print(ansiHex('FFE710') + "\n\n" + bd + lh + bd + "\n" + bd + ld + bd)
    s2 = ' ' * int(max(0, TERM_WIDTH()-108) * 0.5)
    s = ' ' * int(max(0, TERM_WIDTH()-80) * 0.5)
    L2 = ansiHex('faf5b4')
    L1 = ansiHex('faf16e')
    M0 = ansiHex('d6cb2b')
    D1 = ansiHex('8f871d')
    D2 = ansiHex('47440e')
    # PR_LN(ansi('Y') + ('╱'*256) + ansi('reset'), pre=False, suf=True)
    # PR_LN(ansi('Y') + ('╱'*256) + ansi('reset'), pre=False, suf=True)
    # SET_PRE(True)
    print('\033[93m')
    print(f"{s+L2} ▄▄▄▄  ▄▄▄▄▄ ▄▄  ▄▄     ▄▄▄▄  ▄▄▄▄  ▄▄   ▄▄ ▄▄▄▄▄   ▄▄▄▄  ▄▄  ▄▄ ▄▄  ▄▄▄▄  ▄▄  ▄▄ ")
    print(f"{s+L1}██     ██    ██▄ ██    ██    ██  ██ ██▄ ▄██ ██  ██ ██  ██ ██▄ ██ ██ ██  ██ ██▄ ██ ")
    print(f"{s+M0}██ ███ ████  ██████ ██ ██    ██  ██ ███████ ██▄▄█▀ ██▄▄██ ██████ ██ ██  ██ ██████ ")
    print(f"{s+D1}██  ██ ██    ██ ▀██    ██    ██  ██ ██ ▀ ██ ██     ██  ██ ██ ▀██ ██ ██  ██ ██ ▀██ ")
    print(f"{s+D2} ▀▀▀▀  ▀▀▀▀▀ ▀▀  ▀▀     ▀▀▀▀  ▀▀▀▀  ▀▀   ▀▀ ▀▀     ▀▀  ▀▀ ▀▀  ▀▀ ▀▀  ▀▀▀▀  ▀▀  ▀▀ ")
    
    a = ansiHex('00cc88') + "▄▄" + M0
    b = ansiHex('00cc88') + "▀▀" + L1
    c = ansiHex('009e6a') + "▄▄▄" + L2
    d = ansiHex('00cc88') + "███" + L2
    print(f"{s2+D2}                                                   ▄▄▄▄▄▄                                                   ")
    print(f"{s2+D1}▀█████████████▀████████▀████████▀████████▄    ▄▄████████████▄▄    ▄████████▀████████▀████████▀█████████████▀")
    print(f"{s2+M0}  ▀█████████▄   ▄████▄   ▄████▄   ▄███████   ██████████████████   ███████▄   ▄████▄   ▄████▄   ▄█████████▀  ")
    print(f"{s2+M0}    ▀████████▄█▄██████▄█▄██████▄█▄█████████  ███████▀{a}▀███████  █████████▄█▄██████▄█▄██████▄█▄████████▀    ")
    print(f"{s2+L1}                                            ▄███████▄{b}▄███████▄                                            ")
    print(f"{s2+L2}       ▀█████████████████████████████████▀  ██▀{c} ██████ {c}▀██  ▀██████████████████████████████████▀      ")
    print(f"{s2+L2}         ▀█████████████████████████████▀  ▄███ {d} ██████ {d} ███▄  ▀██████████████████████████████▀        ")
    print(f"{s2+L1}                                          ▀████▄▄▄████████▄▄▄████▀                                          ")
    print(f"{s2+M0}                    ▀███████████████████▄   ▀███████▀  ▀███████▀   ▄███████████████████▀                    ")
    print(f"{s2+M0}                      ▀███████████████████▄      ███▄██▄███      ▄███████████████████▀                      ")
    print(f"{s2+D1}                                                 ▀████████▀                                                 ")
    print(f"{s2+D2}                                                    ▀▀▀▀                                                    ")

#     print("""\033[93m\n
# {s} ▄▄▄▄  ▄▄▄▄▄ ▄▄  ▄▄     ▄▄▄▄  ▄▄▄▄  ▄▄   ▄▄ ▄▄▄▄▄   ▄▄▄▄  ▄▄  ▄▄ ▄▄  ▄▄▄▄  ▄▄  ▄▄ 
# {s}██     ██    ██▄ ██    ██    ██  ██ ██▄ ▄██ ██  ██ ██  ██ ██▄ ██ ██ ██  ██ ██▄ ██ 
# {s}██ ███ ████  ██████ ██ ██    ██  ██ ███████ ██▄▄█▀ ██▄▄██ ██████ ██ ██  ██ ██████ 
# {s}██  ██ ██    ██ ▀██    ██    ██  ██ ██ ▀ ██ ██     ██  ██ ██ ▀██ ██ ██  ██ ██ ▀██ 
# {s} ▀▀▀▀  ▀▀▀▀▀ ▀▀  ▀▀     ▀▀▀▀  ▀▀▀▀  ▀▀   ▀▀ ▀▀     ▀▀  ▀▀ ▀▀  ▀▀ ▀▀  ▀▀▀▀  ▀▀  ▀▀ 
# \033[0m""")
    
#     print("""\033[93m\n
                  
                  
# ▄▀▀▀  █▀▀▀ █▄ █   ▄▀▀▀
# █  ▀█ █▀▀  █ ▀█ ▀ █     
#  ▀▀▀  ▀▀▀▀ ▀  ▀    ▀▀▀ 
# \033[0m""")





def ERS(text: str): return STY(text,'#fffdfc', 'bold')+ansiHex('ffddcc')
def ERR(text: str):
    b = "" # ansiHex('ff0000') + '┃' + ansi('reset') # ╱ │ ║ ▚
    i = f"\n{b}{ansiHex('aa0000') + ('▀'*TERM_WIDTH()) + ansi('reset')}" # ff6655
    l = f"\n{b}{ansiHex('aa0000') + ('━'*TERM_WIDTH()) + ansi('reset')}" # ff6655
    o = f"\n{b}{ansiHex('ff0000')} ✖  {ansi('reset')+ansiHex('ffddcc')}{text}"
    print("\n")
    print(f"\n{i}{o}{l}{ansi('reset')}")
    print(ansiHex('ff5555'))
    return (f"\n{i}{o}{l}{ansi('reset')}\n")
