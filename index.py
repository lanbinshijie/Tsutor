from flask import Flask, render_template, send_from_directory
from core import *

app = Flask(__name__, static_folder="assets")

def generate_html_list(data):
    html = "<ul>\n"
    count = len(data)
    for item in data:
        title = item["filename"]
        catagory = item["category"]
        hasher = item["hash"]
        link = "/p/" + str(hasher)
        html += f"<li><a href='{link}'>{catagory} | {title}</a></li>\n"
        count -= 1
    html += "</ul>"
    return html

introDuction = """
<p>期中考试临近，编写了一些复习资料，但苦于不喜欢收纳整理文件，所以想将它们都放到网站上，故做了这个CMS系统，目前开发中，仅支持阅读。如果你觉得这个项目还可以，欢迎去Github点一个Star～</p>
"""

@app.route("/")
def index():
    # 调用 getNewestMD 函数获取 Markdown 内容
    # print(list_and_cache_passages())
    markdown_list = generate_html_list(list_and_cache_passages())
    # print(markdown_list)
    
    # 渲染模板并传递 HTML 内容
    return render_template("index.html", content=introDuction+markdown_list, namer="主页")

@app.route("/save")
def save():
    list_and_cache_passages(True)
    html = "<h1>保存成功！</h1>"
    return render_template("index.html", content=html)

@app.route('/p/<string:idx>')
def readPassage(idx):
    # 调用 getNewestMD 函数获取 Markdown 内容
    name, markdown_text = getById(idx)
    html_text = render_html(markdown_text, idx)

    # 渲染模板并传递 HTML 内容
    return render_template("p.html", content=html_text, namer=name)

@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    app.run(debug=True)
