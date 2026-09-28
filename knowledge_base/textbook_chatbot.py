
import json
import re
from typing import List, Dict

class TextbookChatbot:
    def __init__(self, kb_file_path: str):
        """Initialize chatbot with your knowledge base"""
        with open(kb_file_path, 'r', encoding='utf-8') as f:
            self.kb = json.load(f)

        self.chunks = {chunk['id']: chunk for chunk in self.kb['chunks']}
        self.search_index = self.kb['search_index']

        print("🤖 Sanskrit/Tamil Textbook Chatbot Ready!")
        print(f"📚 Loaded {len(self.chunks)} chunks from your textbook")

    def search_relevant_chunks(self, question: str, limit: int = 3) -> List[Dict]:
        """Find relevant text chunks for the question"""
        question_words = re.findall(r'\\b[a-zA-Z]{3,}\\b', question.lower())

        chunk_scores = {}
        for word in question_words:
            if word in self.search_index:
                for chunk_id in self.search_index[word]:
                    chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0) + 1

        # Sort by relevance
        sorted_chunks = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)

        results = []
        for chunk_id, score in sorted_chunks[:limit]:
            if chunk_id in self.chunks:
                results.append({
                    'text': self.chunks[chunk_id]['text'],
                    'score': score,
                    'chunk_id': chunk_id
                })

        return results

    def generate_answer(self, question: str) -> str:
        """Generate answer based on relevant chunks"""
        relevant_chunks = self.search_relevant_chunks(question)

        if not relevant_chunks:
            return "I couldn't find relevant information in the textbook to answer your question. Try rephrasing or asking about different topics."

        # Create context-based answer
        context = "\\n\\n".join([chunk['text'] for chunk in relevant_chunks])

        answer = f"""Based on your textbook, here's what I found:

{context[:800]}{'...' if len(context) > 800 else ''}

(This information comes from {len(relevant_chunks)} relevant sections of your textbook)"""

        return answer

    def chat(self):
        """Interactive chat interface"""
        print("\\n" + "="*60)
        print("🏛️ SANSKRIT/TAMIL TEXTBOOK CHATBOT")
        print("="*60)
        print("Ask me questions about your textbook content!")
        print("Type 'quit' to exit, 'help' for examples")
        print("="*60)

        while True:
            try:
                question = input("\\n📚 You: ").strip()

                if question.lower() in ['quit', 'exit', 'q']:
                    print("\\n👋 Goodbye! Happy learning!")
                    break

                if question.lower() == 'help':
                    print("""
🆘 Example questions you can ask:
- What is mentioned about Sanskrit philosophy?
- Tell me about Tamil culture
- What does the book say about ancient temples?
- Explain the historical context mentioned
- What are the main concepts discussed?
- Who are the important figures mentioned?
                    """)
                    continue

                if not question:
                    print("Please ask a question!")
                    continue

                print("\\n🤖 Bot: ", end="")
                answer = self.generate_answer(question)
                print(answer)

            except KeyboardInterrupt:
                print("\\n\\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\\n❌ Error: {e}")

def main():
    # Update this path to your knowledge base file
    kb_path = "F:/TANCAM/knowledge_base/knowledge_base_20251024_153040/knowledge_base.json"

    try:
        chatbot = TextbookChatbot(kb_path)
        chatbot.chat()
    except FileNotFoundError:
        print("❌ Knowledge base file not found!")
        print("Make sure the path is correct:")
        print(kb_path)
    except Exception as e:
        print(f"❌ Error starting chatbot: {e}")

if __name__ == "__main__":
    main()
