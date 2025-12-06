import json
from utils.util import hasSome, isDict, isList, isNone, isStr
__all__ = [name for name in dir() if not name.startswith("_")]



# oneLineLenMax = 128 # 112


class _Inline:
    __slots__ = ("value",)
    def __init__(self, value): self.value = value

def _collapse_for_render(obj, level=0, root_array_level=None, *, oneLineLenMax=128):
    def json_one_line(x):
        s = json.dumps(x, ensure_ascii=False, separators=(', ', ': '))
        if isinstance(x, dict):  return "{ " + s[1:-1] + " }"
        if isinstance(x, list):  return "[ " + s[1:-1] + " ]"
        return s

    if isinstance(obj, dict):
        if (root_array_level is None or level != root_array_level + 1):
            one_liner = json_one_line(obj)
            if len(one_liner) <= oneLineLenMax:
                return _Inline(obj)                         # wrapper only for rendering
        return {k: _collapse_for_render(v, level+1, root_array_level, oneLineLenMax=oneLineLenMax)
                for k, v in obj.items()}

    if isinstance(obj, list):
        next_root = root_array_level if root_array_level is not None else (0 if level == 0 else None)
        return [_collapse_for_render(v, level+1, next_root, oneLineLenMax=oneLineLenMax) for v in obj]

    return obj

def render_json(objRaw, indent=2, level=0, *, oneLineLenMax=112, collapse=True):
    # Build a temporary, collapsed view purely for rendering
    obj = _collapse_for_render(objRaw, oneLineLenMax=oneLineLenMax) if collapse else objRaw

    # Inline nodes: print their payload on one line w/o quotes
    if isinstance(obj, _Inline):
        val = obj.value
        s = json.dumps(val, ensure_ascii=False, separators=(', ', ': '))
        if isinstance(val, dict):  return "{ " + s[1:-1] + " }"
        if isinstance(val, list):  return "[ " + s[1:-1] + " ]"
        return s  # scalar

    # Flat list of numbers
    if isinstance(obj, list) and all(isinstance(n, (int, float)) for n in obj):
        flat = json.dumps(obj, ensure_ascii=False, separators=(', ', ': '))
        if len(flat) <= oneLineLenMax: return flat

    # Nested list of number lists
    if isinstance(obj, list) and all(isinstance(s, list) and all(isinstance(n, (int, float)) for n in s) for s in obj):
        flat = json.dumps(obj, ensure_ascii=False, separators=(', ', ': '))
        if len(flat) <= oneLineLenMax: return flat

    if isinstance(obj, list):
        lines = ["["]
        for i, item in enumerate(obj):
            s = render_json(item, indent, level+1, oneLineLenMax=oneLineLenMax, collapse=False)
            s_lines = s.splitlines()
            if len(s_lines) == 1:
                lines.append(" " * ((level+1) * indent) + s_lines[0] + ("," if i < len(obj) - 1 else ""))
            else:
                lines.append(" " * ((level+1) * indent) + s_lines[0])
                for subline in s_lines[1:-1]:
                    lines.append(subline)
                lines.append(" " * ((-level) * indent) + s_lines[-1] + ("," if i < len(obj) - 1 else ""))
                # lines.append(" " * ((level+1) * indent) + s_lines[-1] + ("," if i < len(obj) - 1 else ""))
        lines.append(" " * (level * indent) + "]")
        return "\n".join(lines)

    if isinstance(obj, dict):
        items = []
        for k, v in obj.items():
            items.append(json.dumps(k, ensure_ascii=False) + ": " +
                         render_json(v, indent, level+1, oneLineLenMax=oneLineLenMax, collapse=False))
        if not items: return "{}"
        sep = ",\n" + " " * ((level+1) * indent)
        return "{\n" + " " * ((level+1)*indent) + sep.join(items) + "\n" + " " * (level*indent) + "}"

    # scalars
    return json.dumps(obj, ensure_ascii=False)






# For each dict in arr, shift the given keys as a group by 'steps' positions.
# Maintains the order and stops at the start/end as needed.
def shiftKeys(arr, keys, steps):
    if isDict(arr): arr = [arr]
    if isStr(keys): keys = [keys]
    for obj in arr:
        all_keys = list(obj.keys()) # Maintain order with list of keys (including order in obj)
        key_indices = [all_keys.index(k) for k in keys if k in obj] # Indices of keys to shift (in their current order)
        if not key_indices: continue  # None of the keys present, nothing to shift
        start, end = key_indices[0], key_indices[-1] + 1 # Group start/end index in all_keys
        group = all_keys[start:end]
        del all_keys[start:end] # Remove group from all_keys
        max_left = 0 # Compute new position
        max_right = len(all_keys)
        if steps < 0: new_pos = max(max_left, start + steps)
        else: new_pos = min(max_right, start + steps)
        all_keys = all_keys[:new_pos] + group + all_keys[new_pos:] # Insert group at new position
        items = [(k, obj[k]) for k in all_keys if k in obj] # Rebuild obj with new order
        for k in keys:
            if k in obj and k not in all_keys: items.append((k, obj[k]))  # Add missing keys if any
        obj.clear()
        obj.update(items)
    return arr






def removeKeys(item, keys):
    if isStr(keys): keys = [keys]
    if isDict(item):
        for k in keys: 
            if k in item: del item[k]
    elif isList(item):
        for obj in item:
            for k in keys: 
                if k in obj: del obj[k]
    return item






def renameKey(item, keyOld, keyNew):
    if keyOld in item:
        item[keyNew] = item[keyOld]
        del item[keyOld]
    return item






# For each dict in arr, combines values from srcKeys into a list assigned to destKey.
# The source keys are removed from the dict.
# If a source key is missing, uses `default` value.
def arrayKeys(arr, srcKeys, destKey, default=0):
    for o in arr: o[destKey] = [o.pop(k, default) for k in srcKeys]
    return arr
            





# For each dict in arr, add PRIORITY: 0 as the first key.
# Returns the updated array.
def prependPriority(arr):
    updated = []
    for obj in arr:
        if not isinstance(obj, dict):
            updated.append(obj)
            continue
        new_obj = {'PRIORITY': 0} # Insert PRIORITY at the top
        new_obj.update(obj)
        updated.append(new_obj)
    return updated






# For each object in arr1, step through all objects in arr2.
# For each match between obj1[key1] == obj2[key2], increment obj1['PRIORITY'] by 1.
# Modifies arr1 in place, returns arr1.
def incrementPriority(arr1, key1, arr2, key2):
    for obj1 in arr1:
        if not isinstance(obj1, dict) or "PRIORITY" not in obj1: continue
        for obj2 in arr2:
            if not isinstance(obj2, dict): continue
            if obj1.get(key1) == obj2.get(key2): obj1["PRIORITY"] += 1
    return arr1






# Returns a new list with objects from arr sorted by the value of 'key'.
# If the key is missing, those objects will appear last.
def sortByID(arr, idKey):
    return sorted(arr, key=lambda obj: obj.get(idKey, float('inf')))






# Sorts objects in arr by descending completion score.
# Returns the sorted list.
def sortByCompletion(arr):
    def get_completion_score(o):
        score = 0
        if isNone(o): score -= 1000
        elif isinstance(o, bool):
            if o == True: score += 10
            score += 10
        elif isinstance(o, dict):
            for v in o.values(): score += get_completion_score(v)
            score += len(o)
        elif isinstance(o, list):
            for i in o: score += get_completion_score(i)
            score += len(o)
        elif isinstance(o, int): 
            if o > 0: score += len(f"{o}") * 4
            else: score -= 100
        elif isinstance(o, float): score += len(f"{o}")
        elif isinstance(o, str):
            if "unknown" in o.lower(): score -= len(o)
            elif len(o) > 0: score += len(o)
            else: score -= 100
        
        return score
    return sorted(arr, key=get_completion_score, reverse=True)






# For each object in list1, finds the first object in list2 where obj1[match_key] == obj2[match_key].
# Adds the matched obj2 as the value of assign_key in obj1.
# If not found, assigns 𝗨𝗡𝗗𝗘𝗙𝗜𝗡𝗘𝗗 to assign_key.
# Returns the new list of merged objects.
def mergeLists(list1, key1, list2, key2="", newKey="", defaultTo={}, keepKey1=True, keepKey2=True):
    # PR_PROC_INIT('mergeLists', f"[{len(list1)}] {key1}  ➡  [{len(list2)}] {key2}")
    result = []
    if key2 == "": key2 = key1
    for obj1 in list1:
        found = False
        for obj2 in list2:
            if obj1.get(key1) == obj2.get(key2):
                
                if keepKey1: newObj1 = obj1.copy()
                else: newObj1 = {k: v for k, v in obj1.items() if k != key1}
                # newObj1 = {k: v for k, v in newObj1.items() if k != "PRIORITY"}

                if keepKey2: newObj2 = obj2.copy()
                else: newObj2 = {k: v for k, v in obj2.items() if k != key2}
                # newObj2 = {k: v for k, v in newObj2.items() if k != "PRIORITY"}
                
                if newKey == "": newObj1.update(newObj2) # Copy all keys from obj2_copy into merged_obj (overwriting)
                else: newObj1[newKey] = newObj2
                result.append(newObj1)
                found = True
                break
        if not found:
            if keepKey1: newObj1 = obj1.copy()
            else: newObj1 = {k: v for k, v in obj1.items() if k != key1}
            # newObj1 = {k: v for k, v in newObj1.items() if k != "PRIORITY"}
            if newKey == "": newObj1.update(defaultTo) # No match, no merge: do nothing
            # else: newObj1[newKey] = "𝗨𝗡𝗗𝗘𝗙𝗜𝗡𝗘𝗗"
            else: newObj1[newKey] = None
            result.append(newObj1)
    return result