from yaml import load, dump, dump_all
try:
    from yaml import Cloader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import os
import sys
import re
import datetime

chall_path = ""
io_path = ""

web_recent = ""
pwn_recent = ""
crypto_recent = ""
reverse_recent = ""
misc_recent = ""

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
    if type(origin) == dict:
        if len(pathes) == 1 and pathes[0] in origin.keys(): #update {"CHALL":"/type0/type1/CHALL.md"}
            origin[pathes[0]] = "{file_name}.md".format(file_name = direct)
            return origin
        if pathes[0] in origin.keys():
            origin[pathes[0]] = yml_add_new_item(origin[pathes[0]], pathes[1:], direct)
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
        if len(pathes) >= 2:
            new_node = {}
            new_node[pathes[0]] = []
            new_node[pathes[0]] = yml_add_new_item(new_node[pathes[0]], pathes[1:], direct)
            origin.append(new_node)
            return origin
        elif len(pathes) == 1:
            new_node = {}
            new_node[pathes[0]] = ""
            new_node[pathes[0]] = "{file_name}.md".format(file_name = direct)
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
    print dump(mkdocs_content_old_yml)
    mkdocs_file = open(os.path.join(io_path, "mkdocs.yml"), "w")
    mkdocs_file.write(mkdocs_content_new)
    mkdocs_file.close()

index_module = '''### web

https://f61d.github.io/web/
  
{web_recent}

### pwn

https://f61d.github.io/pwn/
  
{pwn_recent}

### crypto

https://f61d.github.io/crypto/
  
{crypto_recent}

### reverse

https://f61d.github.io/reverse/
  
{reverse_recent}

### misc

https://f61d.github.io/misc/
  
{misc_recent}
'''


def UpdateHomePage(direct):
    global chall_path, io_path
    global web_recent
    global pwn_recent
    global crypto_recent
    global reverse_recent
    global misc_recent
    origin_cwd = os.getcwd()
    #goto chall_path work dir
    os.chdir(chall_path)
    README_PATH = os.path.join("./", direct)
    README_PATH = os.path.join(README_PATH, "README.md")
    result = os.popen('git log --date=short \"{readme_path}\"'.format(readme_path = README_PATH))
    #print 'git log --date=short {readme_path}'.format(readme_path = README_PATH)
    res = result.read()
    result.close()
    AUTHOR = ""
    DATE = ""
    #print res
    for line in res.splitlines(): 
        if "Author:".lower() in line.lower() and AUTHOR == "":
            #print line
            AUTHOR = line[line.find(":") + 1 : ].strip()
            AUTHOR_mail_beg = AUTHOR.find("<")
            AUTHOR_mail_end = AUTHOR.find(">")
            AUTHOR = AUTHOR[ : AUTHOR_mail_beg] + AUTHOR[AUTHOR_mail_end + 1 : ]
            AUTHOR = AUTHOR.strip()
            #print AUTHOR
        if "Date:".lower() in line.lower() and DATE == "":
            DATE = line[line.find(":") + 1 : ].strip()
            timeArray = DATE.split("-")
            day_commit = datetime.datetime(int(timeArray[0]), int(timeArray[1]), int(timeArray[2]))
            day_now = datetime.datetime.now()
            day_dec = (day_now - day_commit).days
            if day_dec > 60:
                os.chdir(origin_cwd)
                return
            
    if direct.replace("\\", "/").split("/")[0] == "web":
        web_recent += "> ```{chall_name}``` by **```{AUTHOR}```** @ {DATE} \n\n".format(chall_name = direct.replace("\\", "/").split("/")[-1], AUTHOR = AUTHOR, DATE = DATE)
    elif direct.replace("\\", "/").split("/")[0] == "pwn":
        pwn_recent += "> ```{chall_name}``` by **```{AUTHOR}```** @ {DATE} \n\n".format(chall_name = direct.replace("\\", "/").split("/")[-1], AUTHOR = AUTHOR, DATE = DATE)
    elif direct.replace("\\", "/").split("/")[0] == "crypto":
        crypto_recent += "> ```{chall_name}``` by **```{AUTHOR}```** @ {DATE} \n\n".format(chall_name = direct.replace("\\", "/").split("/")[-1], AUTHOR = AUTHOR, DATE = DATE)
    elif direct.replace("\\", "/").split("/")[0] == "reverse":
        reverse_recent += "> ```{chall_name}``` by **```{AUTHOR}```** @ {DATE} \n\n".format(chall_name = direct.replace("\\", "/").split("/")[-1], AUTHOR = AUTHOR, DATE = DATE)
    elif direct.replace("\\", "/").split("/")[0] == "misc":
        misc_recent += "> ```{chall_name}``` by **```{AUTHOR}```** @ {DATE} \n\n".format(chall_name = direct.replace("\\", "/").split("/")[-1], AUTHOR = AUTHOR, DATE = DATE)
    #return to original work dir
    os.chdir(origin_cwd)

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
    UpdateHomePage(direct)

def Write2HomePage():
    global io_path
    global web_recent
    global pwn_recent
    global crypto_recent
    global reverse_recent
    global misc_recent
    TO_BE_UPDATED = index_module.format(web_recent = web_recent, 
                                        pwn_recent = pwn_recent, 
                                        crypto_recent = crypto_recent, 
                                        reverse_recent = reverse_recent , 
                                        misc_recent = misc_recent)
    index_bak_path = os.path.join(io_path, "docs/index.md.bak")
    index_new_path = os.path.join(io_path, "docs/index.md")
    if not os.path.exists(index_bak_path):
        raise Exception("index.md.bak not found for {index_bak_path}".format(index_bak_path = index_bak_path))
    index_bak = open(index_bak_path, "r")
    index_bak_content = index_bak.read()
    index_bak.close()
    index_bak_content = index_bak_content.format(TO_BE_UPDATED = TO_BE_UPDATED)
    print index_bak_content
    index_new = open(index_new_path, "w")
    index_new.write(index_bak_content)
    index_new.close()
    
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
                print " ------"
    Write2HomePage()
