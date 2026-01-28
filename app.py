import streamlit as st
from pathlib import Path
from rhyme_engine import RhymeEngine
import os


@st.cache_resource
def load_engine():
    dict_path_env = os.environ.get('RIMER_DICT_PATH')
    if dict_path_env:
        dict_path = Path(dict_path_env)
    else:
        dict_path = Path(__file__).parent / "data" / "dict" / "hunspell-sr" / "sr-Latn.dic"
    
    engine = RhymeEngine(dict_path)
    try:
        engine.load_dictionary()
        return engine, None
    except FileNotFoundError as e:
        return None, str(e)


st.set_page_config(page_title="RimerSR", page_icon="🎵", layout="wide")

st.title("🎵 RimerSR (offline)")
st.markdown("Serbian rhyme suggester - Works with Latin and Cyrillic input")

engine, error = load_engine()

if error:
    st.error(error)
    st.stop()

tab1, tab2 = st.tabs(["Single word", "Paste lyrics"])

with tab1:
    st.subheader("Find rhymes for a single word")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        word_input = st.text_input("Enter a word (Latin or Cyrillic):", key="single_word")
    
    with col2:
        st.write("")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        syllables = st.slider("Rhyme tightness (syllables from end):", 1, 3, 2, key="single_syllables")
    
    with col2:
        max_results = st.slider("Max results:", 10, 200, 50, key="single_max")
    
    with col3:
        show_cyrillic = st.checkbox("Show Cyrillic output too", key="single_cyrillic")
    
    if word_input:
        with st.spinner("Finding rhymes..."):
            rhymes = engine.find_rhymes(word_input, syllables=syllables, max_results=max_results)
        
        if rhymes:
            st.success(f"Found {len(rhymes)} rhymes:")
            
            if show_cyrillic:
                col_latin, col_cyrillic = st.columns(2)
                with col_latin:
                    st.markdown("**Latin:**")
                    for rhyme in rhymes:
                        st.text(rhyme)
                with col_cyrillic:
                    st.markdown("**Cyrillic:**")
                    for rhyme in rhymes:
                        st.text(engine.transliterate_to_cyrillic(rhyme))
            else:
                for rhyme in rhymes:
                    st.text(rhyme)
        else:
            st.warning("No rhymes found.")

with tab2:
    st.subheader("Find rhymes for lyrics")
    
    lyrics_input = st.text_area("Paste your lyrics here:", height=200, key="lyrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        lyrics_syllables = st.slider("Rhyme tightness (syllables from end):", 1, 3, 2, key="lyrics_syllables")
    
    with col2:
        lyrics_max = st.slider("Max results per word:", 10, 200, 30, key="lyrics_max")
    
    with col3:
        lyrics_cyrillic = st.checkbox("Show Cyrillic output too", key="lyrics_cyrillic")
    
    if st.button("Find rhymes for all lines"):
        if lyrics_input:
            lines = lyrics_input.strip().split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            if lines:
                with st.spinner("Processing lyrics..."):
                    for line in lines:
                        words = line.split()
                        if not words:
                            continue
                        
                        last_word = words[-1]
                        st.markdown(f"**Line:** `{line}`")
                        st.markdown(f"**Last word:** `{last_word}`")
                        
                        rhymes = engine.find_rhymes(last_word, syllables=lyrics_syllables, max_results=lyrics_max)
                        
                        if rhymes:
                            if lyrics_cyrillic:
                                col_latin, col_cyrillic = st.columns(2)
                                with col_latin:
                                    st.markdown("*Latin:*")
                                    st.text(", ".join(rhymes[:10]))
                                with col_cyrillic:
                                    st.markdown("*Cyrillic:*")
                                    cyrillic_rhymes = [engine.transliterate_to_cyrillic(r) for r in rhymes[:10]]
                                    st.text(", ".join(cyrillic_rhymes))
                            else:
                                st.text(", ".join(rhymes[:10]))
                        else:
                            st.text("No rhymes found.")
                        
                        st.markdown("---")
            else:
                st.warning("No valid lines found.")
        else:
            st.warning("Please paste some lyrics first.")

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "RimerSR is an offline Serbian rhyme suggester.\n\n"
    "Supports both Latin and Cyrillic input.\n\n"
    "Dictionary: Serbian Hunspell\n\n"
    "Transliteration: SrbAI"
)
