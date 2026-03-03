"""
💾 Cache - 15-minute TTL for pair rankings
"""
import json
import time
import logging
from typing import List, Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class PairCache:
    def __init__(self, cache_file: str = "pair_hunter_cache.json", ttl_seconds: int = 900):
        self.cache_file = Path(cache_file)
        self.ttl = ttl_seconds
        self._memory_cache = None
        self._cache_time = 0
    
    def get(self) -> Optional[List[Dict]]:
        if self._memory_cache and (time.time() - self._cache_time) < self.ttl:
            return self._memory_cache
        
        if not self.cache_file.exists():
            return None
        
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
            
            cache_age = time.time() - data.get('timestamp', 0)
            if cache_age > self.ttl:
                return None
            
            pairs = data.get('pairs', [])
            self._memory_cache = pairs
            self._cache_time = data.get('timestamp', time.time())
            
            return pairs
            
        except Exception:
            return None
    
    def set(self, pairs: List[Dict]):
        data = {
            'timestamp': time.time(),
            'pairs': pairs,
            'count': len(pairs)
        }
        
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(data, f)
            
            self._memory_cache = pairs
            self._cache_time = data['timestamp']
            
        except Exception as e:
            logger.error(f"Failed to write cache: {e}")
    
    def clear(self):
        self._memory_cache = None
        self._cache_time = 0
        if self.cache_file.exists():
            self.cache_file.unlink()
    
    def is_valid(self) -> bool:
        return self.get() is not None
    
    def get_age_seconds(self) -> float:
        if self._cache_time == 0:
            return float('inf')
        return time.time() - self._cache_time
