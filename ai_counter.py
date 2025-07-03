import tiktoken
from typing import Dict, Any
#Logging
import customLogging

logger = customLogging.safe_logger_setup()

# Global counters (you might want to move these to a class or config)
class UsageTracker:
    def __init__(self):
        self.total_requests = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_tokens = 0
    
    def increment_request(self):
        self.total_requests += 1
    
    def add_tokens(self, input_tokens: int, output_tokens: int):
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_tokens += (input_tokens + output_tokens)
    
    def get_stats(self) -> Dict[str, int]:
        return {
            "total_requests": self.total_requests,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_tokens
        }

# Initialize global tracker
usage_tracker = UsageTracker()

def count_tokens(text: str, model_name: str = "gpt4omini") -> int:
    """
    Count tokens in text using tiktoken
    
    Args:
        text: Text to count tokens for
        model_name: Model name for appropriate encoding
    Returns:
        int: Number of tokens
    """
    try:
        # Map model names to encodings
        # Map model names to encodings
        model_encodings = {
            "gpt-4": "cl100k_base",
            "gpt-4o": "cl100k_base",
            "gpt4omini": "cl100k_base",  # Alternative naming
            "gpt-3.5-turbo": "cl100k_base",
            "claude": "cl100k_base",  # Approximation for Claude
            "text-davinci-003": "p50k_base",
        }

        encoding_name = model_encodings.get(model_name, "cl100k_base")
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(text))
    except Exception as e:
        logger.warning(f"Error counting tokens: {e}")
        # Fallback approximation: ~4 chars per token
        return len(text) // 4

def count_messages_tokens(messages, model_name: str = "gpt4omini") -> int:
    """
    Count total tokens in a list of messages
    
    Args:
        messages: List of message objects
        model_name: Model name for appropriate encoding
    Returns:
        int: Total number of tokens
    """
    total_tokens = 0
    for message in messages:
        # Handle different message formats
        if hasattr(message, 'content'):
            content = message.content
        elif isinstance(message, dict):
            content = message.get('content', '')
        else:
            content = str(message)
        
        total_tokens += count_tokens(content, model_name)
        
        # Add tokens for message metadata (role, etc.)
        total_tokens += 4  # Approximate overhead per message
    
    return total_tokens



# Helper function to get current usage statistics
def get_usage_statistics() -> Dict[str, int]:
    """Get current usage statistics"""
    return usage_tracker.get_stats()

# Helper function to reset usage statistics
def reset_usage_statistics():
    """Reset usage statistics"""
    global usage_tracker
    usage_tracker = UsageTracker()
    logger.info("Usage statistics reset")

# Helper function to log usage summary
def log_usage_summary():
    """Log a summary of current usage"""
    stats = usage_tracker.get_stats()
    logger.info("=" * 50)
    logger.info("USAGE SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Total API Requests: {stats['total_requests']}")
    logger.info(f"Total Input Tokens: {stats['total_input_tokens']:,}")
    logger.info(f"Total Output Tokens: {stats['total_output_tokens']:,}")
    logger.info(f"Total Tokens: {stats['total_tokens']:,}")
    logger.info(f"Average Input Tokens per Request: {stats['total_input_tokens'] // max(1, stats['total_requests'])}")
    logger.info(f"Average Output Tokens per Request: {stats['total_output_tokens'] // max(1, stats['total_requests'])}")
    logger.info("=" * 50)