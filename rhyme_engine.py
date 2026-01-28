import re
from pathlib import Path
from typing import List, Dict, Set, Optional
import srbai


class RhymeEngine:
    def __init__(self, dict_path: Optional[Path] = None):
        self.dict_path = dict_path or Path(__file__).parent / "data" / "dict" / "hunspell-sr" / "sr-Latn.dic"
        self.words: Set[str] = set()
        self.rhyme_index: Dict[str, List[str]] = {}
        self._loaded = False
        
    def load_dictionary(self):
        if self._loaded:
            return
            
        if not self.dict_path.exists():
            raise FileNotFoundError(
                f"Dictionary not found at {self.dict_path}.\n"
                f"Please run: scripts/fetch_dict.ps1"
            )
        
        with open(self.dict_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                word = line.split('/')[0].strip()
                if word:
                    normalized = self._normalize_word(word)
                    if normalized:
                        self.words.add(normalized)
        
        self._loaded = True
    
    def _normalize_word(self, word: str) -> str:
        word = word.lower().strip()
        
        try:
            if any(ord(c) > 127 and ord(c) < 0x530 for c in word):
                word = srbai.transliterate(word, to_latin=True)
        except Exception:
            pass
        
        word = re.sub(r'[^a-zčćđšž]', '', word)
        
        return word
    
    def _collapse_digraphs(self, word: str) -> str:
        word = word.replace('nj', 'Ñ')
        word = word.replace('lj', 'Ĺ')
        word = word.replace('dž', 'Ď')
        return word
    
    def _compute_rhyme_key(self, word: str, syllables: int = 2) -> str:
        collapsed = self._collapse_digraphs(word)
        
        vowels = 'aeiou'
        vowel_positions = [i for i, c in enumerate(collapsed) if c.lower() in vowels]
        
        if len(vowel_positions) == 0:
            return collapsed
        
        target_vowel_count = min(syllables, len(vowel_positions))
        start_pos = vowel_positions[-target_vowel_count]
        
        return collapsed[start_pos:]
    
    def build_index(self, syllables: int = 2):
        self.rhyme_index = {}
        
        for word in self.words:
            key = self._compute_rhyme_key(word, syllables)
            if key not in self.rhyme_index:
                self.rhyme_index[key] = []
            self.rhyme_index[key].append(word)
    
    def find_rhymes(self, query: str, syllables: int = 2, max_results: int = 50) -> List[str]:
        normalized_query = self._normalize_word(query)
        
        if not normalized_query:
            return []
        
        self.build_index(syllables)
        
        query_key = self._compute_rhyme_key(normalized_query, syllables)
        
        candidates = self.rhyme_index.get(query_key, [])
        
        candidates = [w for w in candidates if w != normalized_query]
        
        candidates.sort(key=lambda w: (abs(len(w) - len(normalized_query)), w))
        
        return candidates[:max_results]
    
    def transliterate_to_cyrillic(self, word: str) -> str:
        try:
            return srbai.transliterate(word, to_latin=False)
        except:
            return word
