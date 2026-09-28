# hybrid_tamil_tokenizer.py
import torch
from transformers import AutoTokenizer, AutoModel
from reverse_sandhi_rules import REVERSE_RULES
import re
import warnings
warnings.filterwarnings("ignore")

class HybridTamilTokenizer:
    def __init__(self, corpus_path="tamil_corpus.txt", confidence_threshold=0.7):
        """
        Initialize hybrid tokenizer with IndicBERT + custom rules
        """
        # Try multiple Tamil tokenizer options
        print("Loading Tamil tokenizer...")
        
        try:
            # Option 1: Try IndicBERT with specific parameters
            self.indicbert_tokenizer = AutoTokenizer.from_pretrained(
                "ai4bharat/indic-bert", 
                use_fast=False,  # Use slow tokenizer to avoid conversion issues
                trust_remote_code=True
            )
            print("✓ Loaded ai4bharat/indic-bert tokenizer")
        except Exception as e:
            try:
                # Option 2: Try multilingual BERT
                self.indicbert_tokenizer = AutoTokenizer.from_pretrained(
                    "bert-base-multilingual-cased",
                    use_fast=False
                )
                print("✓ Loaded bert-base-multilingual-cased tokenizer (fallback)")
            except Exception as e2:
                try:
                    # Option 3: Try Tamil-specific model
                    self.indicbert_tokenizer = AutoTokenizer.from_pretrained(
                        "l3cube-pune/tamil-bert",
                        use_fast=False
                    )
                    print("✓ Loaded l3cube-pune/tamil-bert tokenizer (fallback)")
                except Exception as e3:
                    print(f"❌ All tokenizer loading failed. Using basic tokenizer.")
                    self.indicbert_tokenizer = None
        
        # Load Tamil corpus
        self.vocab = self.load_corpus(corpus_path)
        print(f"✓ Loaded {len(self.vocab)} words from Tamil corpus")
        
        # Set confidence threshold for applying custom rules
        self.confidence_threshold = confidence_threshold
        
        print("✓ Hybrid Tamil Tokenizer initialized successfully!")
    
    def load_corpus(self, path):
        """Load Tamil vocabulary from corpus file"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                vocab = set(w.strip() for w in f.readlines() if w.strip())
            return vocab
        except FileNotFoundError:
            print(f"❌ Warning: {path} not found. Using empty vocabulary.")
            return set()
    
    def basic_tamil_tokenize(self, text):
        """Basic Tamil tokenization fallback if IndicBERT fails"""
        # Simple whitespace and punctuation based tokenization
        import re
        # Split on whitespace and common punctuation
        tokens = re.findall(r'[\u0B80-\u0BFF]+|[a-zA-Z]+|\S', text)
        return tokens
    
    def apply_custom_rules(self, word):
        """Apply reverse sandhi rules to split compound words"""
        if len(word) < 3:  # Skip very short words
            return [word]
        
        # Try all reverse sandhi rules
        all_splits = []
        for rule in REVERSE_RULES:
            try:
                splits = rule(word)
                for w1, w2 in splits:
                    # Validate both parts exist in corpus
                    if w1 in self.vocab and w2 in self.vocab:
                        all_splits.append([w1, w2])
            except Exception as e:
                continue
        
        # Return best split or original word
        if all_splits:
            return all_splits[0]  # Return first valid split
        return [word]
    
    def estimate_confidence(self, token, original_text):
        """
        Estimate tokenizer confidence based on various factors
        """
        # Check if token is a known Tamil word
        if token in self.vocab:
            return 0.9
        
        # Check if token contains Tamil characters
        tamil_pattern = r'[\u0B80-\u0BFF]+'
        if not re.search(tamil_pattern, token):
            return 0.3  # Low confidence for non-Tamil tokens
        
        # Check token length (very long tokens might be incorrectly merged)
        if len(token) > 15:
            return 0.4
        
        # Check for obvious compound patterns
        compound_patterns = ['ல்ல', 'ங்க', 'ม्ப', 'ஞ்ச', 'ய்', 'வ்']
        for pattern in compound_patterns:
            if pattern in token:
                return 0.5  # Medium confidence, might need splitting
        
        return 0.8  # Default confidence
    
    def tokenize(self, text, apply_custom_rules=True, debug=False):
        """
        Main tokenization function combining IndicBERT + custom rules
        """
        if debug:
            print(f"\n=== Tokenizing: '{text}' ===")
        
        # Step 1: Get base tokenization
        if self.indicbert_tokenizer:
            try:
                base_tokens = self.indicbert_tokenizer.tokenize(text)
            except Exception as e:
                if debug:
                    print(f"IndicBERT failed: {e}")
                base_tokens = self.basic_tamil_tokenize(text)
        else:
            base_tokens = self.basic_tamil_tokenize(text)
        
        if debug:
            print(f"Base tokens: {base_tokens}")
        
        if not apply_custom_rules:
            return base_tokens
        
        # Step 2: Apply custom rules to low-confidence tokens
        enhanced_tokens = []
        
        for token in base_tokens:
            # Skip special tokens and punctuation
            if token.startswith('##') or token in ['[CLS]', '[SEP]', '[PAD]', '[UNK]'] or len(token) <= 1:
                enhanced_tokens.append(token)
                continue
            
            # Estimate confidence
            confidence = self.estimate_confidence(token, text)
            
            if debug:
                print(f"Token: '{token}', Confidence: {confidence:.2f}")
            
            # Apply custom rules if confidence is low
            if confidence < self.confidence_threshold:
                custom_result = self.apply_custom_rules(token)
                if len(custom_result) > 1:
                    if debug:
                        print(f"  ✓ Custom split: '{token}' → {custom_result}")
                    enhanced_tokens.extend(custom_result)
                else:
                    enhanced_tokens.append(token)
            else:
                enhanced_tokens.append(token)
        
        if debug:
            print(f"Final tokens: {enhanced_tokens}")
        
        return enhanced_tokens
    
    def tokenize_batch(self, texts, apply_custom_rules=True):
        """Tokenize multiple texts efficiently"""
        results = []
        for text in texts:
            results.append(self.tokenize(text, apply_custom_rules))
        return results
    
    def evaluate_improvement(self, test_texts):
        """Compare hybrid vs base tokenizer performance"""
        print("\n=== Performance Comparison ===")
        
        for text in test_texts:
            print(f"\nText: '{text}'")
            
            # Base tokenizer only
            base_only = self.tokenize(text, apply_custom_rules=False)
            print(f"Base tokenizer: {base_only}")
            
            # Hybrid approach
            hybrid_result = self.tokenize(text, apply_custom_rules=True)
            print(f"Hybrid result:  {hybrid_result}")
            
            # Show difference
            if base_only != hybrid_result:
                print("  → ✓ Enhancement applied!")
            else:
                print("  → No change needed")

# Test function
def main():
    # Initialize tokenizer
    tokenizer = HybridTamilTokenizer("tamil_corpus.txt", confidence_threshold=0.7)
    
    # Test cases - add your Tamil literature examples
    test_texts = [
        "கல்விசாலை",
        "நல்லவரவு", 
        "தமிழ்நாடு",
        "பல்லை",
        "நரியா",
        "பூவா",
        "Tamil literature is rich and diverse",
        "கல்லூரிக்கு செல்கிறேன்"
    ]
    
    print("=== Hybrid Tamil Tokenizer Demo ===")
    
    # Test individual tokenization with debug
    for text in test_texts[:3]:
        result = tokenizer.tokenize(text, debug=True)
        print(f"Result: {result}\n")
    
    # Batch processing
    print("\n=== Batch Processing ===")
    batch_results = tokenizer.tokenize_batch(test_texts)
    for text, tokens in zip(test_texts, batch_results):
        print(f"'{text}' → {tokens}")
    
    # Performance evaluation
    tokenizer.evaluate_improvement(test_texts)

if __name__ == "__main__":
    main()
