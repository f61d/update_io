from yaml import load, dump, dump_all
try:
    from yaml import Cloader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import os
import sys
import re

chall_path = ""
io_path = ""

# direct: "pwn/VMEscape/BabyQemu"
# rel: "![](./index_files/2d7a730f-7bb6-424f-ab64-9c1836826315.jpg)"
def RelPathPre2FullPathPre(direct):
    global chall_path, io_path
    prefix = r"https://raw.githubusercontent.com/f61d/challenges/master/"
    return prefix + direct

# direct: "pwn/VMEscape/BabyQemu"
def UpdateREADME(direct):
    #print direct
    global chall_path, io_path
    if direct.endswith("/"):
        direct = direct[: -1]    
    README_PATH = os.path.join(chall_path, direct)
    README_PATH = os.path.join(README_PATH, "README.md")
    if not os.path.exists(README_PATH):
        raise Exception("README.md for {README_PATH} not found".format(README_PATH = README_PATH))
    rdme = open(README_PATH, "r")
    content_old = rdme.read()
    rdme.close()
    content_new = content_old.replace("![](./", "![]({full_path}/".format(full_path = RelPathPre2FullPathPre(direct)))
    return content_new 

def yml_add_new_item(origin, pathes, direct):
    #print pathes
    if len(pathes) == 1:
        new_node = {}
        new_node[pathes[0]] = "{file_name}.md".format(file_name = direct)
        return new_node
    
    if type(origin) == dict:
        if pathes[0] in origin.keys():
            for i in range(0, len(origin[pathes[0]])):
                val = yml_add_new_item(origin[pathes[0]][i], pathes[1:], direct)
                if val == False:
                    continue
                else:
                    origin[pathes[0]][i] = val
                    return origin
            new_node = {}
            new_node[pathes[1]] = []
            origin[pathes[0]].append(yml_add_new_item(new_node, pathes[1:]), direct)
            return origin
        else:
            return False
    
    if type(origin) == list:
        for i in range(0, len(origin)):
            val = yml_add_new_item(origin[i], pathes, direct)
            if val == False:
                continue
            else:
                origin[i] = val
                return origin
        new_node = {}
        new_node[pathes[0]] = []
        origin.append(new_node)
        return origin

def UpdateMKDOCS(direct):
    mkdocs_file = open(os.path.join(io_path, "mkdocs.yml"), "r")
    mkdocs_content_old = mkdocs_file.read()
    mkdocs_file.close()
    mkdocs_content_old_before = mkdocs_content_old[ : mkdocs_content_old.find("nav:")]
    mkdocs_content_old_after = mkdocs_content_old[mkdocs_content_old.find("nav:") : ]
    mkdocs_content_old_yml = load(mkdocs_content_old_after, Loader=Loader)

    path_init = mkdocs_content_old_yml.values()[0]
    key_name = mkdocs_content_old_yml.keys()[0]
    mkdocs_content_old_yml[key_name] = yml_add_new_item(path_init, direct.split("/"), direct)
    mkdocs_content_new = mkdocs_content_old_before + dump(mkdocs_content_old_yml)
    mkdocs_file = open(os.path.join(io_path, "mkdocs.yml"), "w")
    mkdocs_file.write(mkdocs_content_new)
    mkdocs_file.close()

# direct: "pwn/VMEscape/BabyQemu"
def Copy2IO(direct):
    global chall_path, io_path
    if direct.endswith("/"):
        direct = direct[: -1]
    docs_path = os.path.join(io_path, "docs")
    if not os.path.exists(os.path.join(docs_path, os.path.dirname(direct))):
        os.makedirs(os.path.join(docs_path, os.path.dirname(direct)))
    README_PATH = os.path.join(chall_path, direct)
    README_PATH = os.path.join(README_PATH, "README.md")
    if not os.path.exists(README_PATH):
        raise Exception("README.md for {README_PATH} not found".format(README_PATH = README_PATH))
    doc_file_name = os.path.join(docs_path, os.path.dirname(direct))
    doc_file_name = os.path.join(doc_file_name, direct.split("/")[-1])
    print doc_file_name + ".md"
    new_doc = open(doc_file_name + ".md", "w")
    new_doc.write(UpdateREADME(direct))
    new_doc.close()
    UpdateMKDOCS(direct)

def Usage():
    print '''
    python2 update_io.py path_to_challenges path_to_f61d.github.io
    '''

if __name__ == "__main__":
    if len(sys.argv) != 3:
        Usage()
    chall_path = sys.argv[1]
    while chall_path.endswith("/") or chall_path.endswith("\\"):
        chall_path = chall_path[:-1].replace("\\", "/")
    io_path = sys.argv[2]
    while io_path.endswith("/") or io_path.endswith("\\"):
        io_path = io_path[:-1].replace("\\", "/")
    for root,dirs,files in os.walk(chall_path):
        for file in files:
            if ".git" in root:
                continue
            if root == chall_path:
                continue
            if file == "README.md":
                direct = root.replace("\\", "/")
                direct = direct.replace(chall_path, "")
                while direct.startswith("./"):
                    direct = direct[2:]
                while direct.startswith("/"):
                    direct = direct[1:]
                while direct.endswith("/"):
                    direct = direct[:-1]
                Copy2IO(direct)
