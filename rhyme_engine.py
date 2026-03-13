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
    
    def count_syllables(self, word: str) -> int:
        """
        Count syllables in a Serbian word.
        Vowels: a, e, i, o, u
        Syllabic R: 'r' acts as a vowel when between two consonants, 
        or at the beginning of a word before a consonant.
        """
        word = self._normalize_word(word)
        if not word:
            return 0
            
        collapsed = self._collapse_digraphs(word)
        vowels = 'aeiou'
        
        # Simple vowel count
        syllable_count = sum(1 for char in collapsed if char in vowels)
        
        # Handle syllabic R
        for i, char in enumerate(collapsed):
            if char == 'r':
                # Check if 'r' is syllabic
                is_syllabic = False
                
                # Case 1: Between two consonants
                if i > 0 and i < len(collapsed) - 1:
                    prev_char = collapsed[i-1]
                    next_char = collapsed[i+1]
                    if prev_char not in vowels and next_char not in vowels:
                        is_syllabic = True
                        
                # Case 2: At start of word before a consonant
                elif i == 0 and len(collapsed) > 1:
                    next_char = collapsed[1]
                    if next_char not in vowels:
                        is_syllabic = True
                
                # Case 3: At end of word after a consonant (rare but possible in some dialects/slang)
                elif i == len(collapsed) - 1 and i > 0:
                    prev_char = collapsed[i-1]
                    if prev_char not in vowels:
                        is_syllabic = True
                        
                if is_syllabic:
                    syllable_count += 1
                    
        # Every word has at least 1 syllable unless empty
        return max(1, syllable_count) if word else 0

    def get_vowel_positions(self, collapsed_word: str) -> List[int]:
        """Get positions of all vowels including syllabic R."""
        vowels = 'aeiou'
        positions = []
        
        for i, char in enumerate(collapsed_word):
            if char in vowels:
                positions.append(i)
            elif char == 'r':
                # Check if syllabic R
                is_syllabic = False
                if i > 0 and i < len(collapsed_word) - 1:
                    if collapsed_word[i-1] not in vowels and collapsed_word[i+1] not in vowels:
                        is_syllabic = True
                elif i == 0 and len(collapsed_word) > 1:
                    if collapsed_word[1] not in vowels:
                        is_syllabic = True
                elif i == len(collapsed_word) - 1 and i > 0:
                    if collapsed_word[i-1] not in vowels:
                        is_syllabic = True
                
                if is_syllabic:
                    positions.append(i)
                    
        return positions

    def _compute_rhyme_key(self, word: str, syllables: int = 2) -> str:
        collapsed = self._collapse_digraphs(word)
        vowel_positions = self.get_vowel_positions(collapsed)
        
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
        
        # Exclude exact match and words with different syllable counts if it's a short word
        query_syllables = self.count_syllables(normalized_query)
        
        filtered_candidates = []
        for w in candidates:
            if w == normalized_query:
                continue
            
            # Keep words with similar syllable counts for better rhythm
            w_syllables = self.count_syllables(w)
            if abs(w_syllables - query_syllables) <= 1 or query_syllables > 3:
                filtered_candidates.append(w)
        
        filtered_candidates.sort(key=lambda w: (abs(len(w) - len(normalized_query)), w))
        
        return filtered_candidates[:max_results]

    def find_consonant_matches(self, query: str, match_type: str = 'initial', max_results: int = 50) -> List[str]:
        """
        Find words with similar consonant patterns for Drill/Rap flow.
        match_type: 'initial' (starts with same consonants), 'hard' (contains hard drill consonants)
        """
        normalized_query = self._normalize_word(query)
        if not normalized_query:
            return []
            
        collapsed = self._collapse_digraphs(normalized_query)
        vowels = 'aeiou'
        
        candidates = []
        
        if match_type == 'initial':
            # Extract initial consonant cluster
            initial_consonants = ''
            for char in collapsed:
                if char not in vowels:
                    initial_consonants += char
                else:
                    break
            
            if not initial_consonants:
                return []
                
            # Find words starting with the same consonant cluster
            for word in self.words:
                if word == normalized_query:
                    continue
                    
                w_collapsed = self._collapse_digraphs(word)
                if w_collapsed.startswith(initial_consonants):
                    candidates.append(word)
                    
        elif match_type == 'hard':
            # Drill focus: k, g, t, d, p, b
            hard_consonants = set('kgtdpbcčćđď')
            query_hard_chars = [c for c in collapsed if c in hard_consonants]
            
            if not query_hard_chars:
                return []
                
            # Score words based on containing similar hard consonants
            scored_candidates = []
            for word in self.words:
                if word == normalized_query:
                    continue
                    
                w_collapsed = self._collapse_digraphs(word)
                w_hard_chars = [c for c in w_collapsed if c in hard_consonants]
                
                # Check for intersection of hard consonants
                common_hard = set(query_hard_chars).intersection(set(w_hard_chars))
                if common_hard:
                    # Score based on number of matching hard consonants and syllable similarity
                    score = len(common_hard) * 2
                    
                    # Bonus for exact sequence match
                    query_seq = ''.join(query_hard_chars)
                    w_seq = ''.join(w_hard_chars)
                    if query_seq in w_seq or w_seq in query_seq:
                        score += 3
                        
                    # Penalty for vastly different lengths
                    len_diff = abs(len(w_collapsed) - len(collapsed))
                    score -= len_diff * 0.5
                    
                    if score > 0:
                        scored_candidates.append((word, score))
            
            # Sort by score descending
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            candidates = [w for w, score in scored_candidates]
            
        return candidates[:max_results]
    
    def find_rhyme_scheme_words(self, words_to_match: List[str], scheme: str, syllables_match: bool = True) -> Dict[str, List[str]]:
        """
        Given a list of words and a scheme (like AABB), find matching rhymes.
        e.g., words_to_match=["sunce", "ljubav"], scheme="AABB" 
        """
        # Get unique patterns from the scheme (e.g. ['A', 'B'])
        unique_patterns = []
        for char in scheme:
            if char not in unique_patterns:
                unique_patterns.append(char)
                
        # Map each unique pattern to a seed word
        pattern_seeds = {}
        for i, word in enumerate(words_to_match):
            if i < len(unique_patterns):
                pattern_seeds[unique_patterns[i]] = word
                
        results = {}
        
        for i, char in enumerate(scheme):
            line_key = f"Line {i+1} ({char})"
            
            if char in pattern_seeds:
                seed = pattern_seeds[char]
                # If this is the exact line where the seed was provided
                if list(scheme).index(char) == i:
                    results[line_key] = [seed]
                else:
                    # Find rhymes for the seed
                    target_syllables = self.count_syllables(seed)
                    rhymes = self.find_rhymes(seed, syllables=2, max_results=100)
                    
                    if syllables_match:
                        # Strict syllable matching
                        strict_rhymes = [r for r in rhymes if self.count_syllables(r) == target_syllables]
                        results[line_key] = strict_rhymes[:10] if strict_rhymes else rhymes[:10]
                    else:
                        results[line_key] = rhymes[:10]
            else:
                results[line_key] = ["<needs seed word for pattern " + char + ">"]
                
        return results

    def is_perfect_rhyme(self, word1: str, word2: str, syllables: int = 2) -> bool:
        """Check if two words are a perfect rhyme (exact match from nth vowel to end)."""
        w1_norm = self._normalize_word(word1)
        w2_norm = self._normalize_word(word2)
        
        if not w1_norm or not w2_norm or w1_norm == w2_norm:
            return False
            
        key1 = self._compute_rhyme_key(w1_norm, syllables)
        key2 = self._compute_rhyme_key(w2_norm, syllables)
        
        return key1 == key2

    def is_slant_rhyme(self, word1: str, word2: str) -> bool:
        """Check if words are a slant rhyme (matching vowels, different consonants)."""
        w1_norm = self._normalize_word(word1)
        w2_norm = self._normalize_word(word2)
        
        if not w1_norm or not w2_norm or w1_norm == w2_norm:
            return False
            
        w1_collapsed = self._collapse_digraphs(w1_norm)
        w2_collapsed = self._collapse_digraphs(w2_norm)
        
        # Extract just the vowels of the last 2 syllables
        vowels = 'aeiou'
        w1_vowels = [c for c in w1_collapsed if c in vowels]
        w2_vowels = [c for c in w2_collapsed if c in vowels]
        
        # Compare last 2 vowels
        if len(w1_vowels) >= 2 and len(w2_vowels) >= 2:
            return w1_vowels[-2:] == w2_vowels[-2:]
        elif len(w1_vowels) >= 1 and len(w2_vowels) >= 1:
            return w1_vowels[-1] == w2_vowels[-1]
            
        return False
