import os
import yaml
import argparse

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


def get_sidebar_link(header):
    if 'sidebar_link' in header and isinstance(header['sidebar_link'], int):
        url = '/' + header.get('permalink', '')
        link_id = header['sidebar_link']
        return link_id, url
    else:
        return None, None


def get_header_info(header, full_path):
    if 'sidebar' in header:
        if header['sidebar'] == 'none':
            return full_path, None, None, None
        elif header['sidebar'] == 'doc_sidebar':
            link_id, url = get_sidebar_link(header)
            return None, full_path if link_id is None else None, link_id, url
    return None, None, None, None


def process_file(file, root):
    if file.endswith('.md'):
        full_path = os.path.join(root, file)
        header = parse_md_header(full_path)
        if header is not None:
            return get_header_info(header, full_path)
    return None, None, None, None


def parse_md_files(dir_path):
    md_links, untracked_files, nosidebar_files, nolink_files = {}, [], [], []

    for root, dirs, files in os.walk(dir_path):
        for file in files:
            nosidebar_file, nolink_file, link_id, url = process_file(file, root)
            if nosidebar_file is not None:
                nosidebar_files.append(nosidebar_file)
            elif nolink_file is not None:
                nolink_files.append(nolink_file)
            elif link_id is not None:
                if link_id in md_links:
                    print(f'\nDuplicate sidebar_link found: {link_id}, for pages:\n' \
                          f'- {md_links[link_id][1:]}\n- {url[1:]}')
                    return None
                md_links[link_id] = url
            else:
                untracked_files.append(os.path.join(root, file))

    print(f'\nLargest sidebar_link: {max(md_links.keys())}')
    return md_links, untracked_files, nosidebar_files, nolink_files
    

def remove_file_from_dict(dic, key):
    if key in dic:
        del dic[key]
    return dic


def generate_sidebar(tree_path, md_links):
    sidebar = 'entries:\n- product: Documentation\n  version: v0.1\n\n'
#    sidebar = 'entries:\n- product: \n  version: \n\n'

    text = open(tree_path, 'r').read()
    try:
        tree = yaml.safe_load(text)
    except yaml.YAMLError as e:
        print(f'Error parsing YAML header in {tree_path}: {e}')
        return None

    for title in tree:
        sidebar += f'- title: {title}\n  folders:\n\n'
        dir = tree[title]
        if type(dir) != dict and type(dir) != None:
            raise ValueError(f'1-level title "{title}" should have a dictionary value')
        
        for folder in dir:
            sidebar += f'  - title: {folder}\n    output: web\n    folderitems:\n\n'
            dir_items = dir[folder]
            if type(dir_items) != dict and type(dir_items) != None:
                raise ValueError(f'2-level title "{folder}" should have a dictionary value')
            
            dir_items = list(dir_items.items())
            for i in range(len(dir_items)):
                key, value = dir_items[i]

                # this is the situation where 3-level title is a page
                if type(value) == int:
                    if value in md_links:
                        url = md_links[value]
                        sidebar += f'    - title: {key}\n      url: {url}\n'
                        sidebar += f'      output: web\n\n'
                        md_links = remove_file_from_dict(md_links, value)
                    else:
                        raise ValueError(f'Page "{key}" with number {value} either has no .md or {value} is duplicated in the tree')

                # this is the situation where 3-level title is a folder
                else:
                    if type(value) != dict and type(value) != None:
                        raise ValueError(f'4-level title "{key}" should have a dictionary value')
                    
                    if i == 0:
                        raise ValueError(f'4-level subfolder "{key}" should follow a page entry '\
                                         '(this is the only way Jekyll allows for subfolder generation)')
                    
                    key_prev, value_prev = dir_items[i-1]
                    # subfolder follows a page entry
                    if type(value_prev) == int:
                        sidebar += '      subfolders:\n'
                    sidebar += f'      - title: {key}\n        output: web\n        subfolderitems:\n\n'

                    for name, val in value.items():
                        if type(val) != int:
                            raise ValueError(f'5-level title "{key}" should be a page entry')
                        if val in md_links:
                            link = md_links[val]
                            sidebar += f'        - title: {name}\n          url: {link}\n'
                            sidebar += f'          output: web\n\n'
                            md_links = remove_file_from_dict(md_links, val)
                        else:
                            raise ValueError(f'Page "{name}" with number {val} either has no .md or {val}  is duplicated in the tree')
    
    return sidebar, md_links


def print_verbose_info(name, collection, verbose, restrict_details=False):
    if len(collection) > 0 or verbose:
        print(f'\n{name} ({len(collection)}):')
        if verbose or not restrict_details:
            for item in collection:
                print(item)
        else:
            print('(use -v to see list)')


def build_sidebar(dir_path, tree_path, verbose=False):
    parsed_results = parse_md_files(dir_path)
    
    if not parsed_results:
        return None
    
    md_links, untracked_files, nosidebar_files, nolink_files = parsed_results

    try:
        generated_sidebar = generate_sidebar(tree_path, md_links)
        if generated_sidebar is None:
            return None
        sidebar, dangling_links = generated_sidebar
    except ValueError as e:
        print(f'\nError: {e}')
        return None
    
    print_verbose_info("Files intentionally omitted from sidebar", nosidebar_files, verbose, restrict_details=True)
    print_verbose_info("Files missing sidebar_link", nolink_files, verbose)
    print_verbose_info("Files with other header issues", untracked_files, verbose)
    print_verbose_info("Files with sidebar_link not referenced in doc_tree.yml", dangling_links, verbose)
    
    print('\n')

    return sidebar


# ===================================== main driver ==================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    args = parser.parse_args()

    docs_path = 'pages/'
    sidebar_path = '_data/sidebars/doc_sidebar.yml'
    tree_path = '_data/sidebars/doc_tree.yml'
    
    sidebar = build_sidebar(docs_path, tree_path, args.verbose)
    if sidebar:
        with open(sidebar_path, 'w') as f:
            f.write(sidebar)
    else:
        print('\nNo sidebar generated\n')


if __name__ == '__main__':
    main()
