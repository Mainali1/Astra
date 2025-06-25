"""
Text Summarization Feature for Astra Voice Assistant

This module provides text summarization capabilities including:
- Extractive summarization
- Abstractive summarization
- Multiple summarization algorithms
- Voice commands for text summarization
"""

import re
import nltk
from typing import Dict, List, Optional, Any
from collections import Counter
import requests
import json
import os
import PyPDF2
import docx
from bs4 import BeautifulSoup


class TextSummarizer:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        self.stop_words = set(nltk.corpus.stopwords.words('english'))
        self.supported_formats = ['.txt', '.pdf', '.docx', '.md', '.html']
    
    def extractive_summarize(self, text: str, num_sentences: int = 3) -> str:
        """Extractive summarization using TF-IDF approach"""
        try:
            # Clean and preprocess text
            sentences = self._split_into_sentences(text)
            if len(sentences) <= num_sentences:
                return text
            
            # Calculate sentence scores
            sentence_scores = self._calculate_sentence_scores(sentences)
            
            # Get top sentences
            top_sentences = sorted(sentence_scores.items(), 
                                 key=lambda x: x[1], reverse=True)[:num_sentences]
            
            # Sort by original order
            top_sentences.sort(key=lambda x: sentences.index(x[0]))
            
            # Join sentences
            summary = ' '.join([sentence for sentence, score in top_sentences])
            
            return summary
            
        except Exception as e:
            print(f"Error in extractive summarization: {e}")
            return text[:500] + "..." if len(text) > 500 else text
    
    def frequency_based_summarize(self, text: str, num_sentences: int = 3) -> str:
        """Frequency-based summarization"""
        try:
            sentences = self._split_into_sentences(text)
            if len(sentences) <= num_sentences:
                return text
            
            # Get word frequencies
            word_frequencies = self._get_word_frequencies(text)
            
            # Calculate sentence scores based on word frequencies
            sentence_scores = {}
            for sentence in sentences:
                score = sum(word_frequencies.get(word.lower(), 0) 
                          for word in sentence.split() 
                          if word.lower() not in self.stop_words)
                sentence_scores[sentence] = score
            
            # Get top sentences
            top_sentences = sorted(sentence_scores.items(), 
                                 key=lambda x: x[1], reverse=True)[:num_sentences]
            
            # Sort by original order
            top_sentences.sort(key=lambda x: sentences.index(x[0]))
            
            # Join sentences
            summary = ' '.join([sentence for sentence, score in top_sentences])
            
            return summary
            
        except Exception as e:
            print(f"Error in frequency-based summarization: {e}")
            return text[:500] + "..." if len(text) > 500 else text
    
    def luhn_summarize(self, text: str, num_sentences: int = 3) -> str:
        """Luhn's algorithm for summarization"""
        try:
            sentences = self._split_into_sentences(text)
            if len(sentences) <= num_sentences:
                return text
            
            # Get word frequencies
            word_frequencies = self._get_word_frequencies(text)
            
            # Calculate sentence scores using Luhn's algorithm
            sentence_scores = {}
            for sentence in sentences:
                words = sentence.split()
                significant_words = [word.lower() for word in words 
                                   if word.lower() not in self.stop_words 
                                   and word_frequencies.get(word.lower(), 0) > 1]
                
                if len(significant_words) == 0:
                    sentence_scores[sentence] = 0
                    continue
                
                # Calculate clusters of significant words
                clusters = self._find_significant_clusters(words, significant_words)
                score = sum(len(cluster) ** 2 for cluster in clusters)
                sentence_scores[sentence] = score
            
            # Get top sentences
            top_sentences = sorted(sentence_scores.items(), 
                                 key=lambda x: x[1], reverse=True)[:num_sentences]
            
            # Sort by original order
            top_sentences.sort(key=lambda x: sentences.index(x[0]))
            
            # Join sentences
            summary = ' '.join([sentence for sentence, score in top_sentences])
            
            return summary
            
        except Exception as e:
            print(f"Error in Luhn summarization: {e}")
            return text[:500] + "..." if len(text) > 500 else text
    
    def api_summarize(self, text: str, api_type: str = "textanalysis") -> str:
        """Summarize using external APIs"""
        try:
            if api_type == "textanalysis":
                return self._textanalysis_api_summarize(text)
            elif api_type == "rapidapi":
                return self._rapidapi_summarize(text)
            else:
                return self.extractive_summarize(text)
                
        except Exception as e:
            print(f"Error in API summarization: {e}")
            return self.extractive_summarize(text)
    
    def _textanalysis_api_summarize(self, text: str) -> str:
        """Summarize using Text Analysis API (free tier)"""
        try:
            # This is a placeholder for a free text analysis API
            # In practice, you would use a real API like:
            # - Microsoft Azure Text Analytics
            # - Google Cloud Natural Language API
            # - IBM Watson Natural Language Understanding
            
            # For now, fall back to extractive summarization
            return self.extractive_summarize(text)
            
        except Exception as e:
            print(f"Error in Text Analysis API: {e}")
            return self.extractive_summarize(text)
    
    def _rapidapi_summarize(self, text: str) -> str:
        """Summarize using RapidAPI (free tier)"""
        try:
            # This is a placeholder for RapidAPI summarization
            # You would need to sign up for a free API key
            
            # For now, fall back to extractive summarization
            return self.extractive_summarize(text)
            
        except Exception as e:
            print(f"Error in RapidAPI: {e}")
            return self.extractive_summarize(text)
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        try:
            sentences = nltk.sent_tokenize(text)
            return [s.strip() for s in sentences if s.strip()]
        except:
            # Fallback to simple sentence splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
    
    def _get_word_frequencies(self, text: str) -> Dict[str, int]:
        """Get word frequencies from text"""
        words = re.findall(r'\b\w+\b', text.lower())
        words = [word for word in words if word not in self.stop_words]
        return Counter(words)
    
    def _calculate_sentence_scores(self, sentences: List[str]) -> Dict[str, float]:
        """Calculate sentence scores using TF-IDF approach"""
        # Get word frequencies
        all_words = []
        for sentence in sentences:
            words = re.findall(r'\b\w+\b', sentence.lower())
            words = [word for word in words if word not in self.stop_words]
            all_words.extend(words)
        
        word_frequencies = Counter(all_words)
        
        # Calculate sentence scores
        sentence_scores = {}
        for sentence in sentences:
            words = re.findall(r'\b\w+\b', sentence.lower())
            words = [word for word in words if word not in self.stop_words]
            
            if len(words) == 0:
                sentence_scores[sentence] = 0
                continue
            
            # Calculate average word frequency
            total_score = sum(word_frequencies[word] for word in words)
            sentence_scores[sentence] = total_score / len(words)
        
        return sentence_scores
    
    def _find_significant_clusters(self, words: List[str], significant_words: List[str]) -> List[List[str]]:
        """Find clusters of significant words in a sentence"""
        clusters = []
        current_cluster = []
        
        for word in words:
            if word.lower() in significant_words:
                current_cluster.append(word)
            else:
                if len(current_cluster) > 0:
                    clusters.append(current_cluster)
                    current_cluster = []
        
        if len(current_cluster) > 0:
            clusters.append(current_cluster)
        
        return clusters
    
    def get_summary_stats(self, original_text: str, summary: str) -> Dict[str, Any]:
        """Get statistics about the summarization"""
        try:
            original_sentences = len(self._split_into_sentences(original_text))
            summary_sentences = len(self._split_into_sentences(summary))
            
            original_words = len(original_text.split())
            summary_words = len(summary.split())
            
            return {
                'original_length': len(original_text),
                'summary_length': len(summary),
                'compression_ratio': len(summary) / len(original_text) if len(original_text) > 0 else 0,
                'original_sentences': original_sentences,
                'summary_sentences': summary_sentences,
                'original_words': original_words,
                'summary_words': summary_words,
                'sentence_reduction': (original_sentences - summary_sentences) / original_sentences if original_sentences > 0 else 0,
                'word_reduction': (original_words - summary_words) / original_words if original_words > 0 else 0
            }
        except Exception as e:
            print(f"Error calculating summary stats: {e}")
            return {}

    async def extract_text_from_document(self, file_path: str) -> str:
        """Extract text from various document formats"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format. Supported formats: {self.supported_formats}")
            
        if ext == '.pdf':
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
                
        elif ext == '.docx':
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
        elif ext == '.html':
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                return soup.get_text()
                
        else:  # .txt or .md
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()

    async def summarize_document(self, file_path: str, method: str = "api", num_sentences: int = 5) -> dict:
        """Summarize a document file"""
        try:
            text = await self.extract_text_from_document(file_path)
            summary = await self.summarize_text(text, method, num_sentences)
            stats = self.get_summary_stats(text, summary)
            
            return {
                "original_text": text,
                "summary": summary,
                "stats": stats,
                "file_path": file_path,
                "method": method
            }
        except Exception as e:
            return {
                "error": str(e),
                "file_path": file_path
            }

    async def summarize_text(self, text: str, method: str = "api", num_sentences: int = 5) -> str:
        """Enhanced text summarization with DeepSeek API integration"""
        if method == "api":
            from src.ai.deepseek_client import DeepSeekClient
            client = DeepSeekClient()
            prompt = f"""Please provide a concise and informative summary of the following text in {num_sentences} sentences:

{text}

Focus on the key points and main ideas while maintaining clarity and coherence."""
            
            response = await client.generate_response(prompt)
            return response.strip()
            
        # Fallback to existing methods if API is not available
        return super().summarize_text(text, method, num_sentences)


class SummarizerFeature:
    def __init__(self):
        self.summarizer = TextSummarizer()
        self.summarization_methods = {
            "extractive": self.summarizer.extractive_summarize,
            "frequency": self.summarizer.frequency_based_summarize,
            "luhn": self.summarizer.luhn_summarize,
            "api": self.summarizer.api_summarize
        }
    
    def process_command(self, command: str) -> str:
        """Process voice commands for text summarization"""
        command = command.lower().strip()
        
        # Summarize text
        if any(keyword in command for keyword in ["summarize", "summarise", "summary of", "sum up"]):
            return self._summarize_from_command(command)
        
        # Compare summarization methods
        elif any(keyword in command for keyword in ["compare summaries", "different summaries", "all methods"]):
            return self._compare_summarization_methods(command)
        
        # Get summary statistics
        elif any(keyword in command for keyword in ["summary stats", "compression ratio", "summary info"]):
            return self._get_summary_statistics(command)
        
        else:
            return ("I can summarize text for you. Try saying:\n"
                   "• 'Summarize [text]' or 'Summary of [text]'\n"
                   "• 'Use extractive method' for different algorithms\n"
                   "• 'Compare summaries' to see different approaches")
    
    def _summarize_from_command(self, command: str) -> str:
        """Extract text and summarize from command"""
        # Remove summarization keywords
        for keyword in ["summarize", "summarise", "summary of", "sum up"]:
            command = command.replace(keyword, "").strip()
        
        # Determine method
        method = "extractive"
        if "extractive" in command:
            method = "extractive"
            command = command.replace("extractive", "").strip()
        elif "frequency" in command:
            method = "frequency"
            command = command.replace("frequency", "").strip()
        elif "luhn" in command:
            method = "luhn"
            command = command.replace("luhn", "").strip()
        elif "api" in command:
            method = "api"
            command = command.replace("api", "").strip()
        
        # Determine number of sentences
        num_sentences = 3
        sentence_match = re.search(r'(\d+)\s*sentences?', command)
        if sentence_match:
            num_sentences = int(sentence_match.group(1))
            command = command.replace(sentence_match.group(0), "").strip()
        
        if not command:
            return "Please provide text to summarize."
        
        # Summarize the text
        if method == "api":
            summary = self.summarizer.api_summarize(command)
        else:
            summary = self.summarizer.extractive_summarize(command, num_sentences)
        
        # Get statistics
        stats = self.summarizer.get_summary_stats(command, summary)
        
        response = f"📝 Summary ({method.title()} method):\n\n"
        response += f"{summary}\n\n"
        response += f"📊 Statistics:\n"
        response += f"• Compression: {stats.get('compression_ratio', 0):.1%}\n"
        response += f"• Sentences: {stats.get('original_sentences', 0)} → {stats.get('summary_sentences', 0)}\n"
        response += f"• Words: {stats.get('original_words', 0)} → {stats.get('summary_words', 0)}\n"
        
        return response
    
    def _compare_summarization_methods(self, command: str) -> str:
        """Compare different summarization methods"""
        # Extract text to summarize
        for keyword in ["compare summaries", "different summaries", "all methods"]:
            command = command.replace(keyword, "").strip()
        
        if not command:
            return "Please provide text to compare summarization methods."
        
        response = "📊 Comparing Summarization Methods:\n\n"
        
        # Test each method
        for method_name, method_func in self.summarization_methods.items():
            try:
                if method_name == "api":
                    summary = method_func(command)
                else:
                    summary = method_func(command, 3)
                
                stats = self.summarizer.get_summary_stats(command, summary)
                
                response += f"🔹 {method_name.title()} Method:\n"
                response += f"   {summary[:200]}...\n"
                response += f"   Compression: {stats.get('compression_ratio', 0):.1%}\n\n"
                
            except Exception as e:
                response += f"🔹 {method_name.title()} Method: Error - {str(e)}\n\n"
        
        return response
    
    def _get_summary_statistics(self, command: str) -> str:
        """Get detailed summary statistics"""
        # Extract text
        for keyword in ["summary stats", "compression ratio", "summary info"]:
            command = command.replace(keyword, "").strip()
        
        if not command:
            return "Please provide text to analyze."
        
        # Create a sample summary
        summary = self.summarizer.extractive_summarize(command, 3)
        stats = self.summarizer.get_summary_stats(command, summary)
        
        response = "📊 Summary Analysis:\n\n"
        response += f"📏 Original Length: {stats.get('original_length', 0):,} characters\n"
        response += f"📏 Summary Length: {stats.get('summary_length', 0):,} characters\n"
        response += f"📈 Compression Ratio: {stats.get('compression_ratio', 0):.1%}\n"
        response += f"📝 Original Sentences: {stats.get('original_sentences', 0)}\n"
        response += f"📝 Summary Sentences: {stats.get('summary_sentences', 0)}\n"
        response += f"📊 Sentence Reduction: {stats.get('sentence_reduction', 0):.1%}\n"
        response += f"📊 Word Reduction: {stats.get('word_reduction', 0):.1%}\n"
        
        return response
    
    def summarize_text(self, text: str, method: str = "extractive", num_sentences: int = 3) -> str:
        """Summarize text with specified method"""
        try:
            if method == "api":
                return self.summarizer.api_summarize(text)
            else:
                return self.summarizer.extractive_summarize(text, num_sentences)
        except Exception as e:
            print(f"Error summarizing text: {e}")
            return text[:500] + "..." if len(text) > 500 else text


# Global instance
summarizer_feature = SummarizerFeature()


def handle_summarizer_command(command: str) -> str:
    """Handle summarizer-related voice commands"""
    return summarizer_feature.process_command(command)


def summarize_text(text: str, method: str = "extractive", num_sentences: int = 3) -> str:
    """Summarize text with specified method"""
    return summarizer_feature.summarize_text(text, method, num_sentences)


if __name__ == "__main__":
    # Test the summarizer feature
    feature = SummarizerFeature()
    
    # Sample text for testing
    sample_text = """
    Artificial intelligence (AI) is a branch of computer science that aims to create intelligent machines that work and react like humans. 
    Some of the activities computers with artificial intelligence are designed for include speech recognition, learning, planning, and problem solving. 
    AI has been used in various applications such as virtual assistants, autonomous vehicles, medical diagnosis, and game playing. 
    Machine learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. 
    Deep learning, a type of machine learning, uses neural networks with multiple layers to analyze various factors of data. 
    The field of AI has seen significant advancements in recent years, leading to breakthroughs in natural language processing, computer vision, and robotics.
    """
    
    # Test commands
    test_commands = [
        f"summarize {sample_text}",
        "compare summaries " + sample_text,
        "summary stats " + sample_text
    ]
    
    for cmd in test_commands:
        print(f"Command: {cmd[:50]}...")
        print(f"Response: {feature.process_command(cmd)}")
        print("-" * 50) 