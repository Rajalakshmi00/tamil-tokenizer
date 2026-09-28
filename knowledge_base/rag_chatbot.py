
import json
import re
import requests
import os
import sys
from typing import List, Dict

class FixedRAGChatbot:
    def __init__(self, kb_file_path: str, api_key: str = None):
        """Initialize RAG chatbot with knowledge base and optional API"""
        print("🔄 Loading knowledge base...")

        # Load knowledge base
        with open(kb_file_path, 'r', encoding='utf-8') as f:
            self.kb = json.load(f)

        self.chunks = {chunk['id']: chunk for chunk in self.kb['chunks']}
        self.search_index = self.kb['search_index']
        self.api_key = api_key

        print("🤖 FIXED RAG-Powered Sanskrit/Tamil Textbook Chatbot Ready!")
        print(f"📚 Loaded {len(self.chunks)} chunks from your textbook")
        print(f"🔍 Search index has {len(self.search_index)} terms")

        if api_key:
            print("🔗 Connected to Perplexity API for enhanced responses")
        else:
            print("💭 Using template-based responses (no API key provided)")

    def retrieve_context(self, question: str, limit: int = 3) -> List[Dict]:
        """FIXED: Retrieve relevant chunks from knowledge base"""
        # Fix the regex pattern - remove extra backslashes
        question_words = re.findall(r'\b[a-zA-Z]{3,}\b', question.lower())

        print(f"🔍 Debug: Searching for words: {question_words}")

        chunk_scores = {}
        for word in question_words:
            print(f"   Checking word: '{word}'")
            if word in self.search_index:
                print(f"   ✅ Found '{word}' in {len(self.search_index[word])} chunks")
                for chunk_id in self.search_index[word]:
                    chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0) + 1
            else:
                print(f"   ❌ '{word}' not found in search index")

        print(f"🎯 Found {len(chunk_scores)} matching chunks")

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

    def generate_with_api(self, question: str, context: str) -> str:
        """Generate response using Perplexity API with RAG"""
        if not self.api_key:
            return None

        # Create RAG prompt
        prompt = f"""You are a helpful assistant specializing in Sanskrit and Tamil studies. Answer the user's question based ONLY on the provided textbook context.

CONTEXT FROM TEXTBOOK:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
- Answer based ONLY on the provided context
- If the context doesn't contain enough information, say so
- Preserve any Sanskrit or Tamil terms mentioned
- Be scholarly and accurate
- Provide specific references when possible

ANSWER:"""

        try:
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-sonar-large-128k-online",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 800,
                    "temperature": 0.3
                }
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                print(f"API Error: {response.status_code}")
                return None

        except Exception as e:
            print(f"API Error: {e}")
            return None

    def generate_template_response(self, question: str, context_chunks: List[Dict]) -> str:
        """Generate template-based response without API"""
        if not context_chunks:
            return f"""I couldn't find relevant information about '{question}' in your textbook.

However, I found these terms in your textbook that you can search for:
• Sanskrit terms: cha, tad, chatur, iti, chaiva, tri, tat, deha, bhavet
• Measurement terms: span, measure, measures, equal
• Academic terms: chap, ibid, objects

Try asking about these specific terms instead!"""

        # Create structured response
        response = f"Based on your Sanskrit/Tamil textbook, here's what I found about '{question}':\n\n"

        for i, chunk in enumerate(context_chunks, 1):
            text = chunk['text'][:500] + "..." if len(chunk['text']) > 500 else chunk['text']
            response += f"**Section {i} (Score: {chunk['score']}):**\n{text}\n\n"

        response += f"\n📍 This information comes from {len(context_chunks)} relevant sections of your textbook."

        return response

    def answer_question(self, question: str) -> str:
        """Main RAG pipeline: Retrieve + Generate"""
        # Step 1: Retrieve relevant context
        context_chunks = self.retrieve_context(question, limit=3)

        if not context_chunks:
            return self.generate_template_response(question, [])

        # Step 2: Prepare context for generation
        context_text = "\n\n".join([chunk['text'] for chunk in context_chunks])

        # Step 3: Generate response (API or template)
        if self.api_key:
            ai_response = self.generate_with_api(question, context_text)
            if ai_response:
                return f"{ai_response}\n\n📚 Source: {len(context_chunks)} sections from your textbook"

        # Fallback to template response
        return self.generate_template_response(question, context_chunks)

    def interactive_chat(self):
        """Interactive RAG chat interface"""
        print("\n" + "="*70)
        print("🏛️ FIXED RAG-POWERED SANSKRIT/TAMIL TEXTBOOK CHATBOT")
        print("="*70)
        print("I can answer questions about your textbook using RAG (Retrieval + AI)!")
        print("\nBased on your content, try these terms:")
        print("• Sanskrit terms: cha, tad, chatur, iti, chaiva, tri, tat, deha, bhavet")
        print("• Measurement terms: span, measure, measures, equal")
        print("\nType 'quit' to exit, 'help' for examples")
        print("="*70)

        while True:
            try:
                question = input("\n📚 Ask me about your textbook: ").strip()

                if question.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Happy studying!")
                    break

                if question.lower() == 'help':
                    print("""
🆘 TRY THESE SPECIFIC QUESTIONS:
- What does the text say about span?
- Tell me about Sanskrit measurement terms
- What is mentioned about chatur?
- Explain the concept of equal measures
- What does cha refer to?
- Tell me about deha
- What are the measurement objects?
                    """)
                    continue

                if not question:
                    print("Please ask a question!")
                    continue

                print("\n🤖 Analyzing textbook content...")
                answer = self.answer_question(question)
                print(f"\n{answer}")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

def get_api_key():
    """Force wait for API key input with multiple methods"""
    print("🚀 STARTING FIXED RAG CHATBOT SETUP")
    print("=" * 50)

    kb_path = "F:/TANCAM/knowledge_base/knowledge_base_20251024_153040/knowledge_base.json"

    # Check if knowledge base exists
    if not os.path.exists(kb_path):
        print(f"❌ Knowledge base file not found!")
        print(f"Expected location: {kb_path}")
        return None, None

    print(f"✅ Found knowledge base at: {kb_path}")
    print()

    # FORCE INPUT WAIT with multiple approaches
    print("🔑 PERPLEXITY API CONFIGURATION")
    print("-" * 30)
    print("Choose an option:")
    print("1. Enter Perplexity API key for AI responses")
    print("2. Skip API key (use template responses)")
    print()

    # Force flush output
    sys.stdout.flush()

    try:
        # Method 1: Try with choice first
        choice = input("Enter 1 or 2: ").strip()

        if choice == "1":
            print("\nEnter your Perplexity API key below:")
            print("(Paste and press Enter)")
            sys.stdout.flush()

            # Force wait for API key
            api_key = input("API Key: ").strip()

            if api_key:
                print(f"✅ API key configured (ends with: ...{api_key[-4:]})")
                return kb_path, api_key
            else:
                print("❌ No API key entered, using template mode")
                return kb_path, None

        elif choice == "2":
            print("💭 Using template-based responses")
            return kb_path, None

        else:
            print("Invalid choice, using template mode")
            return kb_path, None

    except Exception as e:
        print(f"Input error: {e}")
        print("Using template mode")
        return kb_path, None

def main():
    # Get configuration with forced input
    kb_path, api_key = get_api_key()

    if not kb_path:
        return

    print("\n" + "=" * 50)

    try:
        chatbot = FixedRAGChatbot(kb_path, api_key)
        chatbot.interactive_chat()
    except FileNotFoundError:
        print("❌ Knowledge base file not found!")
        print(f"Expected location: {kb_path}")
    except Exception as e:
        print(f"❌ Error starting RAG chatbot: {e}")

if __name__ == "__main__":
    main()
