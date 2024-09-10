from pathlib import Path
from urllib.parse import unquote

import zipfile
import re
import json


# Rename file or dir.

def rename_file(path_obj):
    regex = re.compile(r"(\s\w{30,})(?:\.[a-zA-Z]{1,4})?$")
    match = regex.search(path_obj.name)

    if match:
        new_path_obj = path_obj.replace((str(path_obj).replace(match[1], "")))
        return new_path_obj


# Rename links in *.md files.

def rename_links_in_file(path):
    if not path.endswith(".md"):
        return
    
    regex = re.compile(r"\[(?:\n)?.*\(?.*\)?.*\](\(.*\.[a-zA-Z]{1,4}\))")
    
    with open(path, "r+", encoding="UTF-8") as f:
        text = f.read()
        
        matches = regex.findall(text)

        if matches:
            for el in matches:
                unquote_el = unquote(el)  # URL encoding - decode.

                u_regex = re.compile(r"(\s\w{30,})(?:\/|(?:\.[a-zA-Z]{1,4}))")
                u_match = u_regex.findall(unquote_el.replace("\\", "/"))
   
                for u_el in u_match:
                    unquote_el = unquote_el.replace(u_el, "")

                text = text.replace(el, unquote_el.replace(" ", "%20"))
            
            f.seek(0)
            f.truncate(0)  # If you don't use it, it writes strange things to the file.
            f.write(text)


# Getting files and subdirectories of a directory.
# Removes identifiers from names and inside *.md files.

def parse_folder(path):
    path_obj = Path(path)

    for el in path_obj.glob("*"):
        if (new_el := rename_file(el)):
            el = new_el

        if el.is_file():
            rename_links_in_file(str(el).replace("\\", "/"))
        elif el.is_dir():
            parse_folder(str(el).replace("\\", "/"))


# Unpacking a *.zip archive.

def unzip_file(path):
    with zipfile.ZipFile(path, "r") as zip_obj:
        try:
            new_path_obj = Path(path.rstrip(".zip"))
            new_path_obj.mkdir(parents=True, exist_ok=True)
            
            try:
                zip_obj.extractall(new_path_obj)
            except Exception as ex:
                print(ex)

        except FileExistsError as ex:
            print(ex)


def main():
    with open("settings.json", encoding="UTF-8") as settings:
        path = json.load(settings)["Zip archive path"].replace("\\", "/")

    # try:
    #     with open(path, encoding="UTF-8") as f:
    #         pass
    # except FileNotFoundError as ex:
    #     print(f'{ex}\n\nSpecify the correct path to the archive in the "files/settings.json" file.\n')
    #     return

    # unzip_file(path)
    parse_folder(path.rstrip(".zip"))


if __name__ == "__main__":
    main()
