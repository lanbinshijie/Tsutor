import os
import hashlib
import shutil
import json
import re


from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.footnote import footnote_plugin

md = (
    MarkdownIt('commonmark' ,{'breaks':True,'html':True})
    .use(front_matter_plugin)
    .use(footnote_plugin)
    .enable('table')
)


# Helper Functions
def create_folders():
    if not os.path.exists("cache"):
        os.mkdir("cache")
    if not os.path.exists("assets"):
        os.mkdir("assets")

def create_assets_folder(md5):
    base_dir = "assets"
    path = os.path.join(base_dir, md5)
    if not os.path.exists(path):
        os.mkdir(path)

def compute_md5(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()
        return hashlib.md5(content).hexdigest()[:10]

def extract_filename_category(filename):
    file_name, category = filename.rsplit("_", 1)[0], filename.rsplit("_", 1)[1].rsplit(".", 1)[0]
    return file_name, category

def save_to_json(data, filename="lists.json"):
    with open(filename, "w") as file:
        json.dump(data, file)

def load_from_json(filename="lists.json"):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file)
    return []

# Main Functions
def list_and_cache_passages(rebuild=False):
    if not rebuild:
        return load_from_json()
    
    create_folders()
    base_dir = "passages"
    files = [f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f)) and f.endswith(".md")]
    extracted_data = []

    for f in files:
        file_name, category = extract_filename_category(f)
        file_hash = compute_md5(os.path.join(base_dir, f))
        create_assets_folder(file_hash)
        
        # Copy the file to cache with the hash as the filename
        shutil.copy(os.path.join(base_dir, f), os.path.join("cache", f"{file_hash}.md"))
        extracted_data.append({"filename": file_name, "category": category, "hash": file_hash})
    
    save_to_json(extracted_data)
    return extracted_data

def get_file_path_by_hash(file_hash):
    return os.path.join("cache", f"{file_hash}.md")

def read_file_content(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        title = file.readline().strip()  # Assuming first line is the title
        content = file.read().strip()  # Rest of the file is the content
    return title[1:], content

def getByIndex(index):
    data = list_and_cache_passages()
    if int(index) < len(data):
        file_hash = data[int(index)]["hash"]
        file_path = get_file_path_by_hash(file_hash)
        return read_file_content(file_path)
    else:
        return None, None

def getById(file_hash):
    file_path = get_file_path_by_hash(file_hash)
    if os.path.exists(file_path):
        return read_file_content(file_path)
    else:
        return None, None

def getByName(filename):
    data = list_and_cache_passages()
    matched_files = [item for item in data if item["filename"] == filename]
    if matched_files:
        file_hash = matched_files[0]["hash"]
        file_path = get_file_path_by_hash(file_hash)
        return read_file_content(file_path)
    else:
        return None, None

def deal_line(line, ln):
    a = line[ln:].replace(" ", "-").replace("&","AND").lower()
    return a if a[0] == "-" else "-"+a

def generate_toc(content):
    print(content)
    lines = content.split('\n')
    toc_list = []
    
    for line in lines:
        if line.startswith('# '):
            toc_list.append(f'<li><a href="#{deal_line(line,2)}">{line[2:]}</a></li>')
        elif line.startswith('## '):
            toc_list.append(f'<ul><li><a href="#{deal_line(line,3)}">{line[3:]}</a></li></ul>')
        elif line.startswith('### '):
            toc_list.append(f'<ul><ul><li><a href="#{deal_line(line,4)}">{line[4:]}</a></li></ul></ul>')
        # 你可以继续添加对更多级别标题的支持
    
    toc = '<ul>' + '\n'.join(toc_list) + '</ul>'
    return toc


def render_html(content, md5=""):
    html_text = md.render(content)
    html_text = render_content_using_bootstrap(html_text, md5=md5)
    return html_text

def add_ids_to_headings(content):
    def replacer(match):
        tag = match.group(1)
        attributes = match.group(2) if match.group(2) else ''
        title = match.group(3)
        return f'<{tag} id="{deal_line(title,0)}" {attributes}>{title}</{tag}>'.replace("amp;",'')

    pattern = re.compile(r'<(h[1-3])([^>]*)>(.+?)<\/\1>')
    return pattern.sub(replacer, content)

def render_content_using_bootstrap(content, md5=""):
    title, origin = getById(md5)
    rendered = content.replace("<h2>", '<h2 class="mb-5">')
    rendered = rendered.replace("<h3>", '<h3 class="mb-3">')
    rendered = rendered.replace("<img", '<img style="max-width: 100%" ')
    rendered = rendered.replace("./assets", f"/assets/{md5}")
    rendered = rendered.replace("[TOC]", generate_toc("# "+title+"\n"+origin))

    rendered = add_ids_to_headings(rendered)
    print(content)
    return rendered

