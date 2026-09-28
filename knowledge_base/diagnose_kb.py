
import json
import os

def diagnose_knowledge_base(kb_path):
    """Diagnose what's actually in your knowledge base"""

    print("🔍 KNOWLEDGE BASE DIAGNOSTIC TOOL")
    print("=" * 50)

    try:
        with open(kb_path, 'r', encoding='utf-8') as f:
            kb = json.load(f)

        print(f"✅ Successfully loaded knowledge base")
        print()

        # Check basic structure
        print("📊 BASIC STATISTICS:")
        print(f"   Total chunks: {len(kb.get('chunks', []))}")
        print(f"   Search index terms: {len(kb.get('search_index', {}))}")
        print(f"   Entity relationships: {len(kb.get('relationships', {}))}")
        print()

        # Check entities
        print("🏷️  ENTITIES FOUND:")
        entities = kb.get('entities', {})
        for entity_type, entity_list in entities.items():
            print(f"   {entity_type}: {len(entity_list)} items")
            if entity_list:
                print(f"      Examples: {entity_list[:3]}")
        print()

        # Check first few chunks content
        print("📄 SAMPLE CHUNK CONTENT:")
        chunks = kb.get('chunks', [])
        if chunks:
            for i, chunk in enumerate(chunks[:3]):
                print(f"\n   Chunk {i+1} (ID: {chunk['id']}):")
                text = chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
                print(f"   Text: {text}")
                print(f"   Words: {chunk.get('word_count', 0)}")

        print()

        # Check search index sample
        print("🔍 SEARCH INDEX SAMPLE:")
        search_index = kb.get('search_index', {})
        if search_index:
            sample_terms = list(search_index.keys())[:10]
            for term in sample_terms:
                chunk_count = len(search_index[term])
                print(f"   '{term}': appears in {chunk_count} chunks")
        else:
            print("   ❌ No search index found!")

        print()

        # Check for common words that should exist
        print("🎯 CHECKING FOR COMMON WORDS:")
        common_words = ['the', 'and', 'of', 'in', 'to', 'a', 'is', 'that', 'it', 'with']
        for word in common_words:
            if word in search_index:
                count = len(search_index[word])
                print(f"   '{word}': ✅ found in {count} chunks")
            else:
                print(f"   '{word}': ❌ not found")

        print()

        # Show total text content
        total_chars = sum(len(chunk['text']) for chunk in chunks)
        total_words = sum(chunk.get('word_count', 0) for chunk in chunks)

        print("📈 CONTENT SUMMARY:")
        print(f"   Total characters: {total_chars:,}")
        print(f"   Total words: {total_words:,}")
        print(f"   Average chunk size: {total_words/len(chunks):.0f} words" if chunks else "   No chunks")

        # Suggest fixes
        print()
        print("💡 SUGGESTED ACTIONS:")
        if total_words < 100:
            print("   ⚠️  Very little content detected!")
            print("   • Check if your original text file had content")
            print("   • Try running simple_kb_builder.py again")
        elif not search_index:
            print("   ⚠️  Search index is empty!")
            print("   • The indexing process may have failed")
            print("   • Try rebuilding the knowledge base")
        elif len(search_index) < 50:
            print("   ⚠️  Very few search terms indexed!")
            print("   • Your text might be very specialized")
            print("   • Try searching for specific terms from your content")
        else:
            print("   ✅ Knowledge base looks healthy")
            print("   • Try searching for terms that appear in the sample chunks")
            print("   • Use broader search terms")

    except FileNotFoundError:
        print(f"❌ Knowledge base file not found: {kb_path}")
    except Exception as e:
        print(f"❌ Error reading knowledge base: {e}")

def suggest_search_terms(kb_path):
    """Suggest actual search terms based on content"""
    try:
        with open(kb_path, 'r', encoding='utf-8') as f:
            kb = json.load(f)

        print("\n🎯 SUGGESTED SEARCH TERMS FROM YOUR CONTENT:")
        print("-" * 50)

        search_index = kb.get('search_index', {})

        # Get most common terms (excluding very common words)
        exclude_words = {'the', 'and', 'of', 'in', 'to', 'a', 'is', 'that', 'it', 'with', 'for', 'as', 'on', 'be', 'at', 'by', 'this', 'have', 'from', 'or', 'one', 'had', 'but', 'not', 'what', 'all', 'were', 'they', 'we', 'when', 'your', 'can', 'said', 'there', 'each', 'which', 'do', 'how', 'their', 'if', 'will', 'up', 'other', 'about', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like', 'into', 'him', 'has', 'two', 'more', 'very', 'after', 'words', 'first', 'been', 'who', 'oil', 'sit', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part'}

        # Sort terms by frequency
        term_freq = [(term, len(chunks)) for term, chunks in search_index.items() 
                     if term not in exclude_words and not term.startswith('entity_')]
        term_freq.sort(key=lambda x: x[1], reverse=True)

        if term_freq:
            print("Most common terms in your textbook:")
            for term, freq in term_freq[:20]:
                print(f"   • '{term}' (appears in {freq} chunks)")

        # Check for potential Sanskrit/Tamil terms
        potential_terms = [term for term, _ in term_freq if len(term) > 4 and any(c in term.lower() for c in 'āīūēōṃḥṅñṭḍṇṣś')]
        if potential_terms:
            print("\nPotential Sanskrit terms found:")
            for term in potential_terms[:10]:
                print(f"   • '{term}'")

        # Check for academic terms
        academic_terms = [term for term, freq in term_freq if len(term) > 5 and freq >= 2 and term[0].isupper()]
        if academic_terms:
            print("\nPotential academic concepts:")
            for term in academic_terms[:15]:
                print(f"   • '{term}'")

        print("\n" + "=" * 50)
        print("📝 WHAT TO DO NEXT:")
        print("1. Use the terms above in your RAG chatbot searches")
        print("2. Try questions like: 'What does the text say about [term]?'")
        print("3. If no good terms found, check your original text file")

    except Exception as e:
        print(f"Error suggesting terms: {e}")

def check_original_text_file(kb_path):
    """Check the original cleaned text file"""
    try:
        # Look for cleaned text file in same directory
        kb_dir = os.path.dirname(kb_path)
        cleaned_text_path = os.path.join(kb_dir, "cleaned_text.txt")

        if os.path.exists(cleaned_text_path):
            print(f"\n📄 CHECKING ORIGINAL TEXT FILE:")
            print("-" * 40)

            with open(cleaned_text_path, 'r', encoding='utf-8') as f:
                content = f.read()

            print(f"   File size: {len(content):,} characters")
            print(f"   Word count: {len(content.split()):,} words")
            print(f"   Line count: {len(content.split(chr(10))):,} lines")

            # Show first 500 characters
            print(f"\n   First 500 characters:")
            print(f"   {repr(content[:500])}")

            if len(content) < 1000:
                print("\n   ⚠️  WARNING: Very short text file!")
                print("   • This might be why your searches aren't working")
                print("   • Check if your original text extraction worked properly")
        else:
            print(f"\n❌ Original text file not found at: {cleaned_text_path}")

    except Exception as e:
        print(f"Error checking original text: {e}")

def main():
    # Update this path to your knowledge base
    kb_path = "F:/TANCAM/knowledge_base/knowledge_base_20251024_153040/knowledge_base.json"

    if not os.path.exists(kb_path):
        print(f"❌ Knowledge base file not found!")
        print(f"Expected location: {kb_path}")
        print("\nMake sure you've run simple_kb_builder.py first!")
        return

    # Run comprehensive diagnosis
    diagnose_knowledge_base(kb_path)
    suggest_search_terms(kb_path)
    check_original_text_file(kb_path)

if __name__ == "__main__":
    main()
