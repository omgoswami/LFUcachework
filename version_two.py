'''
new version: done with Python's Counter 
for each key in the dictionary, store [frequency, recency of access, value]
decrement the recency of access each time the value is accessed because Counter's most_common method returns the Largest value
'''

class LFUCache:
    def __init__(self, capacity):
        self.cache = collections.Counter()
        self.capacity = capacity
        self.recency = 0

    def get(self, key):
        if key not in self.cache:
            return -1
        self.recency -= 1
        self.cache[key] = [self.cache[key][0] - 1, self.recency, self.cache[key][2]]

        return self.cache[key][2]


    def set(self, key, val):
        if self.capacity:
            self.recency -= 1

            if key in self.cache:
                self.cache[key] = [self.cache[key][0] - 1, self.recency, val]
                return
            
            if len(self.cache) == self.capacity:
                k, _= self.cache.most_common(1)[0]
                print(k)
                del self.cache[k]
            
            self.cache[key] = [0, self.recency, val]
