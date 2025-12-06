from functools import wraps
import dataclasses, datetime, decimal, enum, fractions, math, os, pathlib, re, json
from typing import Any, Container, Generator, Hashable, Iterator, Mapping, Dict, Iterable, List, MutableSequence, MutableSet, Reversible, Sequence, Set, Sized, Union
from numbers import Number
from collections import Counter
from types import ModuleType, FunctionType, MethodType, GeneratorType
__all__ = [name for name in dir() if not name.startswith("_")]




def _ink(p): # Upgrade p(v)->bool to p(v,*k)->bool (key-aware).
    @wraps(p)
    def wrapper(v, *k):
        if not k: return p(v)
        if not isinstance(v, Mapping): return False
        return all((kk in v) and p(v[kk]) for kk in k)
    return wrapper

def _not(f): # Negate any key-aware predicate f(v,*k)->bool.
    @wraps(f)
    def neg(v, *k): return not f(v, *k)
    return neg

def _not_bool(t): # Predicate factory: isinstance(x, t) and not bool.
    def p(x): return isinstance(x, t) and type(x) is not bool
    return p

# ---- Only safe/accurate way to validate iterable
def _iterable(x):
    try: iter(x); return True
    except TypeError: return False

# ---- Fallbacks for regex types across Python versions
_RePattern = getattr(re, "Pattern", type(re.compile("x")))
_ReMatch   = getattr(re, "Match",   type(re.match("x", "x")))

# ---- “has this dunder (callable)?” factory (still def, returns a key-aware predicate)
def _has_dund(name):
    @_ink
    def _p(x): return callable(getattr(x, name, None))
    return _p


# ╱╱╱╱╱╱╱╱  Primitives
@_ink
def isNone(x): return x == None
@_ink
def isStr(x): return isinstance(x, str)
@_ink
def isNum(x): return _not_bool(Number)(x)
@_ink
def isStrNum(x): return isinstance(x, str) and re.fullmatch(r"-?\d+(?:\.\d+)?", x) is not None
@_ink
def isInt(x): return _not_bool(int)(x)
@_ink
def isFloat(x): return isinstance(x, float)
@_ink
def isComplex(x): return isinstance(x, complex)
@_ink
def isDict(x): return isinstance(x, dict)
@_ink
def isList(x): return isinstance(x, list)
@_ink
def isTuple(x): return isinstance(x, tuple)
@_ink
def isSet(x): return isinstance(x, set)
@_ink
def isBool(x): return isinstance(x, bool)
@_ink
def isByte(x): return isinstance(x, bytes)
@_ink
def isByteArr(x): return isinstance(x, bytearray)
@_ink
def isMemView(x): return isinstance(x, memoryview)
@_ink
def isFrozenSet(x): return isinstance(x, frozenset)
@_ink
def isRange(x): return isinstance(x, range)
@_ink
def isIterable(x): return _iterable(x)


# ╱╱╱╱╱╱╱╱  Collections
@_ink
def isMapping(x): return isinstance(x, Mapping)
@_ink
def isSequence(x): return isinstance(x, Sequence) and not isinstance(x, (str, bytes, bytearray))
@_ink
def isMutableSequence(x): return isinstance(x, MutableSequence)
@_ink
def isSetish(x): return isinstance(x, Set)
@_ink
def isMutableSet(x): return isinstance(x, MutableSet)


# ╱╱╱╱╱╱╱╱  Callables & iteration protocols
@_ink
def isFunc(x): return callable(x)
@_ink
def isCallable(x): return callable(x)
@_ink
def isIterator(x): return isinstance(x, Iterator)
@_ink
def isGenerator(x): return isinstance(x, Generator) or isinstance(x, GeneratorType)
@_ink
def isHashable(x): return isinstance(x, Hashable)
@_ink
def isSized(x): return isinstance(x, Sized)
@_ink
def isContainer(x): return isinstance(x, Container)
@_ink
def isReversible(x): return isinstance(x, Reversible)




# # ╱╱╱╱╱╱╱╱  Generic types
# isNone      = _ink(lambda x: x is None)
# isStr       = _ink(lambda x: isinstance(x, str))
# isNum       = _ink(_not_bool(Number))
# isStrNum    = _ink(lambda x: isinstance(x, str) and re.fullmatch(r"-?\d+(?:\.\d+)?", x) is not None)
# isInt       = _ink(_not_bool(int))
# isFloat     = _ink(lambda x: isinstance(x, float))
# isComplex   = _ink(lambda x: isinstance(x, complex))
# isDict      = _ink(lambda x: isinstance(x, dict))
# isList      = _ink(lambda x: isinstance(x, list))
# isTuple     = _ink(lambda x: isinstance(x, tuple))
# isSet       = _ink(lambda x: isinstance(x, set))
# isBool      = _ink(lambda x: isinstance(x, bool))
# isByte      = _ink(lambda x: isinstance(x, bytes))
# isByteArr   = _ink(lambda x: isinstance(x, bytearray))
# isMemView   = _ink(lambda x: isinstance(x, memoryview))
# isFrozenSet = _ink(lambda x: isinstance(x, frozenset))
# isRange     = _ink(lambda x: isinstance(x, range))
# isIterable  = _ink(_iterable)

# # ╱╱╱╱╱╱╱╱  Numbers & mathy bits
# isFinite   = _ink(lambda x: isinstance(x, Number) and type(x) is not bool and math.isfinite(x))
# isInf      = _ink(lambda x: isinstance(x, Number) and not math.isfinite(x) and not math.isnan(x))
# isNaN      = _ink(lambda x: isinstance(x, Number) and math.isnan(x))
# isDecimal  = _ink(lambda x: isinstance(x, decimal.Decimal))
# isFraction = _ink(lambda x: isinstance(x, fractions.Fraction))

# # ╱╱╱╱╱╱╱╱  Dates & times
# isDate      = _ink(lambda x: isinstance(x, datetime.date) and not isinstance(x, datetime.datetime))
# isDatetime  = _ink(lambda x: isinstance(x, datetime.datetime))
# isTime      = _ink(lambda x: isinstance(x, datetime.time))
# isTimedelta = _ink(lambda x: isinstance(x, datetime.timedelta))

# # ╱╱╱╱╱╱╱╱  Paths & filesystem-ish
# isPathLike = _ink(lambda x: isinstance(x, os.PathLike))
# isPath     = _ink(lambda x: isinstance(x, pathlib.Path))
# isFile     = _ink(lambda x: isinstance(x, (str, os.PathLike)) and pathlib.Path(x).is_file())
# isDir      = _ink(lambda x: isinstance(x, (str, os.PathLike)) and pathlib.Path(x).is_dir())

# # ╱╱╱╱╱╱╱╱  Iteration protocols & callables
# isIterator   = _ink(lambda x: isinstance(x, Iterator))
# isGenerator  = _ink(lambda x: isinstance(x, Generator) or isinstance(x, GeneratorType))
# isHashable   = _ink(lambda x: isinstance(x, Hashable))
# isSized      = _ink(lambda x: isinstance(x, Sized))
# isContainer  = _ink(lambda x: isinstance(x, Container))
# isReversible = _ink(lambda x: isinstance(x, Reversible))
# isCallable   = _ink(lambda x: callable(x))
# isFunc       = _ink(lambda x: callable(x))  # alias of isCallable

# # ╱╱╱╱╱╱╱╱  Collections (generic)
# isMapping         = _ink(lambda x: isinstance(x, Mapping))
# isSequence        = _ink(lambda x: isinstance(x, Sequence) and not isinstance(x, (str, bytes, bytearray)))
# isMutableSequence = _ink(lambda x: isinstance(x, MutableSequence))
# isSetish          = _ink(lambda x: isinstance(x, Set))
# isMutableSet      = _ink(lambda x: isinstance(x, MutableSet))

# notMapping         = _not(isMapping)
# notSequence        = _not(isSequence)
# notMutableSequence = _not(isMutableSequence)
# notSetish          = _not(isSetish)
# notMutableSet      = _not(isMutableSet)

# # ╱╱╱╱╱╱╱╱  Regex, enums, modules, functions/methods, slices
# isRegex   = _ink(lambda x: isinstance(x, _RePattern))
# isMatch   = _ink(lambda x: isinstance(x, _ReMatch))
# isEnum    = _ink(lambda x: isinstance(x, enum.Enum))
# isEnumCls = _ink(lambda x: isinstance(x, type) and issubclass(x, enum.Enum))

# isModule  = _ink(lambda x: isinstance(x, ModuleType))
# isFunction= _ink(lambda x: isinstance(x, FunctionType))
# isMethod  = _ink(lambda x: isinstance(x, MethodType))

# isSlice   = _ink(lambda x: isinstance(x, slice))
# isEllipsis= _ink(lambda x: x is Ellipsis)

# notRegex    = _not(isRegex)
# notMatch    = _not(isMatch)
# notEnum     = _not(isEnum)
# notEnumCls  = _not(isEnumCls)
# notModule   = _not(isModule)
# notFunction = _not(isFunction)
# notMethod   = _not(isMethod)
# notSlice    = _not(isSlice)
# notEllipsis = _not(isEllipsis)

# # ╱╱╱╱╱╱╱╱  Bytes-like, dataclasses, JSON-ish strings
# isBytesLike  = _ink(lambda x: isinstance(x, (bytes, bytearray, memoryview)))
# isDataclass  = _ink(dataclasses.is_dataclass)  # True for dataclass *instances or classes*
# isDataclassInstance = _ink(lambda x: dataclasses.is_dataclass(x) and not isinstance(x, type))

# notBytesLike         = _not(isBytesLike)
# notDataclass         = _not(isDataclass)
# notDataclassInstance = _not(isDataclassInstance)

# # ╱╱╱╱╱╱╱╱  Length/emptiness (handy in practice)
# isEmpty    = _ink(lambda x: hasattr(x, "__len__") and len(x) == 0)
# isNonEmpty = _ink(lambda x: hasattr(x, "__len__") and len(x) > 0)

# notEmpty    = _not(isEmpty)
# notNonEmpty = _not(isNonEmpty)

# # ╱╱╱╱╱╱╱╱  strict ASCII
# isAscii   = _ink(lambda x: isinstance(x, str) and x.isascii())
# notAscii  = _not(isAscii)

# # ╱╱╱╱╱╱╱╱  printable (no control chars)
# isPrintable  = _ink(lambda x: isinstance(x, str) and x.isprintable())
# notPrintable = _not(isPrintable)

# # ╱╱╱╱╱╱╱╱  iterable/iterator-ish
# hasLen        = _has_dund('__len__')
# hasIter       = _has_dund('__iter__')
# hasNext       = _has_dund('__next__') # iterator protocol
# hasReversed   = _has_dund('__reversed__')
# hasContains   = _has_dund('__contains__')
# hasGetItem    = _has_dund('__getitem__')
# hasSetItem    = _has_dund('__setitem__')
# hasDelItem    = _has_dund('__delitem__')

# # ╱╱╱╱╱╱╱╱  callability & conversion
# hasCall       = _has_dund('__call__') # alias of isCallable
# hasBool       = _has_dund('__bool__')
# hasIndex      = _has_dund('__index__')
# hasInt        = _has_dund('__int__')
# hasFloat      = _has_dund('__float__')
# hasComplex    = _has_dund('__complex__')
# hasStr        = _has_dund('__str__')
# hasRepr       = _has_dund('__repr__')
# hasFormat     = _has_dund('__format__')

# # ╱╱╱╱╱╱╱╱  arithmetic / comparisons
# hasHash       = _ink(lambda x: getattr(type(x), '__hash__', None) is not None and x.__hash__ is not None)
# hasEq         = _has_dund('__eq__')
# hasOrder      = _ink(lambda x: any(callable(getattr(x, m, None)) for m in ('__lt__','__le__','__gt__','__ge__')))
# hasAdd        = _has_dund('__add__')
# hasRAdd       = _has_dund('__radd__')
# hasMul        = _has_dund('__mul__')
# hasRMul       = _has_dund('__rmul__')
# hasMatmul     = _has_dund('__matmul__')
# hasPow        = _has_dund('__pow__')
# hasSub        = _has_dund('__sub__')
# hasTruediv    = _has_dund('__truediv__')
# hasMod        = _has_dund('__mod__')
# hasNeg        = _has_dund('__neg__')
# hasPos        = _has_dund('__pos__')
# hasAbs        = _has_dund('__abs__')

# # ╱╱╱╱╱╱╱╱  context managers / async protocols
# hasEnter      = _has_dund('__enter__')
# hasExit       = _has_dund('__exit__')
# isContextMgr  = _ink(lambda x: callable(getattr(x,'__enter__',None)) and callable(getattr(x,'__exit__',None)))

# hasAEnter     = _has_dund('__aenter__')
# hasAExit      = _has_dund('__aexit__')
# isAsyncCtxMgr = _ink(lambda x: callable(getattr(x,'__aenter__',None)) and callable(getattr(x,'__aexit__',None)))

# isAwaitable   = _has_dund('__await__')
# hasAIter      = _has_dund('__aiter__')
# hasANext      = _has_dund('__anext__')

# # ╱╱╱╱╱╱╱╱  attribute hooks / descriptors
# hasGetAttr        = _has_dund('__getattr__')
# hasGetAttribute   = _has_dund('__getattribute__')
# hasSetAttr        = _has_dund('__setattr__')
# hasDelAttr        = _has_dund('__delattr__')
# isDescriptor      = _ink(lambda x: any(callable(getattr(x, m, None)) for m in ('__get__','__set__','__delete__')))
# hasGet            = _has_dund('__get__')
# hasSet            = _has_dund('__set__')
# hasDelete         = _has_dund('__delete__')

# # ╱╱╱╱╱╱╱╱  class/instance metadata
# hasDict       = _ink(lambda x: hasattr(x, '__dict__'))
# hasSlots      = _ink(lambda x: hasattr(x, '__slots__') or hasattr(type(x), '__slots__'))
# hasAnnotations= _ink(lambda x: hasattr(x, '__annotations__'))
# hasName       = _ink(lambda x: hasattr(x, '__name__'))          # funcs, classes
# hasMRO        = _ink(lambda x: hasattr(x, '__mro__') or hasattr(type(x), '__mro__'))

# # ╱╱╱╱╱╱╱╱  filesystem-ish
# hasFspath     = _has_dund('__fspath__')   # PathLike protocol






# def isNone(v): return v is None
# def notNone(v): return v is not None

# def isStr(v): return isinstance(v, str)
# def notStr(v): return not isStr(v)
# def isNum(v): return isinstance(v, Number) and not isinstance(v, bool)
# def notNum(v): return not isNum(v)
# def isStrNum(v): return isinstance(v, str) and re.fullmatch(r"-?\d+(?:\.\d+)?", v)
# def notStrNum(v): return not isStrNum(v)

# def isInt(v, *k): return isinstance(v, int) and not isinstance(v, bool)
# def notInt(v): return not isInt(v)
# def isFloat(v): return isinstance(v, float)
# def notFloat(v): return not isFloat(v)
# def isComplex(v): return isinstance(v, complex)
# def notComplex(v): return not isComplex(v)

# def isDict(v): return isinstance(v, dict)
# def notDict(v): return not isDict(v)
# def isList(v): return isinstance(v, list)
# def notList(v): return not isList(v)
# def isTuple(v): return isinstance(v, tuple)
# def notTuple(v): return not isTuple(v)
# def isSet(v): return isinstance(v, set)
# def notSet(v): return not isSet(v)
# def isBool(v): return isinstance(v, bool)
# def notBool(v): return not isBool(v)
# def isByte(v): return isinstance(v, bytes)
# def notByte(v): return not isByte(v)
# def isByteArr(v): return isinstance(v, bytearray)
# def notByteArr(v): return not isByteArr(v)
# def isMemView(v): return isinstance(v, memoryview)
# def notMemView(v): return not isMemView(v)
# def isFunc(v): return callable(v)
# def notFunc(v): return not callable(v)
# def isFrozenSet(v): return isinstance(v, frozenset)
# def notFrozenSet(v): return not isFrozenSet(v)
# def isRange(v): return isinstance(v, range)
# def notRange(v): return not isRange(v)
# def isIterable(v):
#     try:
#         iter(v)
#         return True
#     except TypeError: return False
# def notIterable(x): return not isIterable(x)




def isMapWith(m, *k): return isinstance(m, Mapping) and all(key in m for key in k)




_HEX_RE          = re.compile(r"^[0-9a-f]+$", re.IGNORECASE)
_HEX_COLOR_RE    = re.compile(r"^#(?:[0-9a-f]{3}|[0-9a-f]{4}|[0-9a-f]{6}|[0-9a-f]{8})$", re.IGNORECASE)
_HEX_PREFIXED_RE = re.compile(r"^0x[0-9a-f]+$", re.IGNORECASE)

# True if x is hex with or without a 0x/0X prefix, e.g. 'deadBEEF' or '0xdeadBEEF'
def isHex(x: Any) -> bool: return isStr(x) and _HEX_RE.fullmatch(x) is not None

# True if x is a hex string of even length, e.g. '00ff10'.
def isHexEven(x: Any) -> bool: return isStr(x) and (len(x) % 2 == 0) and _HEX_RE.fullmatch(x) is not None

# True if x is a CSS-style hex color: #RGB, #RGBA, #RRGGBB, or #RRGGBBAA.
def isHexColor(x: Any) -> bool: return isStr(x) and _HEX_COLOR_RE.fullmatch(x) is not None

# True if x is a '0x' prefixed hex string, e.g. '0x1a2b3c'
def isHexPrefixed(x: Any) -> bool: return isStr(x) and _HEX_PREFIXED_RE.fullmatch(x) is not None




def _asList(val): return list(val) if isList(val) or isTuple(val) or isSet(val) else [val]

def _bitmaskMatch(a, b):
    try: return isInt(a) and isInt(b) and ((a & b) != 0)
    except Exception: return False


def hasSome(arr1, arr2):
    if isDict(arr1): # Dict checks
        keys = set(arr1.keys())
        search = _asList(arr2)
        return any(k in keys for k in search)
    if isDict(arr2):
        search = set(arr2.keys())
        arr = _asList(arr1)
        return any(a in search for a in arr)
    arr = _asList(arr1)
    search = _asList(arr2)
    for a in arr:
        for b in search:
            if a == b or _bitmaskMatch(a, b): return True
    return False




def hasAll(arr1, arr2):
    if isDict(arr1): # Dict checks
        keys = set(arr1.keys())
        search = _asList(arr2)
        return all(k in keys for k in search)
    if isDict(arr2):
        search = set(arr2.keys())
        arr = _asList(arr1)
        return all(a in search for a in arr)
    arr = _asList(arr1)
    search = _asList(arr2)
    for b in search:
        found = False
        for a in arr:
            if a == b or _bitmaskMatch(a, b):
                found = True
                break
        if not found: return False
    return True




def hasNone(arr1, arr2):
    if isDict(arr1): # Dict checks
        keys = set(arr1.keys())
        search = _asList(arr2)
        return all(k not in keys for k in search)
    if isDict(arr2):
        search = set(arr2.keys())
        arr = _asList(arr1)
        return all(a not in search for a in arr)
    arr = _asList(arr1)
    search = _asList(arr2)
    for a in arr:
        for b in search:
            if a == b or _bitmaskMatch(a, b): return False
    return True




# Return True if any pattern in `patterns` is found in `seq`.
#   Set isContiguous=False to not require matches to appear contiguously in the sequence
#   Set isFirst=True to require first match start at the first element of the sequence
#   Set isLast=True to require last match end at the last element of the sequence
#
def hasSublist(sequence, *pattern, isContiguous=True, isFirst=False, isLast=False) -> bool:
    if not pattern: return False # empty pattern -> no match
    m, n = len(pattern), len(sequence)

    # Return True if all items of `pattern` appear in `seq` in order,
    # will return True even if the sequence is non-contiguous.
    def _has_subsequence(seq, *pat) -> bool:
        it = iter(seq)
        return all(p in it for p in pat)
    
    # Return True if `pattern` appears contiguously inside `seq`.
    # will return False if the sequence is non-contiguous.
    def _has_contiguous(seq, *pat) -> bool:
        if len(pat) > len(seq): return False
        return any(seq[i:i+len(pat)] == list(pat) for i in range(len(seq) - len(pat) + 1))
    
    if isFirst: # Start-anchored: pattern must begin at index 0.
        if isContiguous:
            if sequence[:m] == list(pattern): return True
        else: # subsequence anchored at start: first items equal, rest appear in order later
            if n >= m and sequence[0] == pattern[0] and _has_subsequence(sequence[1:], pattern[1:]): return True
    
    if isLast: # End-anchored: pattern must end at the final element.
        if isContiguous:
            if sequence[-m:] == list(pattern): return True
        else: # subsequence anchored at end: last items equal, earlier items appear in order before
            if n >= m and sequence[-1] == pattern[-1] and _has_subsequence(sequence[:-1], pattern[:-1]): return True
            
    if isContiguous: return _has_contiguous(sequence, pattern)
    else: return _has_subsequence(sequence, pattern)




def _normalize_str(s: str) -> str:
    chars = { 'ëéèê': 'e', 'áàâ': 'a', 'öô': 'o', 'üû': 'u', 'ç': 'c' }
    s = s.lower()
    for chars, rep in chars.items(): s = re.sub(f"[{re.escape(chars)}]", rep, s)
    return s




def slugStr(input: str) -> str:
    if not input: return ''
    slug = _normalize_str(str(input))
    slug = re.sub(r'[\s-]', '_', slug)      # Convert spaces/dashes to underscores
    slug = re.sub(r'[^a-z0-9_]', '', slug)  # Remove all except a-z, 0-9, _
    slug = re.sub(r'_+', '_', slug)         # Collapse multiple underscores
    return slug




def camelLowercase(input: str) -> str:
    if not input: return ''
    s = _normalize_str(input)
    pts = re.split(r'[\s_\-]+', s) # Split on spaces, underscores, or dashes
    pts = [pts[0]] + [p.capitalize() for p in pts[1:]] # Capitalize all but the first part
    return ''.join(pts)




def camelUppercase(input: str) -> str:
    if not input: return ''
    s = _normalize_str(input)
    pts = re.split(r'[\s_\-]+', s)
    pts = [p.capitalize() for p in pts]
    return ''.join(pts)




# Convert camelCase / PascalCase (and mixed strings) to snake_case.
# - Adds '_' before capital letters when transitioning from [a-z0-9] -> [A-Z]
# - Splits acronyms before a capital+lowercase boundary (e.g., HTTPServer -> HTTP_Server)
# - Replaces spaces/dashes with '_'
# - Collapses multiple underscores
def camelSnake(input: str) -> str:
    if not input: return ''
    s = str(input).strip()
    s = re.sub(r'[\s\-]+', '_', s) # Normalize spacers to underscores first
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', s) # Split "acronym"+"Word" like "HTTPServer" -> "HTTP_Server"
    s = re.sub(r'(?<=[a-z0-9])([A-Z])', r'_\1', s) # uscore before uppers that follow a lower: "myVar1X" -> "my_Var1_X"
    s = re.sub(r'_+', '_', s) # Collapse multiple underscores
    return s.lower() # lowercase




def snakeCase(input: str, replace_hyphens: bool = False) -> str:
    if not input: return ''
    s = str(input).lower()
    s = s.replace(" ", "_") # Replace spaces, and optionally hyphens, with underscores
    if replace_hyphens: s = s.replace("-", "_")
    s = re.sub(r"[^a-z0-9_]", "", s) # Remove all characters except a-z, 0-9, and underscores
    s = re.sub(r"_+", "_", s).strip("_") # Collapse extra underscores
    return s.strip("_").lower() # Lowercase and trim stray underscores from ends




def getInitials(input: str) -> str: return ''.join(word[0].upper() for word in input.split() if word)




def getAlphnum(input: str) -> str: return re.sub(r'[^a-zA-Z0-9]', '', input)




def unslugStr(input: str) -> str:
    result = input.replace('_', ' ')
    result = re.sub(r'([a-z])([A-Z])', r'\1 \2', result)
    result = re.sub(r'([^ ])([A-Z])', r'\1 \2', result)
    result = re.sub(r'\s{2,}', ' ', result)
    return result.strip()




# Keep the first entry seen for each key value.
# Entries missing the key are kept and NOT deduped.
def dedupeKeepFirst(entries: Iterable[Dict[str, Any]], key: str, loud: bool = False) -> List[Dict[str, Any]]:
    seen = set()
    out: List[Dict[str, Any]] = []
    for e in entries:
        if key not in e:
            out.append(e)
            continue
        k = e[key]
        if k in seen: 
            if loud: print(f"\n\033[31m\033[1m🚩 DUPE SKIPPED:\033[0m {k}\n")
            continue
        seen.add(k)
        out.append(e)
    return out




# Keep the last entry seen for each key value.
# Entries missing the key are kept and NOT deduped, in original order.
def dedupeKeepLast(entries: Iterable[Dict[str, Any]], key: str, loud: bool = False) -> List[Dict[str, Any]]:
    last_index: Dict[Any, int] = {} # First pass: remember last index for each key value
    entries_list = list(entries)
    for i, e in enumerate(entries_list):
        if key in e: last_index[e[key]] = i
    out: List[Dict[str, Any]] = [] # Second pass: keep if missing key or this is the last occurrence
    for i, e in enumerate(entries_list):
        if key not in e: out.append(e)
        elif last_index.get(e[key]) == i: out.append(e)
    return out





# Build a lookup table (dict) where each item is stored under the string form
# of the given key. Supports dictionaries or objects with attributes.
#
# - If an item is a dict, it must contain `key`.
# - If an item is an object, it must have attribute `key`.
# - If duplicate keys occur:
#     * Always reported to console.
#     * If keepFirst is True -> keep the existing entry, skip the new one.
#     * If keepFirst is False -> overwrite with the new item (last wins).
#
# Raises:
#     KeyError: if an item lacks the required key/attribute.
#
def convertToLUT(
    items: Iterable[Any], key: str, 
    keepFirst: bool = False, loud: bool = False, fail: bool = False, strKeys: bool = True
) -> Dict[str, Any]:
    iDef = f"[util::convertToLUT]  ➔  "
    def pr_sum(text: str): print(iDef + text) if loud else ''
    lut: Dict[str, Any] = {}
    dupes = Counter()
    for idx, item in enumerate(items): # Extract the key value
        iE = f"{iDef}Item at index {idx}"
        if isinstance(item, dict):
            if key not in item: raise KeyError(f"{iE} is missing key '{str(key)}'")
            raw = item[key]
        else:
            if not hasattr(item, key): raise KeyError(f"{iE} has no attribute '{str(key)}'")
            raw = getattr(item, key)
        k = raw if isinstance(raw, int) else str(raw)
        if k in lut: # Handle duplicates
            iW = f"Duplicate '{str(k)}' at index {idx}:"
            dupes[k] += 1
            if keepFirst:
                pr_sum(f"{iW} kept existing, skipped new.")
                continue
            else: pr_sum(f"{iW} overwrote existing with new.")
        lut[str(k) if strKeys else k] = item
    if dupes: # Summary
        total = sum(dupes.values())
        pr_sum(f"Duplicate summary: {total} duplicates across {len(dupes)} key(s).")
        for dk, count in dupes.most_common(): pr_sum(f"  key '{dk}': {count} extra occurrence(s)")
    else: pr_sum("No duplicates found.")
    return lut






# Convert a lookup table (dict) back to a list of items.
#
# If `key` is provided, the LUT key for each entry is injected into the item
# when missing:
#   - If the item is a dict and `key` not in item, a new dict is created with
#     {key: <lut_key>} inserted first, followed by the original fields.
#   - If the item is an object and doesn't have attribute `key`, an attribute
#     with that name is set to <lut_key>. If setting the attribute fails, the
#     item is left unchanged.
#
# Notes:
#     - The returned list preserves the insertion order of `lut` (Python 3.7+).
#     - Dict items are not mutated; a new dict is created when injection happens.
#     - Object items may be mutated (attribute set) if they allow it.
#
# Args:
#     lut: Mapping from string/int keys to items (dicts or objects).
#     key: Optional field/attribute name to store each entry's LUT key.
#
# Returns:
#     A list of the LUT's values, with optional key injection as described.
#
def convertFromLUT(
    lut: Mapping[Union[str, int], Any],
    key: str | None = None,
) -> List[Any]:
    out: List[Any] = []
    for lut_key, item in lut.items():
        if key is not None:
            if isinstance(item, dict):
                if key not in item:
                    # Insert the LUT key as the first field without mutating the original dict
                    new_item = {key: lut_key}
                    new_item.update(item)
                    out.append(new_item)
                    continue
            else:
                # For objects, set attribute if missing; ignore failures on immutable/locked objects
                if not hasattr(item, key):
                    try: setattr(item, key, lut_key)
                    except Exception: pass
        out.append(item)
    return out






def serialize(v: Any) -> str:
    try: return json.dumps(v, ensure_ascii=False)
    except (TypeError, ValueError): return str(v)






# Sort `items` (list or dict) by the value at `key` using:
#   - Numbers: numeric order
#   - Strings: alphabetical (case-insensitive)
#   - Others: by length of their string serialization
# Mixed types are grouped in this fixed order: Any -> String -> Number.
# `ascending` applies within each group (group order is fixed).
# Returns a new sorted object (does not mutate input).
def sortByKey(items, key: str, reverse: bool = False):
    def get_value(obj): return obj.get(key, None) if isinstance(obj, Mapping) else getattr(obj, key, None)
    any_group = []
    str_group = []
    num_group = []
    
    if isinstance(items, Mapping): # Normalize to (k, v) pairs where v is the sortable element
        pairs = list(items.items())
        assign = lambda item, grp: grp.append(item)
        value_of = lambda item: get_value(item[1])
        rebuild_dict = True
    else:
        pairs = list(enumerate(items))  # keep stable identity via index
        assign = lambda item, grp: grp.append(item)
        value_of = lambda item: get_value(item[1])
        rebuild_dict = False

    for pair in pairs:
        v = value_of(pair)
        if isStr(v): assign(pair, str_group)
        elif isNum(v): assign(pair, num_group)
        else: assign(pair, any_group)

    def sort_any(grp): return sorted(grp, key=lambda p: len(serialize(value_of(p))), reverse=reverse)
    def sort_str(grp): return sorted(grp, key=lambda p: (value_of(p) or "").casefold(), reverse=reverse)
    def sort_num(grp): return sorted(grp, key=lambda p: float(value_of(p)), reverse=reverse)
    sorted_pairs = (sort_any(any_group) + sort_str(str_group) + sort_num(num_group))
    if rebuild_dict: return dict(sorted_pairs)
    else: return [p[1] for p in sorted_pairs]




# Return a new list of dicts sorted alphabetically by the 'name' key.
# - Case-insensitive
# - Dicts with missing/None 'name' are placed last
# - Works even if 'name' isn't a string (it will be stringified)
def sort_by_name(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def keyfunc(d: Dict[str, Any]):
        name = d.get("name", None)
        is_missing = name is None
        # casefold for robust, locale-agnostic case-insensitive sorting
        return (is_missing, "" if is_missing else str(name).casefold())
    return sorted(items, key=keyfunc)




# Sum-like function for 'flat' data:
#   - int/float -> value
#   - str -> len(str)
#   - list/tuple -> len(container)
#   - set/frozenset -> len(container)
#   - dict -> sum of processed values
#   - anything else -> 0
def sumObjectFlat(obj):
    if isinstance(obj, (int, float)): return obj # numbers
    if isinstance(obj, str): return len(obj) # strings
    if isinstance(obj, Mapping): # mappings (dict-like): sum their values
        total = 0
        for v in obj.values(): total += sumObjectFlat(v)
        return total
    # sequences or sets (but not strings, handled above)
    # this catches list, tuple, range, etc.
    if isinstance(obj, (Sequence, Set)) and not isinstance(obj, (str, bytes, bytearray)): return len(obj)
    return 0 # fallback for unknown types