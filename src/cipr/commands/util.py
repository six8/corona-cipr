from os import path
import os
import shutil
from fnmatch import fnmatch
    
def _get_file_list(root, child, exclude, include):    
    src_dir = root
    if child:
        src_dir = path.join(src_dir, child)
        
    files = []
    for filename in os.listdir(src_dir):
        part = filename
        if child:
            part = path.join(child, filename)
            
        src = path.join(root, part)

        skip = False
        if exclude:
            for p in exclude:
                if fnmatch(filename, p):
                    skip = True
                    break

        if skip:
            continue

        if not path.isdir(src) and include:
            skip = True
            for p in include:
                if fnmatch(filename, p):
                    skip = False
                    break

        if skip:
            continue

        if path.isdir(src):
            files.extend(_get_file_list(root, part, exclude=exclude, include=include))
        else:
            files.append(part)
    
    return files
        
def get_file_list(root, exclude=None, include=None):
    return _get_file_list(root, child=None, exclude=exclude, include=include)
    
def sync_dir_to(src_dir, dst_dir, exclude=None, include=None, ignore_existing=False):
    if not path.exists(dst_dir):
        os.makedirs(dst_dir)

    files_to_copy = get_file_list(src_dir, exclude=exclude, include=include)
    for filename in files_to_copy:
        src = path.join(src_dir, filename)
        dst = path.join(dst_dir, filename)
                
        if ignore_existing and path.exists(dst):
            continue
        else:
            yield (filename, dst)
            shutil.copy2(src, dst)

def sync_lua_dir_to(src_dir, dst_dir, exclude=None, include=None):
    if not path.exists(dst_dir):
        os.makedirs(dst_dir)

    if not include:
        include = []
    if '*.lua' not in include:
        include.append('*.lua')
        
    files_to_copy = get_file_list(src_dir, exclude=exclude, include=include)
    for filename in files_to_copy:
        name, ext = path.splitext(filename)
        if name.endswith('/init'):
            name = name[:-len('/init')]
            
        distname = name.replace('/', '_').replace('.', '_') + ext
        
        src = path.join(src_dir, filename)
        dst = path.join(dst_dir, distname)

        yield (filename, dst)
        
        shutil.copy2(src, dst)