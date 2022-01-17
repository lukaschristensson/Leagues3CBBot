def pad_0(s):
    while len(s) < 3: s = '0'+s
    return s
def lighten_color(c, amount):
    if amount > 1: return c
    r, g, b = int(c[1:4], 16), int(c[4:7], 16), int(c[7:10], 16)

    max_val = (16*16*15 + 16*15 + 15)
    # lighten by moving every value closer to max val proportionate to their distance to the max
    lighter = r + (max_val - r)*amount, g + (max_val - g)*amount, b + (max_val - b)*amount

    return '#' + pad_0(hex(int(lighter[0]))[2:]) + pad_0(hex(int(lighter[1]))[2:]) + pad_0(hex(int(lighter[2]))[2:])

def intensify(c, amount):
    r, g, b = int(c[1:4], 16), int(c[4:7], 16), int(c[7:10], 16)
    max_val = (16*16*15 + 16*15 + 15)
    # intensifying by multiplying every value with a certain value
    intensified = min(max_val, r*amount), min(max_val, g*amount), min(max_val, b*amount)

    return '#' + pad_0(hex(int(intensified[0]))[2:]) + pad_0(hex(int(intensified[1]))[2:]) + pad_0(hex(int(intensified[2]))[2:])

def mix_color(c1, c2, amount):
    if amount > 1: return c1
    r1, g1, b1 = int(c1[1:4], 16), int(c1[4:7], 16), int(c1[7:10], 16)
    r2, g2, b2 = int(c2[1:4], 16), int(c2[4:7], 16), int(c2[7:10], 16)
    mixed = r1*amount + r2*(1-amount), g1*amount + g2*(1-amount), b1*amount + b2*(1-amount)
    return '#' + pad_0(hex(int(mixed[0]))[2:]) + pad_0(hex(int(mixed[1]))[2:]) + pad_0(hex(int(mixed[2]))[2:])