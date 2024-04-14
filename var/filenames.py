import os
import yaml

def parse_md_header(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Check if the file starts with '---'
    if lines and lines[0].strip() != '---':
        return None

    header = ""
    lines.pop(0)
    for line in lines:
        if line.strip() == '---':
            break
        header += line

    try:
        data = yaml.safe_load(header)
        return data
    except yaml.YAMLError as e:
        print(f'Error parsing YAML header in {file_path}: {e}')
        return None


def search_files(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                header = parse_md_header(full_path)

                if header is None:
                    print(f'{full_path} -> no valid YAML header')
                    continue

                if os.path.splitext(file)[0] != os.path.splitext(header['permalink'])[0]:
                    print(f'{full_path} -> permalink does not match filename')


# ===================================== main driver ==================================

def main():
    docs_path = 'pages/'

    print('\n\nFile header issues:')
    search_files(docs_path)


if __name__ == '__main__':
    main()
