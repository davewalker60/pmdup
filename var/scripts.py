import os
import argparse

parser = argparse.ArgumentParser(description="Run scripts with optional verbosity")

# Add the verbose argument
parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose mode")

# Parse the command-line arguments
args = parser.parse_args()

# Check if the verbose flag was provided
verbose_flag = '-v' if args.verbose else ''

print('\n\n######### Starting scripts.py ##############', flush=True)

os.system('python ./var/filenames.py')
os.system('python ./var/links.py')
os.system(f'python ./var/sidebar.py {verbose_flag}')
