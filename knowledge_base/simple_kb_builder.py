import os
import json
import re
from datetime import datetime
from typing import List, Dict, Tuple
#python ./knowledge_base_20251024_153040/search_interface.py
# Basic NLP (optional - will work without)
try:
    import spacy
    SPACY_AVAILABLE = True
    print("✅ SpaCy available for enhanced entity extraction")
except ImportError:
    SPACY_AVAILABLE = False
    print("⚠️ SpaCy not available - using pattern-based extraction")


class SimpleKnowledgeBaseBuilder:
    """Convert a single text file into a searchable knowledge base"""
    
    def __init__(self, text_file_path: str, output_dir: str = "./knowledge_base"):
        self.text_file_path = text_file_path
        self.output_dir = output_dir
        self.text_content = ""
        self.chunks = []
        self.entities = []
        self.knowledge_base = {}
        
        # Create output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Initialize NLP if available
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                print("✅ SpaCy English model loaded")
            except OSError:
                print("⚠️ Run: python -m spacy download en_core_web_sm")
        
        print(f"🏗️ Knowledge Base Builder initialized")
        print(f"📄 Input file: {text_file_path}")
        print(f"📁 Output directory: {output_dir}")
    
    def step1_load_and_clean_text(self):
        """Step 1: Load and clean the text file"""
        print("\n1️⃣ LOADING AND CLEANING TEXT FILE")
        print("-" * 40)
        
        try:
            with open(self.text_file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            print(f"✅ Loaded text file: {len(raw_content)} characters")
            
            # Clean the text
            self.text_content = self.clean_text(raw_content)
            
            print(f"✅ Cleaned text: {len(self.text_content)} characters")
            print(f"📊 Word count: {len(self.text_content.split())} words")
            
            # Save cleaned text
            cleaned_file = os.path.join(self.output_dir, "cleaned_text.txt")
            with open(cleaned_file, 'w', encoding='utf-8') as f:
                f.write(self.text_content)
            
            print(f"💾 Saved cleaned text to: {cleaned_file}")
            
        except Exception as e:
            print(f"❌ Error loading text file: {e}")
            return False
        
        return True
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text for better processing"""
        # Remove common OCR artifacts
        text = re.sub(r'\[.*?\]', '', text)  # Remove error brackets
        text = re.sub(r'=+ PAGE \d+ =+', '', text)  # Remove page headers
        text = re.sub(r'Processed with:.*?\n', '', text)  # Remove processing info
        text = re.sub(r'Timestamp:.*?\n', '', text)  # Remove timestamps
        text = re.sub(r'={3,}', '', text)  # Remove separator lines
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize paragraph breaks
        text = re.sub(r'[ \t]+', ' ', text)  # Normalize spaces
        text = text.strip()
        
        return text
    
    def step2_create_chunks(self, chunk_size: int = 500, overlap: int = 50):
        """Step 2: Split text into manageable chunks"""
        print("\n2️⃣ CREATING TEXT CHUNKS")
        print("-" * 40)
        
        if not self.text_content:
            print("❌ No text content available")
            return False
        
        # Split into chunks
        text = self.text_content
        chunks = []
        
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Try to end at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for punct in ['. ', '\n', '! ', '? ']:
                    boundary = text.rfind(punct, start, end)
                    if boundary > start:
                        end = boundary + len(punct)
                        break
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk = {
                    'id': f'chunk_{chunk_id:04d}',
                    'text': chunk_text,
                    'start_pos': start,
                    'end_pos': end,
                    'word_count': len(chunk_text.split()),
                    'char_count': len(chunk_text)
                }
                chunks.append(chunk)
                chunk_id += 1
            
            # Move to next chunk with overlap
            start = max(start + chunk_size - overlap, end)
        
        self.chunks = chunks
        
        print(f"✅ Created {len(chunks)} text chunks")
        if chunks:
            print(f"📊 Average chunk size: {sum(c['word_count'] for c in chunks) / len(chunks):.0f} words")
        
        # Save chunks
        chunks_file = os.path.join(self.output_dir, "text_chunks.json")
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved chunks to: {chunks_file}")
        
        return True
    
    def step3_extract_entities(self):
        """Step 3: Extract important entities from text"""
        print("\n3️⃣ EXTRACTING ENTITIES AND CONCEPTS")
        print("-" * 40)
        
        all_entities = {
            'sanskrit_terms': set(),
            'tamil_terms': set(),
            'persons': set(),
            'places': set(),
            'concepts': set(),
            'dates': set()
        }
        
        for chunk in self.chunks:
            text = chunk['text']
            
            # Extract using SpaCy if available
            if self.nlp:
                doc = self.nlp(text)
                
                for ent in doc.ents:
                    if ent.label_ == 'PERSON':
                        all_entities['persons'].add(ent.text.strip())
                    elif ent.label_ in ['GPE', 'LOC']:
                        all_entities['places'].add(ent.text.strip())
                    elif ent.label_ == 'DATE':
                        all_entities['dates'].add(ent.text.strip())
            
            # Pattern-based extraction for Sanskrit/Tamil
            # Sanskrit terms (with diacritical marks)
            sanskrit_pattern = r'\b[A-Za-z]*[āīūṛḷēōṃḥṅñṭḍṇṣśṣ][A-Za-z]*\b'
            sanskrit_matches = re.findall(sanskrit_pattern, text)
            for match in sanskrit_matches:
                if len(match) > 2:  # Filter short matches
                    all_entities['sanskrit_terms'].add(match)
            
            # Tamil script
            tamil_pattern = r'[\u0B80-\u0BFF]+'
            tamil_matches = re.findall(tamil_pattern, text)
            for match in tamil_matches:
                all_entities['tamil_terms'].add(match)
            
            # Academic concepts (capitalized terms, technical words)
            concept_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
            concept_matches = re.findall(concept_pattern, text)
            for match in concept_matches:
                if len(match.split()) <= 3 and len(match) > 3:  # 1-3 words, not too short
                    all_entities['concepts'].add(match)
        
        # Convert sets to sorted lists and filter
        for key in all_entities:
            entities_list = sorted(list(all_entities[key]))
            # Filter out very common/short terms
            filtered = [e for e in entities_list if len(e.strip()) > 2]
            all_entities[key] = filtered
        
        self.entities = all_entities
        
        print(f"✅ Extracted entities:")
        for entity_type, entities in all_entities.items():
            print(f"   {entity_type}: {len(entities)} items")
            if entities:
                print(f"      Examples: {', '.join(entities[:3])}...")
        
        # Save entities
        entities_file = os.path.join(self.output_dir, "extracted_entities.json")
        with open(entities_file, 'w', encoding='utf-8') as f:
            json.dump(all_entities, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved entities to: {entities_file}")
        
        return True
    
    def step4_build_knowledge_base(self):
        """Step 4: Build searchable knowledge base structure"""
        print("\n4️⃣ BUILDING KNOWLEDGE BASE STRUCTURE")
        print("-" * 40)
        
        # Create knowledge base structure
        self.knowledge_base = {
            'metadata': {
                'source_file': self.text_file_path,
                'created': datetime.now().isoformat(),
                'total_chunks': len(self.chunks),
                'total_entities': sum(len(entities) for entities in self.entities.values())
            },
            'chunks': self.chunks,
            'entities': self.entities,
            'search_index': {},
            'relationships': {}
        }
        
        # Build search index
        search_index = {}
        
        # Index chunks by keywords
        for chunk in self.chunks:
            chunk_id = chunk['id']
            text = chunk['text'].lower()
            
            # Extract keywords (simple approach)
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
            unique_words = set(words)
            
            for word in unique_words:
                if word not in search_index:
                    search_index[word] = []
                search_index[word].append(chunk_id)
        
        # Index entities
        for entity_type, entities in self.entities.items():
            for entity in entities:
                entity_key = f"entity_{entity.lower().replace(' ', '_')}"
                search_index[entity_key] = []
                
                # Find chunks containing this entity
                for chunk in self.chunks:
                    if entity.lower() in chunk['text'].lower():
                        search_index[entity_key].append(chunk['id'])
        
        self.knowledge_base['search_index'] = search_index
        
        # Build simple relationships (entities appearing in same chunks)
        relationships = {}
        for entity_type, entities in self.entities.items():
            for entity in entities:
                relationships[entity] = {
                    'type': entity_type,
                    'co_occurring_entities': [],
                    'chunks': []
                }
                
                # Find chunks containing this entity
                entity_chunks = []
                for chunk in self.chunks:
                    if entity.lower() in chunk['text'].lower():
                        entity_chunks.append(chunk['id'])
                
                relationships[entity]['chunks'] = entity_chunks
                
                # Find co-occurring entities
                co_occurring = set()
                for chunk_id in entity_chunks:
                    chunk_text = next(c['text'] for c in self.chunks if c['id'] == chunk_id).lower()
                    
                    # Check for other entities in same chunk
                    for other_type, other_entities in self.entities.items():
                        for other_entity in other_entities:
                            if other_entity != entity and other_entity.lower() in chunk_text:
                                co_occurring.add(other_entity)
                
                relationships[entity]['co_occurring_entities'] = list(co_occurring)
        
        self.knowledge_base['relationships'] = relationships
        
        print(f"✅ Built knowledge base structure:")
        print(f"   📚 Search index: {len(search_index)} terms")
        print(f"   🔗 Relationships: {len(relationships)} entities")
        
        # Save knowledge base
        kb_file = os.path.join(self.output_dir, "knowledge_base.json")
        with open(kb_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved knowledge base to: {kb_file}")
        
        return True
    
    def step5_create_search_interface(self):
        """Step 5: Create simple search functionality"""
        print("\n5️⃣ CREATING SEARCH INTERFACE")
        print("-" * 40)
        
        # Create the search interface file
        search_code = '''import json
import re
import os
from typing import List, Dict

class KnowledgeBaseSearcher:
    def __init__(self, kb_file_path: str = None):
        if kb_file_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            kb_file_path = os.path.join(script_dir, "knowledge_base.json")
        
        try:
            with open(kb_file_path, 'r', encoding='utf-8') as f:
                self.kb = json.load(f)
            print(f"✅ Loaded knowledge base from: {kb_file_path}")
        except FileNotFoundError:
            print(f"❌ Knowledge base file not found: {kb_file_path}")
            return
        
        self.chunks = {chunk['id']: chunk for chunk in self.kb['chunks']}
        self.search_index = self.kb['search_index']
        self.relationships = self.kb['relationships']
        print(f"✅ Knowledge base ready with {len(self.chunks)} chunks")
    
    def search_text(self, query: str, limit: int = 5) -> List[Dict]:
        if not hasattr(self, 'kb'):
            return []
        
        query_words = re.findall(r'\\\\b[a-zA-Z]{3,}\\\\b', query.lower())
        if not query_words:
            return []
        
        chunk_scores = {}
        for word in query_words:
            if word in self.search_index:
                for chunk_id in self.search_index[word]:
                    chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0) + 1
        
        sorted_chunks = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for chunk_id, score in sorted_chunks[:limit]:
            if chunk_id in self.chunks:
                chunk = self.chunks[chunk_id]
                results.append({
                    'chunk_id': chunk_id,
                    'text': chunk['text'][:300] + "..." if len(chunk['text']) > 300 else chunk['text'],
                    'score': score
                })
        
        return results
    
    def search_entity(self, entity_name: str):
        if not hasattr(self, 'kb'):
            return None
        
        if entity_name in self.relationships:
            return self.relationships[entity_name]
        
        for entity in self.relationships:
            if entity.lower() == entity_name.lower():
                return self.relationships[entity]
        return None
    
    def get_all_entities_by_type(self, entity_type: str) -> List[str]:
        if not hasattr(self, 'kb'):
            return []
        return self.kb['entities'].get(entity_type, [])
    
    def interactive_search(self):
        if not hasattr(self, 'kb'):
            return
        
        print("🔍 INTERACTIVE KNOWLEDGE BASE SEARCH")
        print("=" * 50)
        print("Commands:")
        print("  search <text>     - Search for text")
        print("  entity <name>     - Get entity information")
        print("  entities <type>   - List entities by type")
        print("  stats             - Show statistics")
        print("  quit              - Exit")
        print("\\\\nEntity types: sanskrit_terms, tamil_terms, persons, places, concepts, dates")
        print("=" * 50)
        
        while True:
            try:
                query = input("\\\\n> ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                
                if query.startswith('search '):
                    search_term = query[7:].strip()
                    results = self.search_text(search_term, limit=3)
                    
                    if results:
                        print(f"\\\\n📄 Found {len(results)} results for '{search_term}':")
                        for i, result in enumerate(results, 1):
                            print(f"\\\\n{i}. [Score: {result['score']}] {result['chunk_id']}")
                            print(f"   {result['text']}")
                    else:
                        print(f"❌ No results found for '{search_term}'")
                
                elif query.startswith('entity '):
                    entity_name = query[7:].strip()
                    entity_info = self.search_entity(entity_name)
                    
                    if entity_info:
                        print(f"\\\\n📝 Information about '{entity_name}':")
                        print(f"   Type: {entity_info['type']}")
                        print(f"   Appears in {len(entity_info['chunks'])} chunks")
                        related = entity_info['co_occurring_entities'][:5]
                        if related:
                            print(f"   Related: {', '.join(related)}")
                    else:
                        print(f"❌ Entity '{entity_name}' not found")
                
                elif query.startswith('entities '):
                    entity_type = query[9:].strip()
                    entities = self.get_all_entities_by_type(entity_type)
                    
                    if entities:
                        print(f"\\\\n📋 {entity_type.title()} ({len(entities)} total):")
                        for entity in entities[:15]:
                            print(f"   - {entity}")
                        if len(entities) > 15:
                            print(f"   ... and {len(entities) - 15} more")
                    else:
                        print(f"❌ No entities found for type '{entity_type}'")
                
                elif query.lower() == 'stats':
                    print(f"\\\\n📊 KNOWLEDGE BASE STATISTICS")
                    print(f"   Source: {self.kb['metadata']['source_file']}")
                    print(f"   Total chunks: {self.kb['metadata']['total_chunks']}")
                    print(f"   Total entities: {self.kb['metadata']['total_entities']}")
                    for entity_type, entities in self.kb['entities'].items():
                        print(f"   {entity_type}: {len(entities)} items")
                
                else:
                    print("❌ Unknown command")
            
            except KeyboardInterrupt:
                break
        
        print("\\\\n👋 Goodbye!")

def main():
    searcher = KnowledgeBaseSearcher()
    if hasattr(searcher, 'kb'):
        searcher.interactive_search()

if __name__ == "__main__":
    main()
'''
        
        search_file = os.path.join(self.output_dir, "search_interface.py")
        with open(search_file, 'w', encoding='utf-8') as f:
            f.write(search_code)
        
        print(f"✅ Created search interface: {search_file}")
        return True
    
    def build_complete_knowledge_base(self, chunk_size: int = 500, overlap: int = 50):
        """Run all steps to build complete knowledge base"""
        print("🏗️ BUILDING COMPLETE KNOWLEDGE BASE")
        print("=" * 60)
        
        steps = [
            ("Loading and cleaning text", self.step1_load_and_clean_text),
            ("Creating text chunks", lambda: self.step2_create_chunks(chunk_size, overlap)),
            ("Extracting entities", self.step3_extract_entities),
            ("Building knowledge base", self.step4_build_knowledge_base),
            ("Creating search interface", self.step5_create_search_interface)
        ]
        
        for step_name, step_function in steps:
            print(f"\n🔄 {step_name}...")
            try:
                success = step_function()
                if not success:
                    print(f"❌ Failed at step: {step_name}")
                    return False
            except Exception as e:
                print(f"❌ Error in {step_name}: {e}")
                return False
        
        print("\n🎉 KNOWLEDGE BASE CREATION COMPLETED!")
        print("=" * 60)
        print(f"📁 Files saved to: {self.output_dir}")
        print(f"🔍 Run: python {self.output_dir}/search_interface.py")
        
        return True


# MAIN EXECUTION
if __name__ == "__main__":
    print("🏗️ SIMPLE KNOWLEDGE BASE BUILDER")
    print("=" * 50)
    
    text_file = input("\nEnter path to your text file: ").strip()
    if not text_file or not os.path.exists(text_file):
        print("❌ Please provide a valid text file path")
        exit()
    
    output_dir = input("Enter output directory (press Enter for auto): ").strip()
    if not output_dir:
        output_dir = f"./knowledge_base_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    builder = SimpleKnowledgeBaseBuilder(text_file, output_dir)
    success = builder.build_complete_knowledge_base()
    
    if success:
        print("\n✅ Success! Your knowledge base is ready.")
        print("🔍 Try the search interface to explore your content!")
    else:
        print("\n❌ Knowledge base creation failed.")
