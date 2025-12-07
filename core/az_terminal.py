import sys, re, time
from typing import Optional, Tuple, Union
from dataclasses import dataclass, field
from shutil import get_terminal_size
from wcwidth import wcswidth





def ansi(*code: list[str]): return ''.join([ANSI.get(c, '') for c in code])
def strip_ansi(s: str) -> str: return _ANSI_RE.sub("", s)






# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┃   PRIVATE ANSI HELPERS
# ┖────────────────────────────────────────────────────────────────


# ╱╱╱╱╱╱╱╱  Match ANSI CSI sequences and OSC sequences (colors, cursor moves, hyperlinks, etc.)
# CSI: ESC [ ... cmd
# OSC: ESC ] ... BEL   (we also handle ST ESC \)
_ANSI_RE = re.compile(
    r"""
    (?:\x1B\[ [0-?]* [ -/]* [@-~])     # CSI
    | (?:\x1B\] .*? (?:\x07|\x1B\\))   # OSC (terminated by BEL or ST)
    """,
    re.VERBOSE | re.DOTALL,
)


# ╱╱╱╱╱╱╱╱  Control Sequence Introducer
CSI = "\033["


# ╱╱╱╱╱╱╱╱  CHA: move to absolute column (1-based)
def _goto_col(col: int) -> str: return f"{CSI}{max(1, col)}G"


# ╱╱╱╱╱╱╱╱  Save cursor
def _save_cursor() -> str: return f"{CSI}s"


# ╱╱╱╱╱╱╱╱  Restore cursor
def _restore_cursor() -> str: return f"{CSI}u"


# ╱╱╱╱╱╱╱╱  ANSI controls
ANSI = {
    # Clearing / Cursor control
    "clear_end":    f"{CSI}K",   # Clear from cursor to end of line
    "clear_line":   f"{CSI}2K",  # Clear entire line
    "reset":        f"{CSI}0m",   # Reset all styles (color, bold, italic, underline)

    # Text styles
    "bold":         f"{CSI}1m",  # Bold text
    "dim":          f"{CSI}2m",  # Dim / faint text
    "italic":       f"{CSI}3m",  # Italic text (may not work in all terminals)
    "underline":    f"{CSI}4m",  # Underlined text
    "blink":        f"{CSI}5m",  # Blinking text (not widely supported)
    "reverse":      f"{CSI}7m",  # Swap foreground/background colors
    "hidden":       f"{CSI}8m",  # Hidden/invisible text

    # Standard colors (foreground)
    "K":            f"{CSI}30m",  # Black
    "R":            f"{CSI}31m",  # Red
    "G":            f"{CSI}32m",  # Green
    "Y":            f"{CSI}33m",  # Yellow
    "B":            f"{CSI}34m",  # Blue
    "M":            f"{CSI}35m",  # Magenta
    "C":            f"{CSI}36m",  # Cyan
    "W":            f"{CSI}37m",  # White
    "RH":           f"{CSI}91m",  # Bright Red
    "GH":           f"{CSI}92m",  # Bright Green
    "YH":           f"{CSI}93m",  # Bright Yellow
    "BH":           f"{CSI}94m",  # Bright Blue
    "MH":           f"{CSI}95m",  # Bright Magenta
    "CH":           f"{CSI}96m",  # Bright Cyan
    "WH":           f"{CSI}97m",  # Bright White

    # Background colors (standard)
    "BG_K":         f"{CSI}40m",  # Background White
    "BG_R":         f"{CSI}41m",  # Background Red
    "BG_G":         f"{CSI}42m",  # Background Green
    "BG_Y":         f"{CSI}43m",  # Background Yellow
    "BG_B":         f"{CSI}44m",  # Background Blue
    "BG_M":         f"{CSI}45m",  # Background Magenta
    "BG_C":         f"{CSI}46m",  # Background Cyan
    "BG_W":         f"{CSI}47m",  # Background White
    "BG_RH":        f"{CSI}101m",  # Bright Background Red
    "BG_GH":        f"{CSI}102m",  # Bright Background Green
    "BG_YH":        f"{CSI}103m",  # Bright Background Yellow
    "BG_BH":        f"{CSI}104m",  # Bright Background Blue
    "BG_MH":        f"{CSI}105m",  # Bright Background Magenta
    "BG_CH":        f"{CSI}106m",  # Bright Background Cyan
    "BG_WH":        f"{CSI}107m",  # Bright Background White
}


# ╱╱╱╱╱╱╱╱  Truncate string to visible width, preserving ANSI escape codes
def _ansi_truncate(s: str, width: int) -> str:
    if width <= 0 or not s: return ""
    out, vis, i, n = [], 0, 0, len(s)
    while i < n and vis < width:
        if s[i] == '\x1b':
            m = _ANSI_RE.match(s, i)
            if m:
                out.append(m.group(0))
                i = m.end()
                continue
        out.append(s[i])
        vis += 1
        i += 1
    return ''.join(out)


# ╱╱╱╱╱╱╱╱  Pad string to visible width using spaces (ANSI-aware).
def _pad_visible(s: str, width: int, align: str, vlen_fn) -> str:
    vis = vlen_fn(s)
    if vis >= width: return _ansi_truncate(s, width)
    spaces = width - vis
    if align == ">": return " " * spaces + s
    elif align == "^":
        left = spaces // 2
        right = spaces - left
        return " " * left + s + " " * right
    else: return s + " " * spaces # "<"






# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┃   STRING LENGTH HELPERS
# ┖────────────────────────────────────────────────────────────────


# Return the 'visual length' of string `s`, excluding ANSI escape sequences.
# Uses wcwidth for Unicode width where possible.
def vlen(s: str) -> int:
    col = 0
    i = 0
    while i < len(s):
        m = _ANSI_RE.match(s, i)
        if m:
            i = m.end() # skip ANSI escape codes entirely
            continue
        ch = s[i]
        if wcswidth is not None:
            w = wcswidth(ch)
            if w < 0: w = 1  # fallback for unprintables
        else: w = 1
        col += w
        i += 1
    return col




# Truncate/pad s to exactly `width` display columns, preserving ANSI sequences.
# Ensures trailing SGR reset if styling likely active.
def vfit(s, width: int) -> str:
    s = str(s)
    if width <= 0: return ""
    out = []
    col = 0
    i = 0
    needs_reset = False
    while i < len(s) and col < width:
        m = _ANSI_RE.match(s, i)
        if m:
            # copy escape sequence verbatim (no column cost)
            seq = m.group(0)
            out.append(seq)
            # Heuristic: if this looks like SGR with non-reset params, track reset need
            if seq.startswith("\x1b["):
                # strip \x1b[ and trailing cmd letter
                body = seq[2:-1]
                if body and not body.endswith("m"): pass  # not SGR
                elif body and body != "0m": needs_reset = True
            i = m.end()
            continue

        ch = s[i]
        # compute width of this single character (without ANSI)
        if wcswidth is not None:
            w = wcswidth(ch)
            if w < 0: w = 1  # treat unknowns as 1 column
        else: w = 1
        if col + w > width: break

        out.append(ch)
        col += w
        i += 1
    # right-pad with spaces to reach width
    if col < width: out.append(" " * (width - col))
    # Safety: if styles were opened, close them
    if needs_reset and (not out or not out[-1].endswith("\x1b[0m")): out.append("\x1b[0m")
    return "".join(out)






# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┃   GLOBAL TERMINAL CLASS
# ┖────────────────────────────────────────────────────────────────


# DEFAULTS
_W_LINE: int = 96
_W_LINE_MULT: int = 0.96
_W_PRE: int = 20
_W_PRE_MULT: int = 0.32
_W_SUF: int = 20


@dataclass
class ConsoleLineState:
    
    # Content (raw strings; no ANSI width accounting here)
    pre: str = ""
    mid: str = ""
    suf: str = ""

    # Layout
    w_line: int = _W_LINE
    w_pre: int = field(default_factory=lambda: int(max(0, get_terminal_size((_W_LINE, 20)).columns) * _W_PRE_MULT))
    w_suf: int = _W_SUF
    use_term_width: bool = True

    # Logging
    infos: list[str] = field(default_factory=list)
    warns: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    # Progress / spinner
    spinner: int = 0
    prog_cur: int = 0
    prog_max: int = 0
    prog_bytes: bool = False

    # Internals
    _active: bool = False
    _last_render: float = 0.0  # seconds
    _interval: float = 0.1     # seconds between renders


    def dump_infos(self): return '\n\n'.join(self.infos)
    def dump_warns(self): return '\n\n'.join(self.warns)
    def dump_errors(self): return '\n\n'.join(self.errors)
    def add_info(self, text: str): self.infos.append(text)
    def add_warn(self, text: str): self.warns.append(text)
    def add_error(self, text: str): self.errors.append(text)

    def _can_render(self, force: bool = False) -> int:
        now = time.perf_counter()
        can = force == True or (self._active and now - self._last_render < self._interval)
        if can and not force: self._last_render = now
        return can

    def _resolved_line_width(self) -> int:
        if self.use_term_width: return int(max(1, get_terminal_size((self.w_line, 20)).columns) * _W_LINE_MULT)
        return self.w_line
    
    # ╱╱╱╱╱╱╱╱  Return (pre_col, body_col, suf_col) absolute 1-based columns.
    def _regions(self) -> tuple[int, int, int]:
        lw = self._resolved_line_width()
        pw = max(0, min(self.w_pre, lw))
        sw = max(0, min(self.w_suf, lw))
        # Body width fits whatever remains
        # Columns (1-based): prefix at 1; body after prefix; suffix aligned right.
        pre_col = 1
        mid_col = 1 + pw
        suf_col = lw - sw + 1
        # Ensure sane ordering even in small widths
        if mid_col > suf_col: mid_col = suf_col
        return pre_col, mid_col, suf_col

    def _widths(self) -> tuple[int, int, int]:
        lw = self._resolved_line_width()
        pw = max(0, min(self.w_pre, lw))
        sw = max(0, min(self.w_suf, lw))
        bw = max(0, lw - pw - sw)
        return pw, bw, sw

    # ╱╱╱╱╱╱╱╱  Content setters
    def out_pre(self, text: str, force: bool = True, *, append: bool = False):
        self._active = True
        self.w_pre = int(TERM_WIDTH_FULL()*_W_PRE_MULT)
        self.pre = (self.pre + text) if append else text
        self._render_prefix(force)

    def out_mid(self, text: str, force: bool = True, *, append: bool = False):
        self._active = True
        self.mid = (self.mid + text) if append else text
        self._render_body(force)

    def out_suf(self, text: str, force: bool = False):
        self._active = True
        self.w_suf = int(_W_SUF)
        self.suf = text
        self._render_suffix(force)


    # ╱╱╱╱╱╱╱╱  Renders for each region
    def _render_prefix(self, force: bool = True):
        if force or self._can_render(force): 
            pw, _, _ = self._widths()
            col_p, _, _ = self._regions()
            block = vfit(self.pre, pw)
            sys.stdout.write(_save_cursor())
            sys.stdout.write(_goto_col(col_p))
            sys.stdout.write(block[:-1]+" ")
            sys.stdout.write(_restore_cursor())
            sys.stdout.flush()

    def _render_body(self, force: bool = True):
        if force or self._can_render(force): 
            _, bw, _ = self._widths()
            _, col_b, _ = self._regions()
            block = vfit(self.mid, bw)
            sys.stdout.write(_save_cursor())
            sys.stdout.write(_goto_col(col_b))
            sys.stdout.write(block)
            sys.stdout.write(_restore_cursor())
            sys.stdout.flush()

    def _render_suffix(self, force: bool = False):
        if force or self._can_render(force): 
            _, _, sw = self._widths()
            _, _, col_s = self._regions()
            block = vfit(self.suf, sw)
            sys.stdout.write(_save_cursor())
            sys.stdout.write(_goto_col(col_s))
            sys.stdout.write(block)
            sys.stdout.write(_restore_cursor())
            # sys.stdout.flush()


    # ╱╱╱╱╱╱╱╱  UNUSED: For managing nested progressions
    def _set_prog(self, *, pcur: Optional[int], pmax: Optional[int], pbytes: Optional[bool]):
        self.prog_cur = max(pcur if pcur else self.prog_cur, 0)
        self.prog_max = max(pmax if pmax else self.prog_max, 0)
        self.prog_bytes = pbytes if pbytes else self.prog_bytes
        self._render_suffix()


    # ╱╱╱╱╱╱╱╱  Invalidate and render the line again
    def render_all(self, force: bool = False):
        if self._can_render(force):
            self._render_prefix(True)
            self._render_body(True)
            self._render_suffix()
        # if not self._active: return
        # self._render_prefix(force)
        # self._render_body(force)
        # self._render_suffix(force)


    # ╱╱╱╱╱╱╱╱  Lifecycle
    def newline(self):
        if self._active: sys.stdout.write("\n")
        self.pre = self.mid = self.suf = ""
        self._active = False

    def reset(self):
        self.pre = self.mid = self.suf = ""
        self._active = False

    def set_line(self, *,
                   mid: Optional[Union[int, bool, str]] = None,
                   pre: Optional[Union[int, bool, str]] = None,
                   suf: Optional[Union[int, bool, str]] = None,
                   useTermWidth: Optional[bool] = None):
        if pre is not None and isinstance(pre, bool): self.w_pre = int(TERM_WIDTH_FULL() * _W_PRE_MULT) if pre else 0
        if mid is not None and isinstance(mid, bool) and not mid: self.out_mid("")
        if suf is not None and isinstance(suf, bool): self.w_suf = int(_W_SUF) if pre else 0

        if pre is not None and isinstance(pre, int): self.w_pre = int(pre)
        if mid is not None and isinstance(mid, int): self.w_line = int(mid)
        if suf is not None and isinstance(suf, int): self.w_suf = int(suf)

        if mid is not None and isinstance(mid, str): self.out_mid(str(mid), True)
        if pre is not None and isinstance(pre, str): self.out_pre(str(pre), True)
        if suf is not None and isinstance(suf, str): self.out_suf(str(suf), True)

        if useTermWidth is not None: self.use_term_width = bool(useTermWidth)
        if self._active: self.render_all() # If active, re-render with new widths
        # time.sleep(0.5)




# ╱╱╱╱╱╱╱╱  Global instance + API
def _PR() -> "ConsoleLineState":
    global _CONSOLE # lazily create and memoize a single ConsoleLineState instance
    try: return _CONSOLE
    except NameError:
        _CONSOLE = ConsoleLineState()
        return _CONSOLE






# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┃   TERMINAL API
# ┖────────────────────────────────────────────────────────────────


def TERM_WIDTH_FULL(n: int = 1): return int(_PR()._resolved_line_width() * n)
def TERM_WIDTH(n: int = 1): return int((_PR()._resolved_line_width() - _PR()._widths()[2]) // n)




def SET_PR(*, pre: Optional[Union[int, bool, str]] = None,
              mid: Optional[Union[int, bool, str]] = None,
              suf: Optional[Union[int, bool, str]] = None):
    useTerm = mid if isinstance(mid, bool) else None
    _PR().set_line(mid=mid, pre=pre, suf=suf, useTermWidth=useTerm)




def PR_PRE(pre: Optional[Union[int, bool, str]] = None): SET_PR(pre=pre)
def PR_MID(mid: Optional[Union[int, bool, str]] = None): SET_PR(mid=mid)
def PR_SUF(suf: Optional[Union[int, bool, str]] = None): SET_PR(suf=suf)




def PR_NEXT(lines: int = 1):
    _PR().out_suf("", True)
    for _ in range(max(0, int(lines))): _PR().newline()




def PR_RESET(): _PR().reset()




def PR_TABLE(*text, 
    pre: Optional[Union[str, bool]] = None, 
    suf: Optional[Union[str, bool]] = None, 
    loud: bool = True, ln: bool = False, nl: bool = False, br: bool = False,
    gap=2, sep="", align="<", color="#88ffaa", colors=None, ratio=None
):
    if loud: 
        _PR().set_line(pre=pre, mid=True, suf=suf)
        mid = getStrTable(*text, gap=gap, sep=sep, align=align, color=color, colors=colors, ratio=ratio)
        _PR().set_line(pre=pre, mid=mid, suf=suf)
        if nl or br: PR_NEXT()
        if isinstance(pre, str): SET_PR(pre=True)
        if ln or br: PR_NEXT()




def PR(mid: Optional[Union[str, bool]] = None, *, pre: Optional[Union[str, bool]] = None, suf: Optional[Union[str, bool]] = None, 
       loud: bool = True, ln: bool = False, nl: bool = False, br: bool = False):
    if loud: 
        _PR().set_line(pre=pre, mid=mid, suf=suf)
        _PR().set_line(pre=pre, mid=mid, suf=suf)
        if nl or br: PR_NEXT()
        if isinstance(pre, str): SET_PR(pre=True)
        if ln or br: PR_NEXT()




def PR_LN(mid: Optional[Union[str, bool]] = None, *, pre: Optional[Union[str, bool]] = None, suf: Optional[Union[str, bool]] = None, 
          loud: bool = True):
    # PR(f"", pre=False, suf=False)
    PR(mid, pre=pre, suf=suf, loud=loud, ln=True)


def PR_NL(mid: Optional[Union[str, bool]] = None, *, pre: Optional[Union[str, bool]] = None, suf: Optional[Union[str, bool]] = None, 
          loud: bool = True):
    PR(mid, pre=pre, suf=suf, loud=loud, nl=True)


def PR_BR(mid: Optional[Union[str, bool]] = None, *, pre: Optional[Union[str, bool]] = None, suf: Optional[Union[str, bool]] = None, 
          loud: bool = True):
    PR(mid, pre=pre, suf=suf, loud=loud, br=True)






# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┃   STRING HELPERS
# ┖────────────────────────────────────────────────────────────────


def _clevel(level: int):
    def s(c: str): return f"#"+(c[1]*2)+"FF"+(c[0]*2)
    clvl = [s('0E'), s('2C'), s('4A'), s('68'), s('86'), s('A4'), s('C2'), s('E0')]
    return clvl[level % len(clvl)]


def getStrProgBar(pct: float, level: int = 0, w: int = 8):
    STEPS = "▏▎▍▌▋▊▉█"
    TOTAL_UNITS = w * len(STEPS)
    filled_units = int(pct * TOTAL_UNITS)
    full_blocks, remainder = divmod(filled_units, len(STEPS))
    prog = "█" * full_blocks
    if remainder: prog += STEPS[remainder - 1]
    return STY(vfit(prog, w), _clevel(level))


def getStrProgPct(pct: float, w: int = 6, dec: int = 1) -> str:
    if dec < 0: dec = 0
    s = f"{pct*100:.{dec}f}%"
    return STY(vfit(s, w), _clevel(int(8*pct)))


# ("ᴮ", "ᴷᴮ", "ᴹᴮ", "ᴳᴮ", "ᵀᴮ")
# ("ʙ", "ᴋʙ", "ᴍʙ", "ɢʙ", "ᴛʙ")
# ("B", "KB", "MB", "GB", "TB")
_UNITS = ("B", "KB", "MB", "GB", "TB")
_UNITS_SM = ("ʙ", "ᴋʙ", "ᴍʙ", "ɢʙ", "ᴛʙ")
_POW   = {u: i for i, u in enumerate(_UNITS)}
def _choose_unit(n: int, small_unit: bool = True) -> Tuple[float, str]:
    x = float(n)
    for u in (_UNITS_SM if small_unit else _UNITS):
        if x < 1024.0 or u == "TB": return (x, u)
        x /= 1024.0
    return (x, "TB") # fallback


def getStrBytes(
    n: int, *, dec: int = 1, 
    show_suffix: bool = True, 
    small_unit: bool = True, 
    space_unit: bool = False, 
    force_unit: Optional[str] = None
) -> str:
    if n < 0: n = 0
    if force_unit is not None and force_unit not in _POW: force_unit = None
    if force_unit is None: val, unit = _choose_unit(n, small_unit)
    else:
        unit = force_unit
        val = float(n) / (1024.0 ** _POW[unit])
    if unit == "B" or unit == "ʙ": num = f"{int(round(val))}"
    else:
        if dec < 0: dec = 0
        num = f"{val:.{dec}f}"
    if space_unit: unit = f" {unit}"
    return f"{num}{unit}" if show_suffix else num


# Build left-padded size progress string (e.g. '  0.5 /  0.5KB')
# - Left value is converted to the same unit as total.
# - Suffix visibility controlled by show_suffix.
# - Left-pads to 'width' chars if needed (no truncation if width is small).
def getStrProgBytes(read: int, total: int, *, w: int = _W_SUF, dec: int = 1) -> str:
    br = max(0, int(read))
    bt = max(0, int(total))
    _, unit = _choose_unit(bt) # Decide unit from total; then render both sides with that unit
    left  = STY(column(getStrBytes(br, dec=dec, show_suffix=False, force_unit=unit), 5), '#7dffe7')
    right = STY(column(getStrBytes(bt, dec=dec, show_suffix=True, force_unit=unit), 6), '#5ebfad')
    s = f"{left} / {right}"
    return vfit(s, w)


# Convert a hex color string to an ANSI escape code (Truecolor).
#
# Accepts lengths 3–8 (hex digits), with optional '#' or '0x' prefix:
#   - 3:  RGB      (e.g. "f80")
#   - 4:  RGBA     (e.g. "f80c")
#   - 6:  RRGGBB   (e.g. "ff8800")
#   - 8:  RRGGBBAA (e.g. "ff8800cc")
# Non-standard lengths 5 or 7 are allowed and will be padded by repeating
# the final digit to reach 6 or 8 respectively.
#
# Alpha (if present) darkens the color toward black (premultiplied):
#     rgb' = round(rgb * alpha/255)
#
# Set background=True for a background code, otherwise foreground.
def hexToAnsi(hex_color: str, *, background: bool = False) -> str:
    if not isinstance(hex_color, str): raise TypeError("hex_color must be a string")
    s = hex_color.strip().lower()
    if s.startswith("0x"): s = s[2:]
    elif s.startswith("#"): s = s[1:]
    elif s.startswith("$"): s = s[1:]
    # Validate characters
    if not (3 <= len(s) <= 8): raise ValueError("Hex length must be between 3 and 8 characters")
    if any(c not in "0123456789abcdef" for c in s): raise ValueError("Hex string contains non-hex characters")
    # Normalize to even length (handle 3/4, and pad 5/7 by repeating last char)
    if len(s) in (3, 4): s = "".join(c*2 for c in s)  # short notation expansion
    elif len(s) in (5, 7): s = s + s[-1]  # pad to 6 or 8 by repeating last nibble
    # Now s length is 6 (RGB) or 8 (RGBA)
    if len(s) == 6:
        r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        a = 255
    elif len(s) == 8:
        r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        a = int(s[6:8], 16)
    else: raise ValueError("Could not normalize hex string") # Should be unreachable due to normalization above
    factor = a / 255.0 # Darken toward black by alpha factor (premultiplied alpha)
    r = max(0, min(255, round(r * factor)))
    g = max(0, min(255, round(g * factor)))
    b = max(0, min(255, round(b * factor)))
    return bgRGB(r, g, b) if background else fgRGB(r, g, b)


# Return text padded or truncated to exactly `width` characters.
def column(text, width: Optional[int] = None) -> str:
    if width: return vfit(str(text), width)
    else: return str(text)


# colors = per-column colors (fallback to `color`)
# ratio = per-column weights
def getStrTable(
    *text, w=_PR()._widths()[1], gap=2, pre="", sep="", suf="", align="<", color="#88ffaa", colors=None, ratio=None
) -> str:
    if not text: return ""
    cells = tuple("" if t is None else str(t) for t in text)
    n = len(cells)
    pre_styled = STY(pre + (" " * gap), color + '48') if pre else ""
    sep_styled = STY(sep + (" " * gap), color + '48')
    suf_styled = STY(suf, color + '48') if suf else ""
    sep_space = vlen(sep_styled) * (n - 1) # available visible width for columns
    avail_cols = max(0, w - vlen(pre_styled) - vlen(suf_styled) - sep_space)
    if ratio is None: ratio = []
    weights = [float(ratio[i]) if i < len(ratio) else 1.0 for i in range(n)]
    weights = [wt if wt > 0 else 0.0 for wt in weights]
    total_weight = sum(weights) if sum(weights) > 0 else float(n)
    exact = [avail_cols * (wt / total_weight) for wt in weights]
    base = [int(x) for x in exact]
    remainder = avail_cols - sum(base)
    frac_order = sorted([(i, exact[i] - base[i]) for i in range(n)], key=lambda t: t[1], reverse=True)
    for i in range(remainder): base[frac_order[i % n][0]] += 1
    if avail_cols >= n:
        zeros = [i for i, wcol in enumerate(base) if wcol == 0]
        for zi in zeros:
            donors = sorted(enumerate(base), key=lambda t: t[1], reverse=True)
            for j, wcol in donors:
                if j != zi and wcol > 1:
                    base[j] -= 1
                    base[zi] += 1
                    break

    col_w = base  # sum == avail_cols
    if colors is None: colors = []
    col_colors = [colors[i] if i < len(colors) and colors[i] else color for i in range(n)]
    out_cols = [] # truncate/pad by visible width; only recolor if cell isn't already styled
    for i in range(n):
        raw = cells[i]
        has_ansi = "\x1b[" in raw  # check for existing styling
        trimmed = _ansi_truncate(raw, col_w[i]) if has_ansi else (raw[:col_w[i]]) # truncate by visible width
        padded = _pad_visible(trimmed, col_w[i], align, vlen) # pad by visible width
        col_text = padded if has_ansi else STY(padded, col_colors[i]) # colorize only if not already styled
        out_cols.append(col_text)

    row = sep_styled.join(out_cols)
    return f"{pre_styled}{row}{suf_styled}"





def fgRGB(r:int, g:int, b:int): return f"\033[38;2;{r};{g};{b}m"
def bgRGB(r:int, g:int, b:int): return f"\033[48;2;{r};{g};{b}m"
def fgHex(color:str): return hexToAnsi(color, background=False)
def bgHex(color:str): return hexToAnsi(color, background=True)
def ansiHex(fgColor:str, bgColor:Optional[str] = None): return f"{fgHex(fgColor)}{bgHex(bgColor) if bgColor else ''}"






def STY(text, *style):
    w = 0
    code = ""
    if style:
        for s in style:
            if isinstance(s, (int, float)): w += int(s)
            if isinstance(s, str) and '#' in s: code += fgHex(s)
            if isinstance(s, str) and '$' in s: code += bgHex(s)
            if isinstance(s, str) and '#' not in s and '$' not in s: code += ansi(s)
    return f"{ansi('reset')}{code}{column(str(text), w)}{ansi('reset')}"




# (' FILE COMPLETE ' if is_bytes else ' PROC COMPLETE ')
# (' ꜰɪʟᴇ ᴄᴏᴍᴩʟᴇᴛᴇ ' if is_bytes else ' ᴩʀᴏᴄ ᴄᴏᴍᴩʟᴇᴛᴇ ')
def PR_PROGT(s: Optional[str] = None, level: int = 0):
    # if pct >= 1.0: PR_SUF("▏ ꜰɪʟᴇ ᴄᴏᴍᴩʟᴇᴛᴇᴅ ▕" if is_bytes else "▏ ᴩʀᴏᴄ ᴄᴏᴍᴩʟᴇᴛᴇ ▕")
    if s:
        cap = [STY("▏", '#8c8680'), STY("▕", '#8c8680')]
        _PR().out_suf(cap[0] + column(s, _W_SUF-2) + cap[1], True)
        # PR_SUF(column(f"{level} {s}", _W_SUF))
    else: PR_SUF('')



def termNAME(input):
    text = "List" if isinstance(input, list) else "Dict" if isinstance(input, dict) else "Thing"
    if isinstance(input, str): text = re.split(r"[\\/]", input)[-1].replace('.json','')
    return text


def termHEAD(head: str, name: str = "", color: str = "#7fcef5", *, ic: str = "", depth = 0):
    d = ((" "*depth) + "⮡  ") if depth else "" # "#96d9c2"
    return ansi() + f"{ic} {STY(d, color)}{STY(head, color, 'bold')} {STY(name, '#f5efd7')}" + ansi()




def termTAG(ic: str, head: str, text: str, bgColor: str, fgColor: str, icColor: Optional[str] = None):
    bl = bgHex(f"{bgColor}80") + fgHex(f"{bgColor}cc") + "▐" + ansi('reset')
    br = bgHex(f"{bgColor}80") + fgHex(f"{bgColor}cc") + "▌" + ansi('reset')
    ic = fgHex(icColor if icColor else fgColor) + bgHex(f"{bgColor}") + f" {ic} " + ansi('reset')
    tag = ic + fgHex(fgColor) + bgHex(f"{bgColor}") + ansi('bold') + f" {head} " + ansi('reset')
    return bl + tag + br + STY(f" {str(text)}", fgColor)





def PR_PROG(n: int, total: int, level: int = 0, *, isBytes: bool = False, loud: bool = True):
    if loud:
        _PR().spinner += 1
        def s(b: str, c: str): return STY(b, f"#"+(c[0]*2)+(c[1]*2)+"00")
        clvl = [s("█",'0E'), s("▇",'2C'), s("▆",'4A'), s("▅",'68'), s("▄",'86'), s("▃",'A4'), s("▂",'C2'), s("▁",'E0')]

        fine = len(clvl)
        caps = 4

        clocks = "🕛🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚"
        if level < fine and n >= 0:
            _PR().prog_cur = n
            _PR().prog_max = total
            _PR().prog_bytes = isBytes
        if not loud: return

        can = level < fine and total >= caps * level
        if _PR().prog_max: pct = max(0.0, min((_PR().prog_cur + 1) / _PR().prog_max, 1.0))
        else: pct = 0
        count = f"{clvl[level % len(clvl)]}{'💽' if isBytes else '📚' if n >= 0 else clocks[_PR().spinner % len(clocks)]}"

        # if pct >= 1.0 and level == 0: PR_PROGT(STY('  ᴄᴏᴍᴩʟᴇᴛᴇᴅ' if isBytes else '  ᴩʀᴏᴄᴇꜱꜱᴇᴅ', 'GH'))
        if pct >= 1.0 and level == 0: PR_PROGT(STY(f"{count} ɪᴛᴇᴍꜱ × {total}", '#6bb7ea'))
        elif can and pct >= 1.0 and total >= caps*2 * level: PR_PROGT(STY(f"{count} ɪᴛᴇᴍꜱ × {total}", '#6bb7ea'))
        elif can and _PR().prog_bytes and total >= 2048: PR_PROGT(f"{count} {getStrProgBytes(n, total)}", level)
        elif can and total >= caps*2 * level: PR_PROGT(f"{count} {getStrProgBar(pct, level)} {getStrProgPct(pct)}", level)
