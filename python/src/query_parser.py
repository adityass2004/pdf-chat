import re

def parse_image_query(query):
    """
    Parse natural language image queries.
    Returns: (action, page_num, topic)
    """
    query_lower = query.lower()
    
    # Extract page number
    page_match = re.search(r'page\s+(\d+)', query_lower)
    page_num = int(page_match.group(1)) if page_match else None
    
    # Detect action type
    if any(word in query_lower for word in ["show", "display", "see", "view", "list"]):
        if page_num:
            return ("show_page_images", page_num, None)
        elif any(word in query_lower for word in ["all", "every", "list"]):
            return ("show_all_images", None, None)
        else:
            # Check for topic
            topic_indicators = ["about", "related to", "of", "with", "regarding"]
            for indicator in topic_indicators:
                if indicator in query_lower:
                    topic = query_lower.split(indicator, 1)[1].strip()
                    return ("search_topic", None, topic)
    
    if any(word in query_lower for word in ["open", "analyze", "describe"]):
        # Try to find image number
        num_match = re.search(r'(?:image|img|picture|photo)\s+(\d+)', query_lower)
        if num_match:
            img_num = int(num_match.group(1))
            return ("open_and_analyze", img_num, None)
        elif page_num:
            return ("analyze_page", page_num, None)
    
    return (None, None, None)