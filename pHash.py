import cv2, numpy as np, os, time

def pHash(fn):
    gray = cv2.imread(fn, 0)
    if gray is None: return None
    gray = cv2.blur(gray, (7,7))
    gray = cv2.resize(gray, (32,32))
    gray = cv2.dct(np.asarray(gray, np.float))
    vec = gray[1:9, 1:9].flatten()
    median = np.median(vec)
    hash_val = 0
    for v in vec:
        if v > median:
            hash_val |= 1
        hash_val = hash_val << 1
    return hash_val
    
def hamming_dist(hash1, hash2):
    x = hash1^hash2
    m1  = 0x5555555555555555
    m2  = 0x3333333333333333
    h01 = 0x0101010101010101
    m4  = 0x0f0f0f0f0f0f0f0f
    x -= (x >> 1) & m1
    x = (x & m2) + ((x >> 2) & m2)
    x = (x + (x >> 4)) & m4
    return (x*h01)>>56 & 0xff

def test():
    for dirPath, dirNames, fileNames in os.walk('var/compr'):
        for f in fileNames:
            a = os.path.join(dirPath, f)
            hash_a = pHash(a)

            for cat in ['var/rotd', 'var/blur', 'var/misc']:
                b = os.path.join(cat, f[:-3]+'bmp')
                hash_b = pHash(b)
                print hamming_dist(hash_a, hash_b), '\t', b

ts = time.time()
test()
print '%2.2f secs' % (time.time()-ts)