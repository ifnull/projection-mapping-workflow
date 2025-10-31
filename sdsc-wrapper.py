#!/usr/bin/env python3
"""
Stable Diffusion API CLI Tool
Simplifies making structure control requests to Stability AI API using profile-based configs.
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
import requests
import yaml


def load_profile(profile_name):
    """Load profile configuration from YAML file."""
    profile_path = Path(f"./profiles/{profile_name}.yml")
    
    if not profile_path.exists():
        raise FileNotFoundError(f"Profile not found: {profile_path}")
    
    with open(profile_path, 'r') as f:
        return yaml.safe_load(f)


def create_output_directory(profile_name):
    """Create output directory for the profile if it doesn't exist."""
    output_dir = Path(f"./output/{profile_name}")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def generate_output_filename(profile_name):
    """Generate output filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{profile_name}-{timestamp}.jpg"


def make_api_request(secret_key, input_image, profile_config, output_path):
    """Make the API request to Stability AI."""
    url = "https://api.stability.ai/v2beta/stable-image/control/structure"
    
    headers = {
        "Accept": "image/*",
        "Authorization": f"Bearer {secret_key}",
        "mime-version": "1.0",
        "accept-language": "en-US,*",
        "user-agent": "Mozilla/5.0",
        "pragma": "no-cache",
        "cache-control": "no-cache"
    }
    
    # Prepare form data
    with open(input_image, 'rb') as img_file:
        files = {
            'image': img_file
        }
        
        data = {
            'prompt': profile_config['prompt'],
            'negative_prompt': profile_config['negative_prompt'],
            'control_strength': str(profile_config['control_strength']),
            'output_format': profile_config.get('output_format', 'jpeg'),
            'style_preset': profile_config['style_preset']
        }
        
        print(f"Making API request...")
        print(f"  Prompt: {profile_config['prompt']}")
        print(f"  Style: {profile_config['style_preset']}")
        print(f"  Control Strength: {profile_config['control_strength']}")
        
        response = requests.post(url, headers=headers, files=files, data=data)
    
    # Check response
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"✓ Success! Image saved to: {output_path}")
    else:
        raise Exception(f"API request failed with status {response.status_code}: {response.text}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Stability AI's Structure Control API with profile configs"
    )
    parser.add_argument(
        '--profile',
        required=True,
        help='Profile name (will load ./profiles/{profile}.yml)'
    )
    parser.add_argument(
        '--input-image',
        help='Path to input image (can also use INPUT_IMAGE env var)'
    )
    
    args = parser.parse_args()
    
    # Get STABILITY_SECRET_KEY from environment
    secret_key = os.environ.get('STABILITY_SECRET_KEY')
    if not secret_key:
        print("Error: STABILITY_SECRET_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    # Get input image from CLI arg or environment variable
    input_image = args.input_image or os.environ.get('INPUT_IMAGE')
    if not input_image:
        print("Error: Input image not provided. Use --input-image or set INPUT_IMAGE env var", file=sys.stderr)
        sys.exit(1)
    
    # Validate input image exists
    if not Path(input_image).exists():
        print(f"Error: Input image not found: {input_image}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Load profile configuration
        print(f"Loading profile: {args.profile}")
        profile_config = load_profile(args.profile)
        
        # Create output directory
        output_dir = create_output_directory(args.profile)
        
        # Generate output filename
        output_filename = generate_output_filename(args.profile)
        output_path = output_dir / output_filename
        
        # Make API request
        make_api_request(secret_key, input_image, profile_config, output_path)
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
