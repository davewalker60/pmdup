import os
import re
from pathlib import Path

def find_md_files(directory):
    md_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    return md_files


def extract_unique_headers(md_files):
    headers, header_counts, header_files = {}, {}, {}
    pattern = re.compile(r'^(#{1,6})[ \t]+(\S+.*)$', re.MULTILINE)

    for file in md_files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            found_headers = pattern.findall(content)
            found_headers = [h[1].strip() for h in found_headers]  # Get only the text of the header

            # Skip files without headers
            if not found_headers:
                continue

            # Convert headers to their link form
            link_form_headers = [re.sub('-{2,}', '-', re.sub(r'\W', '-', header.lower())) for header in found_headers]

            # Track headers for each file
            headers[os.path.abspath(file)] = link_form_headers

            # Update header_counts dictionary and header_files dictionary
            for header in link_form_headers:
                header_counts[header] = header_counts.get(header, 0) + 1
                if header not in header_files:
                    header_files[header] = os.path.abspath(file)
    
    unique_headers = {header: header_files[header] for header, count in header_counts.items() if count == 1}
    return headers, unique_headers


def fix_links(md_files, headers, unique_headers):
    fixed_links, unfixable_links = {}, []
    link_pattern = re.compile(r'\[([^\]]*)\]\(((?!https?:\/\/)[^)]*\.md[^)]*(?:#.*)?|#[^)]*)\)')
    for file in md_files:
        current_dir = os.path.dirname(file)
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = link_pattern.findall(content)
            
            for match in matches:
                original_text = match[0]
                original_link = match[1]
                file_part, sep, header_part = original_link.partition('#')
                header_part = header_part or ''

                file_part_path = os.path.join(current_dir, file_part) if file_part else file
                file_part_path_abs = os.path.abspath(file_part_path)
                if file_part and not os.path.isfile(file_part_path_abs):
                    file_part = os.path.basename(file_part)
                    for md_file in md_files:
                        if os.path.basename(md_file) == file_part:
                            file_part = os.path.relpath(md_file, current_dir)
                            file_part_path = os.path.join(current_dir, file_part)
                            file_part_path_abs = os.path.abspath(file_part_path)
                            break
                    # no markdown file was found with a name matching file_part
                    else:
                        unfixable_links.append((file, original_text, original_link))
                        continue

                if header_part and header_part.lower() not in map(str.lower, headers.get(file_part_path_abs, [])):
                    if header_part.lower() in unique_headers:
                        file_part = os.path.relpath(unique_headers[header_part.lower()], current_dir)
                        file_part_path = os.path.join(current_dir, file_part)
                        file_part_path_abs = os.path.abspath(file_part_path)
                    else:
                        unfixable_links.append((file, original_text, original_link))
                        continue

                fixed_link = file_part + ('#' + header_part if header_part else '')
                if fixed_link != original_link:
                    if file not in fixed_links:
                        fixed_links[file] = []
                    fixed_links[file].append((original_link, fixed_link.replace("\\", "/")))

    return fixed_links, unfixable_links

                    
def apply_fixes(fixed_links):
    for file, links in fixed_links.items():
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()

        for original_link, fixed_link in links:
            content = content.replace(original_link, fixed_link)

        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)


def generate_broken_links_table(top_path, table_path, unfixable_links):
    with open(top_path, 'r', encoding='utf-8') as f:
        table_header = f.read()

    mlt = open(table_path, 'w', encoding='utf-8')
    mlt.write(table_header)

    for file, text, link in unfixable_links:
        parts = Path(file).parts
        mlt.write(f'| {"/".join(parts[2:])} | {text} | {link} |\n')

    mlt.close()


# ===================================== main driver ==================================

def main():
    # Because table_top_path and table_path will end up both containing the same permalink header,
    # the filename for table_top_path MUST be alphabetically before table_path,
    # so Jekyll the .html for table_top_path first then overwrites the .html with the one we want.
    # Note: Jekyll searched all files, so just changing the .md extension doesn't work. 
    table_top_path = 'var/broken-links-header.md'
    table_path = 'pages/broken-links-table.md'
    docs_path = 'pages/'

    # Gather markdown files
    md_files = find_md_files(docs_path)

    # Gather headers
    headers, unique_headers = extract_unique_headers(md_files)

    # Gather links and fix them
    fixed_links, unfixable_links = fix_links(md_files, headers, unique_headers)

    # Apply fixes to the files
    apply_fixes(fixed_links)

    # Generate broken-links.md
    generate_broken_links_table(table_top_path, table_path, unfixable_links)

    # Print out the results
    print('\nFixed links:')
    for file, links in fixed_links.items():
        for original_link, fixed_link in links:
            print(f'{file}: {original_link} -> {fixed_link}')

    print('\n\nUnfixable links:')
    for file, text, link in unfixable_links:
        print(f'{file}: [{text}]({link})')


if __name__ == '__main__':
    main()
