import os
import re, subprocess, atexit
from datetime import datetime
import traceback
from typing import Optional
from core.az_terminal import PR_BR, PR_LN, STY, TERM_WIDTH, ansi, ansiHex, strip_ansi, termTAG

TIMEISO_START: dict = { "time": datetime.now().isoformat() }
TIMEISO_FINAL: dict = { "time": datetime.now().isoformat() }

def set_TIMEISO_START(): TIMEISO_START['time'] = datetime.now().isoformat()
def set_TIMEISO_FINAL(): TIMEISO_FINAL['time'] = datetime.now().isoformat()


EXITLOGS_INFO: list[dict] = []
EXITLOGS_WARN: list[dict] = []
EXITLOGS_FAIL: list[dict] = []
EXITLOGS_ERROR: list[dict] = []





def push_EXITLOGS_INFO(entry: dict): EXITLOGS_INFO.append(entry)
def push_EXITLOGS_WARN(entry: dict): EXITLOGS_WARN.append(entry)
def push_EXITLOGS_FAIL(entry: dict): EXITLOGS_FAIL.append(entry)
def push_EXITLOGS_ERROR(entry: dict): EXITLOGS_ERROR.append(entry)

def _ERS(text: str): return STY(text,'#fffdfc', 'bold')+ansiHex('ffddcc')

def _ERR_I():
    i = f"{ansiHex('aa0000') + ('▀'*(TERM_WIDTH()-4)) + ansi('reset')}" # ff6655
    return (f"{i}{ansi('reset')}")

def _ERR_L(text: str):
    l = f"{ansiHex('ff0000')} ✖  {ansi('reset')+ansiHex('ffddcc')}{text}"
    return (f"{l}{ansi('reset')}")

def _ERR_O():
    o = f"{ansiHex('aa0000') + ('━'*(TERM_WIDTH()-4)) + ansi('reset')}" # ff6655
    return (f"{o}{ansi('reset')}")

def _extract_script_error_type(stderr: str) -> str:
    if not stderr: return "UnknownError"
    match = re.search(r"(\w+Error|Exception|Warning)(?::|$)", stderr.splitlines()[-1]) # Look for final "SomethingError:" or just "ExceptionName:"
    if match: return match.group(1)
    match = re.search(r"(\w+Error|Exception|Warning)", stderr) # fallback: scan entire stderr
    return match.group(1) if match else "UnknownError"


def _clean_trace_lines(trace: str) -> list[str]:
    splitlines = trace.splitlines()
    lines = splitlines[1:]
    cleaned = []
    final = []
    for i, line in enumerate(lines):
        if "File " in line and " line " in line:
            new = _clean_link(line)
            new = new.replace('", line', ansi('reset') + ansi('K') + f", {ansiHex('#55bbdd')}line") 
            new = ansiHex('#aaccff') + ansi('bold') + "    " + new + ansiHex('#77ddff')

            new = new.replace('File "', ansi('reset'))
            new = new.replace(', in <module>', '') + ansi('reset')
            new = new.replace(', in', ansi('reset')+f"{ansi('R')}  :: " + ansiHex('#ff8866')) + ansi('reset')
            if '<' not in new and '>' not in new: cleaned.append('')
            cleaned.append(new)
            # if '<' not in new and '>' not in new: cleaned.append('\n' + new)

        elif '~' in line and '^' in line: # 〰 〜 ～ ┈ ═ ﹉ ﹋ ﹌ ﹊
            new = line.replace("~", f"{ansiHex('#886622')}─")
            new = new.replace("^", f"{ansiHex('#eecc22') + ansi('bold')}━")
            cleaned.append(ansi('reset') + f"{new}" + ansi('reset'))
        elif i == len(lines)-1: 
            key, sep, value = line.partition(': ')
            if sep: new = f"{key}: {_ERS(value)}"
            else: new = f"{_ERS(line)}"
            # final.append(ansi('reset') + _ERR_I() + ansi('reset'))
            final.append(ansi('reset') + _ERR_L(new) + ansi('reset'))
        else: cleaned.append(ansiHex('#ffaadd') + ansiHex('ffddcc') + f"{line}" + ansi('reset'))
    final.extend(cleaned)
    # final.append(_ERR_O())
    return final



def _clean_link(line: str):
    # project_name = os.path.basename(os.path.dirname(__file__))
    project_name = os.path.basename(os.getcwd())
    new = re.sub(rf'^.*?Python[\\/]', '', str(line))                # Remove up through "Python/"
    new = re.sub(rf'^.*?{re.escape(project_name)}[\\/]', '', new)   # Remove up through the project folder dynamically
    new = new.replace("\\", "/")
    return new




        
def _ah(hex: str): return ansiHex(hex[1:])
_rst = ansi('reset')
_c_i = ["#77cdff", "#aaddff", "#bbddee"]
_c_w = ["#eeee11", "#ffee77", "#eeddaa"]
_c_f = ["#ff6644", "#ff7755", "#ee9966"]
_c_e = ["#ff5555", "#ff7766", "#ee8877"]
_pre_ln = "━━"*5
_l = "  "
_ln_pre = ansiHex('#56e64c') + ansi('bold')
_ln = _ln_pre + "│" + _l + ansi('reset')

def _clen(s: str): return len(strip_ansi(s.strip()))
def _init(text: str, cols: list): print(_ln + "\n" + _ln + STY(_pre_ln + f"━━  {text.upper()}  " + ("━" * (max(TERM_WIDTH()-32, len(text)) - len(text))), cols[0])+"\n"+_ln)
def _cap(): print(_ln + ansi('reset'))
def _br(cols: list): print(_ln + _rst + ansiHex(cols[0]) + "\n─────────────────────────────────────────────────────────────────\n" + _rst)

def _pr(s: dict, cols: list, ic: str, width: int): 
    pr_pre = STY(ic + _l, cols[0], 'bold')  +  STY(s['pre'].strip(), cols[1], width) if s['pre'] else ''
    pr_mid = STY(_l +"➡" + _l, "WH") +STY(s['mid'].strip(), cols[2])
    pr_suf = _l + s['link']
    print(_ln + pr_pre + pr_mid + pr_suf)


def _print_LOGS(logs: list[dict], init_text: str, colors: list, ic: str):
    if not logs: return
    sW = 24
    for l in logs: sW = _clen(l['pre']) if l['pre'] and _clen(l['pre']) > sW else sW
    _init(init_text, colors) # print(_ln+"\n"+_ln + STY(_pre_ln+"━━  INFORMATION REPORTS  ━━" + _bld_ln, _c_i[0])+"\n"+_ln)
    for s in logs: _pr(s, colors, ic, sW) # _po(STY(f"✦"+_l, _c_i[0], 'bold'), s['pre'].strip(), _c_i[1], sW, s['mid'].strip(), _c_i[2], s['link'])
    _cap()
    

def _print_EXITLOGS_INFO(): _print_LOGS(EXITLOGS_INFO, "INFORMATION REPORT", _c_i, "✦")
def _print_EXITLOGS_WARN(): _print_LOGS(EXITLOGS_WARN, "WARNING REPORT", _c_w, "⚠︎")
def _print_EXITLOGS_FAIL(): _print_LOGS(EXITLOGS_FAIL, "FAILURE REPORT", _c_f, "✖")

def _print_EXITLOGS_ERROR():
    if not EXITLOGS_ERROR: return
    _init("ERROR REPORT", _c_e)
    for i, pkg in enumerate(EXITLOGS_ERROR, start=1):
        if "trace" in pkg and pkg["trace"]:  # full traceback for module error
            trace_lines = _clean_trace_lines(pkg["trace"].rstrip())
            print(f"{_ln}" + f"\n{_ln}".join(trace_lines))
        if i < len(EXITLOGS_ERROR)-1: _br(_c_e)
    _cap()

def getCurrentDurationStr():
    curr_time = datetime.now()
    set_TIMEISO_FINAL()
    try: init_time = datetime.fromisoformat(TIMEISO_START['time']) if TIMEISO_START["time"] else curr_time
    except Exception: init_time = curr_time
    return { 
        'duration': str(curr_time - init_time).split('.')[0], 
        'curr': str(curr_time).split(' ')[1].split('.')[0], 
        'init': str(init_time).split(' ')[1].split('.')[0],
    }

def PRINT_DURATION_REPORT():
    nrm = ansiHex('29abcc')
    bld = ansiHex('33d6ff') + ansi('bold')
    durStr = getCurrentDurationStr()
    str_dur = f"{bld}DURATION: {_rst}{durStr['duration']}"
    str_final = f"{nrm}TIME: {_rst}{durStr['curr']} - {durStr['init']}"
    print(f"\n   {str_dur}    {str_final}\n{_rst}")
    # if len(EXITLOGS_INFO): print(f"EXITLOGS_INFO: {len(EXITLOGS_INFO)}")
    # if len(EXITLOGS_WARN): print(f"EXITLOGS_WARN: {len(EXITLOGS_WARN)}")
    # if len(EXITLOGS_FAIL): print(f"EXITLOGS_FAIL: {len(EXITLOGS_FAIL)}")
    # if len(EXITLOGS_ERROR): print(f"EXITLOGS_ERROR: {len(EXITLOGS_ERROR)}")


def PR_NOTE(mid: str, defTo = None, *, pre: Optional[str] = None):
    PR_LN(termTAG("●", "NOTE", mid, '#2472c8', '#99caff'), pre=pre)
    return defTo


def PR_INFO(mid: str, defTo = None, *, pre: Optional[str] = None, group: str = "", link: str = ""):
    mid = termTAG("✧", "INFO", mid, '#2472c8', '#99caff')
    PR_LN(mid, pre=pre)
    push_EXITLOGS_INFO({ "group": group, "link": link, "mid": mid, "pre": pre })
    return defTo


def PR_WARN(mid: str, defTo = None, *, pre: str = "WARN", group: str = "", link: str = ""):
    mid = termTAG("⚠︎", "WARN", STY(mid, '#f5f580'), '#e5e510', '#222200', '#ff0000')
    PR_LN(mid, pre=STY(pre, 'Y', 'bold'))
    push_EXITLOGS_WARN({ "group": group, "link": link, "mid": mid, "pre": pre })
    return defTo


def PR_FAIL(mid: str, defTo = None, *, pre: str = "FAIL", group: str = "", link: str = ""):
    mid = termTAG("✖", "FAIL", mid, '#cd3131', '#ff7777')
    PR_LN(mid, pre=pre)
    push_EXITLOGS_FAIL({ "group": group, "link": link, "mid": mid, "pre": pre })
    return defTo


def PR_ERROR(mid: str, e: Exception, defTo = None, *, pre: str = "ERROR", group: str = "", link: str = "", ic: str = "✖"):
    if isinstance(e, subprocess.CalledProcessError): # Subprocess errors include pipe output
        trace = e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
    else: trace = ''.join(traceback.format_exception(type(e), e, e.__traceback__)) # Python exception traceback
    push_EXITLOGS_ERROR({
        "group": group, "link": link, "mid": mid, "pre": pre,
        "trace": trace, "internal_type": _extract_script_error_type(trace),
    })
    PR_BR(STY(f"{_clean_link(link)}", 'italic', 'RH'), pre=STY(f"  {ic}  ERROR  ", 'BG_R', 'bold'))
    trace_lines = _clean_trace_lines(trace.rstrip())
    print(f"\n".join(trace_lines))




# INITIALIZE AT PROGRAM START  ➡  atexit.register(PRINT_EXITLOGS)
def PRINT_EXITLOGS():
    termw = (TERM_WIDTH()-2)
    bd = ansiHex('29abcc') + '┃' + ansi('reset')
    lh = ansiHex('33d6ff') + '╱' * termw + ansi('reset')
    ld = ansiHex('1f8199') + '╱' * termw + ansi('reset')
    print(ansiHex('33d6ff') + "\n\n" + bd + lh + bd + "\n" + bd + ld + bd + ansi('reset'))
    PRINT_DURATION_REPORT()

    strStart = f"──────── ★ ★ ★ ─────────   S U M M A R Y   ───────── ★ ★ ★ ────────"
    strFinal = f"──────── ★ ★ ★ ────   G E N   C O M P L E T E   ──── ★ ★ ★ ────────"
    strStart = strStart + "─" * max(termw - len(strStart), 0)
    strFinal = strFinal + "─" * max(termw - len(strFinal), 0)

    can_sum = len(EXITLOGS_INFO) + len(EXITLOGS_WARN) + len(EXITLOGS_FAIL) + len(EXITLOGS_ERROR) > 0
    if can_sum: print("\n\n" + _ln_pre + f"┌" + strStart + ansi('reset'))
    if len(EXITLOGS_INFO): _print_EXITLOGS_INFO()
    if len(EXITLOGS_WARN): _print_EXITLOGS_WARN()
    if len(EXITLOGS_FAIL): _print_EXITLOGS_FAIL()
    if len(EXITLOGS_ERROR): _print_EXITLOGS_ERROR()

    print(_ln_pre + f"{'└' if can_sum else '\n'}" + strFinal + ansi('reset') + "\n\n\n")


def INIT_REPORTS(): 
    atexit.register(PRINT_EXITLOGS)
    set_TIMEISO_START()