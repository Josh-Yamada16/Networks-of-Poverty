# Reddit Scraping Configuration File
# Modify these parameters to customize your Reddit data collection

# =============================================================================
# SUBREDDIT SETTINGS
# =============================================================================
SUBREDDIT_NAME = "poverty"  # Change to any subreddit (without r/)
# Examples: "poverty", "personalfinance", "assistance", "povertyfinance", "homeless"

# =============================================================================
# POST COLLECTION SETTINGS
# =============================================================================
NUM_POSTS = 10  # Number of posts to scrape

# Sorting method - choose one:
# 'top'           - Highest scored posts (most upvotes)
# 'comments'      - Most commented posts (most discussion)
# 'interaction'   - Highest score + comments combined
# 'hot'           - Currently trending posts
# 'controversial' - Most controversial/debated posts
SORT_BY = "comments"

# Time filter for 'top' and 'controversial' sorting:
# 'hour', 'day', 'week', 'month', 'year', 'all'
TIME_FILTER = "all"

# =============================================================================
# OUTPUT SETTINGS
# =============================================================================
VERBOSE = True  # Set to True to see posts as they're being scraped
PRINT_RESULTS = True  # Set to True to print formatted results

# =============================================================================
# DATA EXPORT SETTINGS
# =============================================================================
SAVE_TO_FILE = False  # Set to True to save results to a file
OUTPUT_FORMAT = "json"  # 'json', 'csv', or 'txt'
OUTPUT_FILENAME = "reddit_posts"  # Will add appropriate extension

# =============================================================================
# ADVANCED SETTINGS
# =============================================================================
# For 'comments' and 'interaction' sorting, we initially fetch more posts
# to ensure we get the most interactive ones after sorting
OVERSAMPLE_MULTIPLIER = 3  # Fetch NUM_POSTS * this number, then sort and take top NUM_POSTS

# Include additional post data
INCLUDE_AUTHOR = True  # Include post author information
INCLUDE_CREATED_TIME = True  # Include when post was created
INCLUDE_FLAIR = True  # Include post flair/tags
INCLUDE_SELFTEXT = False  # Include post body text (can be very long)

# =============================================================================
# MULTIPLE SUBREDDIT SETTINGS
# =============================================================================
# Set to True to scrape from multiple subreddits
MULTI_SUBREDDIT = False
SUBREDDIT_LIST = [
    "poverty",
    "povertyfinance", 
    "assistance",
    "homeless",
    "frugal"
]

# =============================================================================
# FILTERING SETTINGS
# =============================================================================
# Minimum thresholds for posts to be included
MIN_SCORE = 0  # Minimum upvotes
MIN_COMMENTS = 0  # Minimum number of comments
MIN_INTERACTION_SCORE = 0  # Minimum score + comments

# Maximum values (set to None for no limit)
MAX_SCORE = None  # Maximum upvotes
MAX_COMMENTS = None  # Maximum number of comments

# =============================================================================
# REDDIT API SETTINGS (Advanced users only)
# =============================================================================
# Reddit API credentials (keep these secure)
CLIENT_ID = 'qThRoFaCe_iXAwY7CDOoLg'
CLIENT_SECRET = 'ch-zv9PCgeXqCMcfQ9CKLqvbyxUmuA'
USER_AGENT = 'poverty_research_script'

# Rate limiting
REQUEST_DELAY = 0  # Delay between requests in seconds (0 = no delay)