from math import log, exp, ceil

# def translate(value, leftMin, leftMax, rightMin, rightMax):
#     # Figure out how 'wide' each range is
#     leftSpan = leftMax - leftMin
#     rightSpan = rightMax - rightMin
#
#     # Convert the left range into a 0-1 range (float) basically % of left scale
#     valueScaled = float(value - leftMin) / float(leftSpan)
#     b=10
#     logmax = log(rightMax / rightMin, 10)
#     X = Xmax * log(V / Vmin, b) / logmax
#     V = Vmin * b ** (logmax * X / Xmax)
#
#
#     # Convert the 0-1 range into a value in the right range.
#     return rightMin + (valueScaled * rightSpan)
def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return ceil(rightMin + (valueScaled * rightSpan))

def inttodb(value, linMin, linMax, dbMin, dbMax):
    linSpan = linMax - linMin
    dbSpan = dbMax - dbMin

    linRatio = float(value - linMin) /float(linSpan)

    b = log(abs(float(dbMax)/float(dbMin)), 10) / float(dbSpan)

    dbVal = dbMax/exp(b * linMax)

''' 0.5 = 512
    0.25 = 255
    0.0625 = 64
'''

def int_to_db_X32( value ):
    if value >= 512:
        d = ((value/1024) * 40.0) - 30.0
    elif value >= 256:
        d = ((value/1024) * 80.0) - 50.0
    elif value >= 64:
        d = ((value/1024) * 160.0) - 70.0
    elif value > 0:
        d = ((value/1024) * 480.0) - 90.0
    elif value == 0:
        d = -90
    return d


if __name__ == "__main__":
    print(int_to_db_X32(1))
    for y in range(0, 1024, 100):
        x = int_to_db_X32(y)
        print(x)
    for y in range(0, 1024, 100):
        x = translate(y, 0, 1023, 0, 127)
        print(x)
    for y in range(-10, 10):
        print('{0:>0.2f}'.format(y))