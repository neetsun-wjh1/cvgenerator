def safe_log_text(text, max_length=500):
    """
    Safely prepare text for logging by handling Unicode and length
    
    Args:
        text: Input text that may contain Unicode characters
        max_length: Maximum length to truncate to
    
    Returns:
        str: Safe text for logging
    """
    if not text:
        return "[Empty content]"
    
    try:
        # Convert to string if not already
        text_str = str(text)
        
        # Truncate if too long
        if len(text_str) > max_length:
            text_str = text_str[:max_length] + "..."
        
        # Replace problematic Unicode characters
        safe_text = text_str.encode('ascii', 'replace').decode('ascii')
        
        # Alternative: Keep Unicode but escape problematic chars
        # safe_text = text_str.encode('unicode_escape').decode('ascii')
        
        return safe_text
        
    except Exception as e:
        return f"[Text encoding error: {str(e)}]"

def safe_logger_setup():
    """
    Setup logger with UTF-8 support and error handling
    """
    # Configure logging with UTF-8 support
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('assistant.log', encoding='utf-8')
        ],
        force=True  # Override existing configuration
    )
