
import json
import re
import os
from typing import List, Dict

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("❌ Google Generative AI not available. Install with: pip install google-generativeai")
    exit()

class UpdatedGeminiRAGChatbot:
    def __init__(self, kb_file_path: str, api_key: str):
        """Initialize RAG chatbot with knowledge base and Gemini API"""
        print("🔄 Loading knowledge base...")

        # Load knowledge base
        with open(kb_file_path, 'r', encoding='utf-8') as f:
            self.kb = json.load(f)

        self.chunks = {chunk['id']: chunk for chunk in self.kb['chunks']}
        self.search_index = self.kb['search_index']

        print("🤖 UPDATED Gemini-Powered Sanskrit/Tamil Textbook Chatbot Ready!")
        print(f"📚 Loaded {len(self.chunks)} chunks from your textbook")
        print(f"🔍 Search index has {len(self.search_index)} terms")

        # Initialize Gemini with CORRECT model name
        try:
            genai.configure(api_key=api_key)
            # Try different model names that are currently available
            model_options = [
                'gemini-1.5-flash',
                'gemini-1.5-pro', 
                'gemini-1.0-pro',
                'models/gemini-1.5-flash',
                'models/gemini-1.0-pro'
            ]

            self.model = None
            for model_name in model_options:
                try:
                    print(f"🔄 Trying model: {model_name}")
                    self.model = genai.GenerativeModel(model_name)
                    # Test the model with a simple request
                    test_response = self.model.generate_content("Hello")
                    print(f"✅ Successfully connected to: {model_name}")
                    break
                except Exception as e:
                    print(f"❌ {model_name} failed: {str(e)[:100]}...")
                    continue

            if not self.model:
                print("❌ All Gemini models failed. Using template responses.")

        except Exception as e:
            print(f"❌ Gemini API connection failed: {e}")
            print("Continuing with template responses...")
            self.model = None

    def retrieve_context(self, question: str, limit: int = 3) -> List[Dict]:
        """Retrieve relevant chunks from knowledge base"""
        # Fixed regex pattern
        question_words = re.findall(r'\b[a-zA-Z]{3,}\b', question.lower())

        print(f"🔍 Searching for words: {question_words}")

        # Debug: Show some search index terms
        sample_terms = list(self.search_index.keys())[:10]
        print(f"🔍 Available terms sample: {sample_terms}")

        chunk_scores = {}
        for word in question_words:
            print(f"   Checking word: '{word}'")
            if word in self.search_index:
                chunk_count = len(self.search_index[word])
                print(f"   ✅ Found '{word}' in {chunk_count} chunks")
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
                print(f"   📄 Selected chunk: {chunk_id} (score: {score})")

        return results

    def generate_with_gemini(self, question: str, context: str) -> str:
        """Generate response using Gemini API with RAG"""
        if not self.model:
            return None

        prompt = f"""You are a scholarly assistant specializing in Sanskrit and Tamil studies. Answer the user's question based ONLY on the provided textbook context.

CONTEXT FROM TEXTBOOK:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
- Answer based ONLY on the provided context from the textbook
- If the context doesn't contain enough information, say so clearly
- Preserve any Sanskrit or Tamil terms mentioned exactly as they appear
- Be scholarly and accurate in your explanation
- Provide specific references to the content when possible

Please provide a comprehensive answer:"""

        try:
            print("🤖 Generating response with Gemini...")
            response = self.model.generate_content(prompt)

            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
            else:
                print("❌ Gemini returned empty response")
                return None

        except Exception as e:
            print(f"❌ Gemini API Error: {e}")
            return None

    def generate_template_response(self, question: str, context_chunks: List[Dict]) -> str:
        """Generate template-based response without API"""
        if not context_chunks:
            return f"""I couldn't find relevant information about '{question}' in your textbook.

Try asking about these terms that ARE in your textbook:
• Sanskrit terms: cha, tad, chatur, iti, chaiva, tri, tat, deha, bhavet
• Measurement terms: span, measure, measures, equal

Or try: "What does the text say about [term]?" """

        response = f"Based on your Sanskrit/Tamil textbook, here's what I found about '{question}':\n\n"

        for i, chunk in enumerate(context_chunks, 1):
            text = chunk['text'][:600] + "..." if len(chunk['text']) > 600 else chunk['text']
            response += f"**Section {i} (Relevance Score: {chunk['score']}):**\n{text}\n\n"

        response += f"\n📍 This information comes from {len(context_chunks)} sections of your textbook."

        # Add intelligent suggestions based on content
        all_text = " ".join([chunk['text'].lower() for chunk in context_chunks])
        if 'measure' in all_text or 'span' in all_text:
            response += "\n\n💡 This appears to discuss Sanskrit measurement systems and mathematical concepts."

        return response

    def answer_question(self, question: str) -> str:
        """Main RAG pipeline: Retrieve + Generate"""
        context_chunks = self.retrieve_context(question, limit=3)

        if not context_chunks:
            return self.generate_template_response(question, [])

        context_text = "\n\n".join([f"Section {i+1}: {chunk['text']}" for i, chunk in enumerate(context_chunks)])

        if self.model:
            ai_response = self.generate_with_gemini(question, context_text)
            if ai_response:
                return f"{ai_response}\n\n📚 Source: {len(context_chunks)} sections from your textbook"

        return self.generate_template_response(question, context_chunks)

    def chat(self):
        """Interactive chat interface"""
        print("\n" + "="*70)
        print("🏛️ UPDATED GEMINI SANSKRIT/TAMIL TEXTBOOK CHATBOT")
        print("="*70)
        print("Ask questions about your textbook! Type 'quit' to exit.")
        print("\nSuggested terms: span, chatur, equal, measure, deha, cha")
        print("="*70)

        while True:
            try:
                question = input("\n📚 Ask about your textbook: ").strip()

                if question.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Happy studying!")
                    break

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

def main():
    print("🚀 UPDATED GEMINI RAG CHATBOT FOR SANSKRIT/TAMIL TEXTBOOK")
    print("=" * 60)

    # Check knowledge base
    kb_path = "F:/TANCAM/knowledge_base/knowledge_base_20251024_153040/knowledge_base.json"
    if not os.path.exists(kb_path):
        print(f"❌ Knowledge base not found: {kb_path}")
        return

    print(f"✅ Found knowledge base")

    # SIMPLE API KEY INPUT
    print("\n🔑 GEMINI API KEY SETUP")
    print("-" * 30)
    print("Get FREE API key from: https://makersuite.google.com/app/apikey")
    print()

    api_key = input("Enter your Gemini API key (or press Enter to skip): ").strip()

    if not api_key:
        print("❌ No API key provided! Using template responses only.")
        print("You'll still get good responses from your textbook content!")
        api_key = "dummy"  # Use dummy key to enable template responses
    else:
        print("✅ API key received!")

    print("\n" + "=" * 60)

    try:
        chatbot = UpdatedGeminiRAGChatbot(kb_path, api_key)
        chatbot.chat()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
