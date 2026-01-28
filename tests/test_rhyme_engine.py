import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rhyme_engine import RhymeEngine


class TestRhymeEngine(unittest.TestCase):
    
    def setUp(self):
        self.engine = RhymeEngine()
    
    def test_normalize_latin(self):
        result = self.engine._normalize_word("Beograd")
        self.assertEqual(result, "beograd")
    
    def test_normalize_cyrillic(self):
        result = self.engine._normalize_word("Београд")
        self.assertEqual(result.lower(), "beograd")
    
    def test_normalize_removes_punctuation(self):
        result = self.engine._normalize_word("Test-123!")
        self.assertEqual(result, "test")
    
    def test_collapse_digraphs(self):
        result = self.engine._collapse_digraphs("anja")
        self.assertEqual(result, "aÑa")
        
        result = self.engine._collapse_digraphs("lja")
        self.assertEqual(result, "Ĺa")
        
        result = self.engine._collapse_digraphs("dža")
        self.assertEqual(result, "Ďa")
    
    def test_rhyme_key_basic(self):
        key = self.engine._compute_rhyme_key("beograd", syllables=2)
        self.assertTrue(len(key) > 0)
        self.assertTrue('a' in key)
    
    def test_rhyme_key_one_syllable(self):
        key1 = self.engine._compute_rhyme_key("grad", syllables=1)
        key2 = self.engine._compute_rhyme_key("rad", syllables=1)
        self.assertEqual(key1, key2)
    
    def test_rhyme_key_no_vowels(self):
        key = self.engine._compute_rhyme_key("xyz", syllables=2)
        self.assertEqual(key, "xyz")
    
    def test_find_rhymes_empty_query(self):
        rhymes = self.engine.find_rhymes("", syllables=2, max_results=10)
        self.assertEqual(rhymes, [])
    
    def test_transliterate_to_cyrillic(self):
        result = self.engine.transliterate_to_cyrillic("beograd")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


class TestRhymeEngineWithDictionary(unittest.TestCase):
    
    def setUp(self):
        self.engine = RhymeEngine()
        test_words = ["grad", "rad", "mlad", "jad", "kuća", "žalba", "ljubav"]
        self.engine.words = set(test_words)
        self.engine._loaded = True
    
    def test_find_rhymes_returns_similar_endings(self):
        rhymes = self.engine.find_rhymes("grad", syllables=1, max_results=50)
        self.assertIn("rad", rhymes)
        self.assertIn("mlad", rhymes)
        self.assertIn("jad", rhymes)
        self.assertNotIn("grad", rhymes)
    
    def test_find_rhymes_excludes_exact_match(self):
        rhymes = self.engine.find_rhymes("grad", syllables=1, max_results=50)
        self.assertNotIn("grad", rhymes)
    
    def test_find_rhymes_respects_max_results(self):
        rhymes = self.engine.find_rhymes("grad", syllables=1, max_results=2)
        self.assertLessEqual(len(rhymes), 2)
    
    def test_find_rhymes_deterministic_ordering(self):
        rhymes1 = self.engine.find_rhymes("grad", syllables=1, max_results=50)
        rhymes2 = self.engine.find_rhymes("grad", syllables=1, max_results=50)
        self.assertEqual(rhymes1, rhymes2)


if __name__ == '__main__':
    unittest.main()
