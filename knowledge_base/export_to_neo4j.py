
import json
import re
from typing import List, Dict

class Neo4jExporter:
    def __init__(self, kb_file_path: str):
        """Load knowledge base for Neo4j export"""
        with open(kb_file_path, 'r', encoding='utf-8') as f:
            self.kb = json.load(f)

        print(f"📊 Loaded knowledge base with {len(self.kb['chunks'])} chunks")

    def generate_cypher_script(self, output_file: str = "import_to_neo4j.cypher"):
        """Generate Cypher script to import data into Neo4j"""

        cypher_commands = []

        # Create document nodes
        cypher_commands.append("// Create Document nodes")
        cypher_commands.append("CREATE (doc:Document {name: 'Sanskrit_Tamil_Textbook', source: 'Extracted_Text'});")

        # Create chunk nodes
        cypher_commands.append("\\n// Create Chunk nodes")
        for chunk in self.kb['chunks']:
            chunk_text = chunk['text'].replace("'", "\\'").replace('"', '\\"')[:200] + "..."
            cypher_commands.append(f"""
CREATE (chunk_{chunk['id'].replace('-', '_')}:Chunk {{
    id: '{chunk['id']}',
    text: "{chunk_text}",
    word_count: {chunk['word_count']}
}});""")

        # Connect chunks to document
        cypher_commands.append("\\n// Connect chunks to document")
        for chunk in self.kb['chunks']:
            chunk_id = chunk['id'].replace('-', '_')
            cypher_commands.append(f"MATCH (doc:Document), (chunk:Chunk {{id: '{chunk['id']}'}}) CREATE (doc)-[:CONTAINS]->(chunk);")

        # Create entity nodes and relationships
        for entity_type, entities in self.kb['entities'].items():
            if entities:  # Only if entities exist
                label = entity_type.replace('_', '').title()
                cypher_commands.append(f"\\n// Create {label} entities")

                for entity in entities:
                    entity_safe = entity.replace("'", "\\'").replace('"', '\\"')
                    entity_id = re.sub(r'[^a-zA-Z0-9_]', '_', entity)
                    cypher_commands.append(f"CREATE ({entity_id}:{label} {{name: '{entity_safe}'}});")

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\\n".join(cypher_commands))

        print(f"✅ Generated Neo4j Cypher script: {output_file}")
        print("\\n📋 To use:")
        print("1. Start Neo4j Desktop or Neo4j Browser")
        print("2. Open the Cypher script file")
        print("3. Copy and paste commands into Neo4j Browser")
        print("4. Run each section separately")

        return output_file

def main():
    # Update this path to your knowledge base
    kb_path = "F:/TANCAM/knowledge_base/knowledge_base_20251024_153040/knowledge_base.json"

    try:
        exporter = Neo4jExporter(kb_path)
        exporter.generate_cypher_script()
    except FileNotFoundError:
        print("❌ Knowledge base file not found!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
