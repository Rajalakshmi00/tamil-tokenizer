import json
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
        
        query_words = re.findall(r'\\b[a-zA-Z]{3,}\\b', query.lower())
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
        print("\\nEntity types: sanskrit_terms, tamil_terms, persons, places, concepts, dates")
        print("=" * 50)
        
        while True:
            try:
                query = input("\\n> ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                
                if query.startswith('search '):
                    search_term = query[7:].strip()
                    results = self.search_text(search_term, limit=3)
                    
                    if results:
                        print(f"\\n📄 Found {len(results)} results for '{search_term}':")
                        for i, result in enumerate(results, 1):
                            print(f"\\n{i}. [Score: {result['score']}] {result['chunk_id']}")
                            print(f"   {result['text']}")
                    else:
                        print(f"❌ No results found for '{search_term}'")
                
                elif query.startswith('entity '):
                    entity_name = query[7:].strip()
                    entity_info = self.search_entity(entity_name)
                    
                    if entity_info:
                        print(f"\\n📝 Information about '{entity_name}':")
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
                        print(f"\\n📋 {entity_type.title()} ({len(entities)} total):")
                        for entity in entities[:15]:
                            print(f"   - {entity}")
                        if len(entities) > 15:
                            print(f"   ... and {len(entities) - 15} more")
                    else:
                        print(f"❌ No entities found for type '{entity_type}'")
                
                elif query.lower() == 'stats':
                    print(f"\\n📊 KNOWLEDGE BASE STATISTICS")
                    print(f"   Source: {self.kb['metadata']['source_file']}")
                    print(f"   Total chunks: {self.kb['metadata']['total_chunks']}")
                    print(f"   Total entities: {self.kb['metadata']['total_entities']}")
                    for entity_type, entities in self.kb['entities'].items():
                        print(f"   {entity_type}: {len(entities)} items")
                
                else:
                    print("❌ Unknown command")
            
            except KeyboardInterrupt:
                break
        
        print("\\n👋 Goodbye!")

def main():
    searcher = KnowledgeBaseSearcher()
    if hasattr(searcher, 'kb'):
        searcher.interactive_search()

if __name__ == "__main__":
    main()
