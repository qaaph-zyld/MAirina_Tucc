from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
from pathlib import Path
from rhyme_engine import RhymeEngine

app = FastAPI(title="MAirina Tucc API", description="AI Songwriting Suite for Serbian Language")

# Initialize engine globally
engine = None

def get_engine():
    global engine
    if engine is None:
        dict_path_env = os.environ.get('RIMER_DICT_PATH')
        if dict_path_env:
            dict_path = Path(dict_path_env)
        else:
            dict_path = Path(__file__).parent / "data" / "dict" / "hunspell-sr" / "sr-Latn.dic"
            
        engine = RhymeEngine(dict_path)
        try:
            engine.load_dictionary()
        except FileNotFoundError as e:
            raise RuntimeError(f"Failed to load dictionary: {e}")
    return engine

@app.on_event("startup")
async def startup_event():
    get_engine() # Pre-load dictionary on startup

# Pydantic models for request/response
class RhymeRequest(BaseModel):
    word: str
    syllables: int = 2
    max_results: int = 50

class RhymeSchemeRequest(BaseModel):
    words: List[str]
    scheme: str
    syllables_match: bool = True

class ConsonantPlayRequest(BaseModel):
    word: str
    match_type: str = 'hard' # 'initial' or 'hard'
    max_results: int = 50

class WordAnalysisResponse(BaseModel):
    word: str
    syllables_count: int
    vowel_positions: List[int]
    transliterated_cyrillic: str

# Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to MAirina Tucc API"}

@app.get("/api/analyze/{word}", response_model=WordAnalysisResponse)
async def analyze_word(word: str):
    eng = get_engine()
    collapsed = eng._collapse_digraphs(eng._normalize_word(word))
    
    return WordAnalysisResponse(
        word=word,
        syllables_count=eng.count_syllables(word),
        vowel_positions=eng.get_vowel_positions(collapsed),
        transliterated_cyrillic=eng.transliterate_to_cyrillic(word)
    )

@app.post("/api/rhymes")
async def get_rhymes(req: RhymeRequest):
    eng = get_engine()
    rhymes = eng.find_rhymes(req.word, syllables=req.syllables, max_results=req.max_results)
    return {"rhymes": rhymes}

@app.post("/api/rhyme-scheme")
async def get_rhyme_scheme(req: RhymeSchemeRequest):
    eng = get_engine()
    results = eng.find_rhyme_scheme_words(
        req.words, 
        scheme=req.scheme, 
        syllables_match=req.syllables_match
    )
    return {"scheme_results": results}

@app.post("/api/consonant-play")
async def get_consonant_matches(req: ConsonantPlayRequest):
    eng = get_engine()
    if req.match_type not in ['initial', 'hard']:
        raise HTTPException(status_code=400, detail="match_type must be 'initial' or 'hard'")
        
    matches = eng.find_consonant_matches(req.word, match_type=req.match_type, max_results=req.max_results)
    return {"matches": matches}
