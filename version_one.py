'''
doubly linked list v1: each node represents the number of times a value has been accessed

doubly linked list v2: each node represents an individual value, and the list is sorted by recency of access (the least recently accessed node is at the top/front)
    why at the front? so we can access (and evict) it in O(1) time 
'''
class CacheNode:
    '''
    doubly linked list of individual values
    '''
    def __init__(self, key, value, freq_node, l_node, r_node):
        self.key = key
        self.value = value
        self.freq_node = freq_node
        self.l_node = l_node # the CacheNode that comes before this one 
        self.r_node = r_node # the CacheNode that comes after this one
    
    def free_myself(self):
        if self.freq_node.cache_head == self.freq_node.cache_tail:
            self.freq_node.cache_head = self.freq_node.cache_tail = None
        elif self.freq_node.cache_head == self:
            self.r_node.l_node = None
            self.freq_node.cache_head = self.r_node
        elif self.freq_node.cache_tail == self:
            self.l_node.r_node = None
            self.freq_node.cache_tail = self.l_node
        else:
            self.l_node.r_node = self.r_node
            self.r_node.l_node = self.l_node

        self.l_node = None
        self.r_node = None
        self.freq_node = None

class FreqNode:
    '''
    doubly linked list of frequencies 
    '''
    def __init__(self, freq, l_node, r_node):
        self.freq = freq
        self.l_node = l_node # previous FreqNode
        self.r_node = r_node # next FreqNode
        self.cache_head = None # CacheNode head under this FreqNode
        self.cache_tail = None # CacheNode tail under this FreqNode
    
    def count_caches(self):
        if self.cache_head is None and self.cache_tail is None:
            return 0
        elif self.cache_head == self.cache_tail:
            return 1
        else:
            return '2+'
    
    def remove(self):
        if self.l_node is not None:
            self.l_node.r_node = self.r_node
        if self.r_node is not None:
            self.r_node.l_node = self.l_node
        
        l_node = self.l_node
        r_node = self.r_node

        self.l_node = self.r_node = self.cache_head = self.cache_tail = None
        return (l_node, r_node)
    
    def pop_top_cache(self):
        if self.cache_head is None and self.cache_tail is None:
            return None
        elif self.cache_head == self.cache_tail:
            cache_head = self.cache_head
            self.cache_head = self.cache_tail = None
            return cache_head
        else:
            cache_head = self.cache_head
            self.cache_head.r_node.l_node = None
            self.cache_head = self.cache_head.r_node
            return cache_head
    
    def add_cache_to_tail(self, cache_node):
        cache_node.freq_node = self
        if self.cache_head is None and self.cache_tail is None:
            self.cache_head = self.cache_tail = cache_node
        else:
            cache_node.l_node = self.cache_tail
            cache_node.r_node = None
            self.cache_tail.r_node = cache_node
            self.cache_tail = cache_node
    
    def insert_after_me(self, freq_node):
        freq_node.l_node = self
        freq_node.r_node = self.r_node

        if self.r_node is not None:
            self.r_node.l_node = freq_node
        
        self.r_node = freq_node

    def insert_before_me(self, freq_node):
        if self.l_node is not None:
            self.l_node.r_node = freq_node
        
        freq_node.l_node = self.l_node
        freq_node.r_node = self
        self.l_node = freq_node

class LFUCache:
    def __init__(self, capacity):
        self.cache = {}
        self.capacity = capacity
        self.freq_link_head = None

    def get(self, key):
        if key in self.cache:
            cache_node = self.cache[key]
            freq_node = cache_node.freq_node
            value = cache_node.value

            self.move_forward(cache_node, freq_node)

            return value
        else:
            return -1        

    def set(self, key, val):
        if self.capacity <= 0:
            return -1
        if key not in self.cache:
            if len(self.cache) >= self.capacity:
                self.dump_cache()
        
            self.create_cache(key, val)
        else:
            cache_node = self.cache[key]
            freq_node = cache_node.freq_node
            cache_node.value = val

            self.move_forward(cache_node, freq_node)
    
    def move_forward(self, cache_node, freq_node):
        if freq_node.r_node is None or freq_node.r_node.freq != freq_node.freq + 1:
            target_freq_node = FreqNode(freq_node.freq + 1, None, None)
            target_empty = True
        else:
            target_freq_node = freq_node.r_node
            target_empty = False
        
        cache_node.free_myself()

        target_freq_node.add_cache_to_tail(cache_node)

        if target_empty:
            freq_node.insert_after_me(target_freq_node)


        if freq_node.count_caches() == 0:
            if self.freq_link_head == freq_node:
                self.freq_link_head = target_freq_node

            freq_node.remove()
    
    def dump_cache(self):
        head_freq_node = self.freq_link_head
        self.cache.pop(head_freq_node.cache_head.key)
        head_freq_node.pop_top_cache()

        if head_freq_node.count_caches() == 0:
            self.freq_link_head = head_freq_node.r_node
            head_freq_node.remove()
    
    def create_cache(self, key, value):
        cache_node = CacheNode(key, value, None, None, None)
        self.cache[key] = cache_node
        
        if self.freq_link_head is None or self.freq_link_head.freq != 0:
            new_freq_node = FreqNode(0, None, None)
            new_freq_node.add_cache_to_tail(cache_node)

            if self.freq_link_head is not None:
                self.freq_link_head.insert_before_me(new_freq_node)
            
            self.freq_link_head = new_freq_node
        else:
            self.freq_link_head.add_cache_to_tail(cache_node)
