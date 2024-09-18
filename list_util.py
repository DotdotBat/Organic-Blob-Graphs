from typing import List

def rotate_list(l:List, rot_amount:int):
    if l == []:
        return []
    rot_amount %= len(l)
    l = l[rot_amount:] + l[:rot_amount]
    return l