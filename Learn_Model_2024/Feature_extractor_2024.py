# Feature_extractor_2024.py
# Wrapper to use the existing ChangedURLFeatureExtractor

import sys
import os

# Add parent directory to path to import the main feature extractor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the existing feature extractor
from Changed_Solution.Changed_feature_extractor import ChangedURLFeatureExtractor

# Create an alias for clarity
URLFeatureExtractor2024 = ChangedURLFeatureExtractor

