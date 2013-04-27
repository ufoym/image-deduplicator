import cv2, numpy as np, os, time, cPickle as pickle

class BKTree(object):
    def __init__(self):
        self.root = None
        pass        
    def insert(self, obj):
        if self.root is None:
            self.root = BKNode(obj)
        else:
            self.root.insert(obj)
    def find(self, obj, threshold):
        if self.root is not None:
            for res in self.root.find(obj, threshold):
                yield res
    
class BKNode(object):
    obj = None
    children = dict()    
    def __init__(self, obj):
        self.obj = obj
        self.children = dict()        
    def insert(self, obj):
        if obj == self.obj:
            return False
        else:
            d = obj.distance(self.obj)
            if self.children.has_key(d):
                self.children[d].insert(obj)
            else:
                self.children[d] = BKNode(obj)
            return True            
    def find(self, obj, threshold):
        d = obj.distance(self.obj)
        if d <= threshold:
            yield self.obj            
        dmin = d - threshold
        dmax = d + threshold
        for i in range(dmin, dmax+1):
            if self.children.has_key(i):
                for child in self.children[i].find(obj, threshold):
                    yield child    
                    
class ImageObject(object):
    def __init__(self, path):
        self.path = path
        self.hash = self.hash(path)
    def distance(self, obj):
        '''Hamming distance'''
        x = self.hash^obj.hash
        m1  = 0x5555555555555555
        m2  = 0x3333333333333333
        h01 = 0x0101010101010101
        m4  = 0x0f0f0f0f0f0f0f0f
        x -= (x >> 1) & m1
        x = (x & m2) + ((x >> 2) & m2)
        x = (x + (x >> 4)) & m4
        return (x*h01)>>56 & 0xff
    def get(self):
        return this.path
    def hash(self, path):
        gray = cv2.imread(path, 0)
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

class ImageDatabase(object):
    def __init__(self, max_distance):
        self.max_distance = max_distance
    def build(self, img_folder):
        self.bktree = BKTree()
        for dirPath, dirNames, fileNames in os.walk(img_folder):
            for f in fileNames:
                path = os.path.join(dirPath, f)
                self.bktree.insert(ImageObject(path))
    def load(self, db_path):
        self.bktree = pickle.load(open(db_path, 'r'))
    def save(self, db_path):
        pickle.dump(self.bktree, open(db_path, 'w'))
    def insert(self, path):
        self.bktree.insert(ImageObject(path))
    def find_duplicate(self, path):
        return self.bktree.find(ImageObject(path), self.max_distance)


def test_find_duplicate(img_folder, db_path):
    imageDB = ImageDatabase(10)
    if os.path.exists(db_path):
        imageDB.load(db_path)
    else:
        imageDB.build(img_folder)
        imageDB.save(db_path)
    for dirPath, dirNames, fileNames in os.walk(img_folder):
        for f in fileNames:
            img_path = os.path.join(dirPath, f)
            for img in imageDB.find_duplicate(img_path):
                print img.path
            print '-------------------------------------'

ts = time.time()
test_find_duplicate('var', 'img.hash')
print '%2.2f secs' % (time.time()-ts)