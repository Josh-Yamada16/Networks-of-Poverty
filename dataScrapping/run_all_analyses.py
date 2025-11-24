"""
Batch script to run all analysis scripts on all cached datasets.

This will run:
1. reddit_network_full_analysis.py
2. analyze_relationship_strength.py
3. graph_filtering_methods.py

On each cached subreddit dataset.
"""

import os
import sys
import subprocess
from datetime import datetime

# List of subreddits with cached data
SUBREDDITS = [
    'poverty',
    'povertyfinance',
    'homeless',
    'frugal',
    'assistance'
]

# Analysis scripts to run
SCRIPTS = [
    'reddit_network_full_analysis.py',
    'analyze_relationship_strength.py',
    'graph_filtering_methods.py'
]

def run_analysis(script_name, subreddit):
    """
    Run an analysis script for a specific subreddit.
    
    Args:
        script_name: Name of the script to run
        subreddit: Subreddit name to analyze
    
    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*80)
    print(f"Running: {script_name} on r/{subreddit}")
    print("="*80)
    
    # Modify the script temporarily to use the specified subreddit
    # We'll do this by setting environment variables that the scripts can read
    env = os.environ.copy()
    env['ANALYSIS_SUBREDDIT'] = subreddit
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            env=env,
            capture_output=False,  # Show output in real-time
            text=True,
            check=True
        )
        print(f"\n✓ SUCCESS: {script_name} completed for r/{subreddit}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ ERROR: {script_name} failed for r/{subreddit}")
        print(f"Error code: {e.returncode}")
        return False
    except Exception as e:
        print(f"\n✗ EXCEPTION: {script_name} failed for r/{subreddit}")
        print(f"Error: {e}")
        return False

def main():
    """Run all analyses on all cached datasets."""
    print("\n" + "="*80)
    print("BATCH ANALYSIS: Running all scripts on all cached datasets")
    print("="*80)
    print(f"\nSubreddits: {', '.join(SUBREDDITS)}")
    print(f"Scripts: {', '.join(SCRIPTS)}")
    print(f"\nTotal analyses to run: {len(SUBREDDITS) * len(SCRIPTS)}")
    print("\nStarted at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Track results
    results = {subreddit: {} for subreddit in SUBREDDITS}
    total_success = 0
    total_failed = 0
    
    # Run each script on each subreddit
    for subreddit in SUBREDDITS:
        print("\n" + "━"*80)
        print(f"ANALYZING: r/{subreddit}")
        print("━"*80)
        
        for script in SCRIPTS:
            success = run_analysis(script, subreddit)
            results[subreddit][script] = success
            
            if success:
                total_success += 1
            else:
                total_failed += 1
    
    # Print summary
    print("\n" + "="*80)
    print("BATCH ANALYSIS COMPLETE")
    print("="*80)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nTotal: {total_success} successful, {total_failed} failed")
    
    print("\n" + "-"*80)
    print("DETAILED RESULTS:")
    print("-"*80)
    
    for subreddit in SUBREDDITS:
        print(f"\nr/{subreddit}:")
        for script, success in results[subreddit].items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            print(f"  {status}: {script}")
    
    print("\n" + "="*80)
    print("\nResults are organized in:")
    print("  - results/{subreddit}/full_analysis_{timestamp}/")
    print("  - results/{subreddit}/relationship_strength_{timestamp}/")
    print("  - results/graph_filtering_{timestamp}/")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
