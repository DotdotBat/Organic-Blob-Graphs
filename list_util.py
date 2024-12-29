from typing import List

def rotate_list(l:List, rot_amount:int):
    "rotation amount = i then the ith element will become the first in the list"
    if l == []:
        return []
    rot_amount %= len(l)
    l = l[rot_amount:] + l[:rot_amount]
    return l