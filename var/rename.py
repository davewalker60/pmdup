import os
import argparse

def find_md_file(directory, filename):
    for root, dirs, files in os.walk(directory):
        if filename in files:
            return os.path.join(root, filename)
    return None


def get_all_md_files(directory):
    md_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    return md_files


def rename_md_file(old_path, new_filename):
    if old_path is None:
        raise Exception("File not found")
        
    directory = os.path.dirname(old_path)
    new_path = os.path.join(directory, new_filename)
    os.rename(old_path, new_path)
    return new_path

        
def update_permalink(file_path, new_filename):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    new_permalink = new_filename.replace('.md', '.html')

    with open(file_path, 'w') as f:
        for line in lines:
            if line.strip().startswith('permalink:'):
                line = 'permalink: ' + new_permalink + '\n'
            f.write(line)

        
def replace_old_filename(directory, old_filename, new_filename):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                content = content.replace(old_filename, new_filename)
                with open(file_path, 'w') as f:
                    f.write(content)


def main():
    parser = argparse.ArgumentParser(description='Rename markdown file and update the references.')
    parser.add_argument('old_filename', type=str, help='Old filename')
    parser.add_argument('new_filename', type=str, help='New filename')

    args = parser.parse_args()
    old_filename = args.old_filename
    new_filename = args.new_filename

    root_folder = 'pages'  # replace with your root directory

    try:
        old_file_path = find_md_file(root_folder, old_filename)
        if not old_file_path:
            print(f"File '{old_filename}' not found in directory '{root_folder}'.")
            return
        new_path = rename_md_file(old_file_path, new_filename)
        update_permalink(new_path, new_filename)
        replace_old_filename(root_folder, old_filename, new_filename)
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
