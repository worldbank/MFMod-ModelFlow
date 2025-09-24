# -*- coding: utf-8 -*-
"""
@author: ibhan

Some utilities to manage files in a jupyterbook 


"""

import yaml
from pathlib import Path
import nbformat as nbf
import nbformat 
from glob import glob
import webbrowser
from subprocess import run
import webbrowser as wb
from pathlib import Path, PosixPath
from shutil import copy, copytree, copy2
import argparse
import re
from zipfile import ZipFile
import tempfile


 
bookdir='mfbook'
def get_all_files(fileloc=bookdir):
    all_notebooks = glob(f"{fileloc}/content/**/*.ipynb", recursive=True)
    return all_notebooks 

def get_all_notebooks(fileloc=bookdir):
    '''get all notebooks in the fileloc book'''
    all_notebooks = list(Path(f'{fileloc}/content').glob('**/*.ipynb'))
    relevant_notebooks = [f for f in all_notebooks if not '.ipynb_checkpoints' in f.parts]
    return relevant_notebooks 



def get_config(fileloc=bookdir):
    '''Get all files mentioned in the _toc but not the root'''
    with open(Path(fr'{fileloc}/_config.yml'), 'r') as f:
        config_data = yaml.safe_load(f)
    return config_data    

def get_latex_root(fileloc=bookdir):
    try:  
        latex_root = get_config(fileloc = fileloc)['latex']['latex_documents']['targetname'].split('.')[0]
    except: 
        latex_root = 'book'    
    return latex_root    


def is_notebook(filename):
    return  type(filename) == type(Path('ibs.ipynb')) and filename.suffix == '.ipynb'
    
    
def get_toc_files(fileloc=bookdir):
    '''Get all files mentioned in the _toc but not the root'''
    with open(Path(fr'{fileloc}/_toc.yml'), 'r') as f:
        toc_data = yaml.safe_load(f)

    # breakpoint() 
    
    
    file_list = []
    chapter_nr = 0

    def make_file_path(f):
        f_name  = f if f.endswith('.md') else f+'.ipynb'
        f_path = Path(fr'{fileloc}/{f_name}')
        return f_path

    
    def process_toc_entries(entries):
        nonlocal chapter_nr
        for i,entry in enumerate(entries):
            # print(i,entry)
            if 'file' in entry :
                filename = make_file_path(entry['file'])
                if filename.exists():
                    chapter_nr = chapter_nr + 1 
                    file_list.append(filename)
                else:   
                    file_list.append((filename,-1))

            if 'chapters' in entry:
                process_toc_entries(entry['chapters'])
            if 'sections' in entry:
                process_toc_entries(entry['sections'])
        # breakpoint() 

    file_list.append(make_file_path(toc_data['root']))
    
    process_toc_entries(toc_data.get('parts', []))
     # Print the list of file paths
     
    # for file_path in file_list:
    #     print(file_path)
    
    

    return file_list

from pathlib import Path
import yaml

def get_toc_files_level(fileloc):
    """
    Extract all filenames and their levels from a _toc.yml file.
    
    Returns a list of tuples: (Path to file, level)
    Level 1 = chapter, Level 2 = section, etc.
    """
    with open(Path(fileloc) / '_toc.yml', 'r', encoding='utf-8') as f:
        toc_data = yaml.safe_load(f)

    file_list = []

    def make_file_path(f):
        f_name = f if f.endswith('.md') else f + '.ipynb'
        return Path(fileloc) / f_name

    def process_toc_entries(entries, level):
        for entry in entries:
            if 'file' in entry:
                filename = make_file_path(entry['file'])
                file_list.append((filename, level if filename.exists() else -1))

            if 'chapters' in entry:
                process_toc_entries(entry['chapters'], level + 1)
            if 'sections' in entry:
                process_toc_entries(entry['sections'], level + 1)

    # Add root file at level 0
    root_file = make_file_path(toc_data['root'])
    file_list.append((root_file, 0 if root_file.exists() else -1))

    # Process chapters (normally in 'parts' or directly in root)
    if 'parts' in toc_data:
        for part in toc_data['parts']:
            process_toc_entries(part.get('chapters', []), level=1)
    elif 'chapters' in toc_data:
        process_toc_entries(toc_data['chapters'], level=1)

    return file_list



def start_notebooks(notebook_list):
    ''' start all notebooks in jupyter in the notebook list '''
    base_url = "http://localhost:8888/notebooks/"

    for notebook_path in notebook_list:
        # print(notebook_path)
        #print(f'{notebook_path.suffix=}')
        if is_notebook(notebook_path) :
            url = base_url + str(notebook_path )
            print(url)
            webbrowser.open(url, new=2)



def hide_cells(notebook_list):
    # Text to look for in adding tags
    text_search_dict = {
        "# HIDDEN": "remove_cell",  # Remove the whole cell
        "# NO CODE": "remove_input",  # Remove only the input
        "# HIDE CODE": "hide_input"  # Hide the input w/ a button to show
    }
    
    # Search through each notebook and look for th text, add a tag if necessary
    for ipath in notebook_list:
        try:
            ntbk = nbf.read(ipath, nbf.NO_CONVERT)
            changed = False
            
            for cell in ntbk.cells:
                cell_tags = cell.get('metadata', {}).get('tags', [])
                for key, val in text_search_dict.items():
                    # breakpoint() 
                    if key in cell['source']:
                        if val not in cell_tags:
                            cell_tags.append(val)
                            changed = True 
                            print(f'Tags set in {ipath=} \n{cell_tags=}')    
                if len(cell_tags) > 0:
                    cell['metadata']['tags'] = cell_tags
        
            if changed:             
                nbf.write(ntbk, ipath)
                print(f'notebook written {ipath}')
            else: 
                print(f'notebook not changed by hide_cells  : {ipath}')
        except: 
                print(f'Hide did not work for this notebook : {ipath}')

def box_nr_cells(notebook_list):
    
    running_nr = 0 
    box_toc =[]

    def make_box_nr(text): 
        patbox = r'(:::{index} single: Box.*?\n:::\n*)?:::{[Aa]dmonition} [Bb]ox (\d+)(\.\d*)* (.*)'

        nonlocal running_nr 
        nonlocal box_toc 
    
        def replace_box(match):
            nonlocal running_nr 
            if 0:
                for idx, group in enumerate(match.groups(), 1):
                    print(f"Group {idx}: {group}")

            lf = '\n'
            running_nr =running_nr + 1
            box_index = f":::{{index}} single: Boxes; Box{running_nr:>4}. {match[4]}{lf}:::"
            box_name = f":::{{admonition}} Box {running_nr}. {match[4]}"
            replace   = f"{box_index}{lf}{lf}{box_name}"
            box_toc.append( box_name )
            if 1: print(f'{replace=}')
            return replace 
        
        return re.sub(patbox, replace_box,text)
       
    for ipath in notebook_list:
        # breakpoint() 
        try:
            ntbk = nbf.read(ipath, nbf.NO_CONVERT)
            changed = False
            for cell in ntbk.cells:
                    # breakpoint() 
                    if (newsource := make_box_nr( cell['source'])):
                        if newsource != cell['source'] :
                            changed = True 
                            # print(f'box change {ipath=} \n{newsource=}')    
                            cell['source'] = newsource 
        
            if changed:             
                nbf.write(ntbk, ipath)
                print(f'notebook written {ipath}')
            else: 
                print(f'notebook not changed by box numbering   : {ipath}')
        except: 
                print(f'Box did not work for this file : {ipath}')
        
    print('\n boxes in the book',*box_toc,sep='\n')        
    return 


def search(notebook_list, pat=r'.*[Bb]ox.*', notfound=False, silent=0, showfiles=False,
           fileopen=False, printmatch=False, replace=False, savecell=True,onlymarkdown=False,returnfound=False,
           flags=0):
    """
    Search for a specified pattern in Jupyter notebooks within a list of paths and optionally replace it.

    Parameters:
    - notebook_list (list): A list of paths to Jupyter notebooks.
    - pat (str): The regular expression pattern to search for in the cells' source code. 
                 Default is '.*[Bb]ox.*'.
    - notfound (bool): If True, return a list of notebooks where the pattern is not found.
                       If False, return a list of notebooks where the pattern is found.
                       Default is False.
    - silent (int): If not 0, suppress print statements. Default is 0.
    - showfiles (bool): If True, print the list of files where the pattern is found or not found.
                        Default is True.
    - fileopen (bool): If True, open the notebooks where the pattern is found with the default system application.
                       Default is False.
    - printmatch (bool): If True, and if silent is 0, print the matched patterns; otherwise, print the entire cell content.
                         Default is False.
    - replace (str or False): The replacement string for the pattern. If False, no replacement is done.
                              Default is False.
    - savecell (bool): If True and replace is not False, save the cell with the replaced content back to the notebook.
                       Default is True.

    Returns:
    - list: A list of paths to notebooks where the pattern is found or not found, based on the 'notfound' parameter.
    
    Note:
    - The function uses regex to search for and optionally replace the specified pattern in the source code of each cell.
    - If 'showfiles' is True, it prints the list of files where the pattern is found or not found.
    - If 'fileopen' is True, it opens the notebooks with the pattern found using the default system application.
    - If 'replace' is a string, the pattern is replaced with this string in the notebook cells, and changes are saved if 'savecell' is True.
    """


    

    found_list = []
    notebook_list_path = [i for i in notebook_list if is_notebook(i)]
    match_list = []
    
    if not silent: print(f'Search patter:{pat}')
    for ipath in notebook_list_path:
        found = False 
        
        try:

            with open(ipath, 'r',encoding='utf-8') as f:
                ntbk = nbf.read(f, nbf.NO_CONVERT)
                
            for cell in ntbk.cells:
                    if onlymarkdown and cell.cell_type != 'markdown':
                        # print(f'{onlymarkdown=} {cell.cell_type=}')
                        continue
                    # breakpoint() 
                    source =  cell['source']
                    matches = re.findall(pat, source,flags=flags)
                    if len(matches):
                        match_list = match_list + [(m,ipath) for m in matches]
                        found = True                            
                        # breakpoint()
                        if not silent:     
                                print(f"\nPattern  here: {'/'.join(ipath.parts[-2:])}")         
                                if printmatch: 
                                    print(*matches,sep='\n')
                                else: 
                                    print(source)
                        if replace: 
                            newsource = re.sub(pat,replace,source,flags=flags)
                            print(f'\nThis\n{source}\nReplaced by:\n{newsource}')
                            if savecell: 
                                cell.source=newsource
            if found: 
               found_list.append(ipath)  
               if replace and savecell: 
                   with open(ipath, 'w',encoding='utf-8') as f:
                       nbf.write(ntbk,f)

        except Exception as e: 
                print(f'Search did not work for this file : {ipath} , {e}')
    not_found_list =     [f for f in notebook_list_path if f not in found_list] 
    if  showfiles: 
        print(f'\n{pat} found here: ')
        print(*[name for name  in found_list],sep='\n')
        print(f'\n{pat} Not found here: ')
        print(*[name for name  in not_found_list],sep='\n')
    if printmatch:
        print(*match_list,sep='\n')
    if fileopen: 
        start_notebooks(found_list)
    if returnfound: 
        return match_list 
    else:
        return not_found_list if notfound else found_list 



def copy_png_files(file_paths, destination_dir):
    """
    Copies all .png files from the directories containing the given file paths
    to the destination directory, replicating the directory structure.

    :param file_paths: List of Path objects pointing to files or directories.
    :param destination_dir: Path object for the destination directory.
    """
    destination_dir = Path(destination_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)  # Ensure destination exists

    # Extract unique source directories from the list of files
    source_dirs = sorted({f.relative_to('.').parent for f in file_paths if f.exists()})
    print(source_dirs)
    for source_dir in source_dirs:
        for png_file in source_dir.glob("*.png"):
            # Calculate the relative path of the file within the source directory
            relative_path = png_file.relative_to(source_dir)

            # Create the corresponding directory structure in the destination
            target_dir = destination_dir / source_dir 
            target_dir.mkdir(parents=True, exist_ok=True)

            # Copy the file to the destination, preserving structure
            destination_file = target_dir / png_file.name
            copy2(png_file, destination_file)
            print(f"Copied {png_file} to {destination_file}")

    print("Copy operation complete.")

def copy_files_with_structure(file_paths, destination,
                          clear_output=False, clear_widgets = False, clear_index=False):
    """
    Copies files from a list of relative paths to a destination directory,
    preserving their relative directory structure.

    :param file_paths: List of pathlib.Path objects representing relative file paths.
    :param destination: The destination directory as a pathlib.Path object.
    """
    destination = Path(destination)
    if not destination.exists():
        destination.mkdir(parents=True, exist_ok=True)

    for file_path in file_paths:
        src = file_path.resolve()
        if not src.exists():
            print(f"File not found: {src}")
            continue

        # Preserve the relative structure by appending the relative path to the destination
        dest = destination / file_path
        dest.parent.mkdir(parents=True, exist_ok=True)  # Create necessary directories

        try:
            if file_path.suffix.lower() == ".ipynb":
                clear_notebook_output(str(src), str(dest),
                   clear_output=clear_output, clear_widgets = clear_widgets, clear_index=clear_index)  # Ensure paths are passed as strings
                print(f"Cleared and copied {src} to {dest}")
            else:
                copy(src, dest)
                print(f"Copied {src} to {dest}")
            
        except Exception as e:
            print(f"Error copying {src} to {dest}: {e}")


def clear_notebook_output(notebook_path: Path, output_path: Path = None,
                          clear_output=False, clear_widgets = False, clear_index=False):
    """
    Clears the output of all cells in a Jupyter Notebook.

    Args:
        notebook_path (Path): Path to the notebook file to clear.
        output_path (Path): Path to save the cleared notebook. Defaults to overwriting the original file.

    Returns:
        None
    """
    try:
        # Ensure input paths are Path objects
        notebook_path = Path(notebook_path)
        output_path = Path(output_path) if output_path else notebook_path

        # Read the notebook
        with notebook_path.open("r", encoding="utf-8") as f:
            notebook = nbf.read(f, as_version=4)

        # Clear output of all code cells
        if clear_output: 
            for cell in notebook.cells:
                if cell.cell_type == "code":
                    cell.outputs = []
                    cell.execution_count = None

        if clear_widgets: 
            if "widgets" in notebook.metadata:
                del notebook.metadata["widgets"]

        if clear_index:
            index_pattern = re.compile(r':::{index}[\s\S;.:]*?:::', re.MULTILINE)
            for cell in notebook.cells:
                if cell.cell_type == "markdown":
                    new_source = re.sub(index_pattern, '', cell.source).strip()
                    new_source = re.sub(r"^:class:.*\n?", "", new_source, flags=re.MULTILINE)
                    new_source = re.sub(r"^:::{[aA]dmonition}\s+(.+?)\s*\n", r"**\1**\n\n", new_source, flags=re.MULTILINE)
                    new_source = re.sub(r"^:::{([nN]ote|[wW]arning)}\s*(.*)", r"**\1**\n\n\2", new_source, flags=re.MULTILINE)

                    new_source = re.sub(r"^:::{(?:[iI]mage|[oO]nly)}[\s\S]*?^:::", "", new_source, flags=re.MULTILINE)
                    new_source = re.sub(r"\n?^:::$", "", new_source, flags=re.MULTILINE)

                    if new_source != cell.source:
                        cell.source = new_source

            notebook.cells = [cell for cell in notebook.cells if not 
                              (
                               len(source:= cell.source.strip())==0 
                               )]    

        # Save the cleared notebook
        with output_path.open("w", encoding="utf-8") as f:
            nbf.write(notebook, f)

        # print(f"Cleared notebook saved to: {output_path}")
        

    except Exception as e:
        print(f"Error clearing notebook output: {e}")



def remove_jupyter_book_index(nb_path):
    """Remove Jupyter Book index directives enclosed in :::index ... ::: from Markdown cells in a Jupyter Notebook."""
    
    nb_path = Path(nb_path)
    notebook = nbformat.read(nb_path, as_version=4)
    
    modified = False
    index_pattern = re.compile(r':::index[\s\S]*?:::', re.MULTILINE)
    
    for cell in notebook.cells:
        if cell.cell_type == "markdown":
            new_source = re.sub(index_pattern, '', cell.source).strip()
            
            if new_source != cell.source:
                cell.source = new_source
                modified = True
    
    if modified:
        nbformat.write(notebook, nb_path)
        print(f"Updated: {nb_path}")
    else:
        print(f"No changes needed: {nb_path}")

def process_notebooks(nb_files):
    """Process a list of Jupyter Notebook files."""
    for nb_file in nb_files:
        nb_path = Path(nb_file)
        if nb_path.exists() and nb_path.suffix == ".ipynb":
            remove_jupyter_book_index(nb_path)
        else:
            print(f"Skipping invalid file: {nb_path}")

# Example usage

def insert_colab(notebook_list):
    content="""\
#This is code to manage dependencies if the notebook is executed in the google colab cloud service
if 'google.colab' in str(get_ipython()):
  import os
  os.system('apt -qqq install graphviz')
  os.system('pip -qqq install ModelFlowIb')

%load_ext autoreload
%autoreload 2
"""  

    for ipath in notebook_list:
        try:
            found = False
           
            with open(ipath, 'r') as f:
                ntbk = nbf.read(f, nbf.NO_CONVERT)
               
            for cell in ntbk.cells:
                    # breakpoint() 
                    source =  cell['source']
                    amatch = re.search(r'google\.colab', source)
                    if amatch:
                        ...
                        found = True # breakpoint()
            if found:             
                print(f"Colab cell found here   : {'/'.join(ipath.parts[-2:])} ")  
            else:
                # breakpoint() 
                print(f"NO Colab cell found here: {'/'.join(ipath.parts[-2:])} ") 
                new_cell = nbf.v4.new_code_cell(source=content)
                if 'id' in new_cell:
                    del new_cell['id']
                cell_tags = cell.get('metadata', {}).get('tags', [])
                cell_tags.append("remove_cell")
                new_cell['metadata']['tags'] = cell_tags
# Step 3: Insert the new cell at a specific position (e.g., second position)
                ntbk.cells.insert(1, new_cell)
                with open(ipath, 'w') as f:
                    ...
                    nbf.write(ntbk, f)
                    
                print(f'Notebook written {"/".join(ipath.parts[-2:])}')

    
        except: 
                print(f'Search colab did not work for this file : {ipath}')
        

def insert_cell(notebook_list,
     content="""\
# Prepare the notebook for use of modelflow 

# Jupyter magic command to improve the display of charts in the Notebook
%matplotlib inline

# Import pandas 
import pandas as pd

# Import the model class from the modelclass module 
from modelclass import model 

# functions that improve rendering of modelflow outputs
model.widescreen()
model.scroll_off();"""  ,
     condition= r'',
     tags=['remove_cell']):
    
    """
    Inserts a specific code cell into Jupyter notebooks if a certain condition is met.

    The function checks each notebook in the provided list. If the notebook contains 
    a cell that matches the given condition, it will print a message. If no such cell
    is found, a new cell with the specified content is added to the notebook.

    Parameters:
    - notebook_list (list): A list of paths to Jupyter notebooks.
    - content (str): The content of the cell to be inserted. By default, it contains
      code to manage dependencies for Google Colab.
    - condition (str, regex pattern): A regex pattern that, if found in a notebook cell,
      will prevent the insertion of the new cell.
    - tag (str): A tag to append to the metadata of the new cell.

    The function will print messages indicating:
    1. Notebooks where a cell matching the condition is found.
    2. Notebooks where the new cell is inserted.
    3. Notebooks where searching failed.

    Note: The function uses nbformat to manipulate notebooks and expects valid notebook paths.
    """    

    for ipath in [ n for n in notebook_list if is_notebook(n)]:
        try:
            found = False
               
            with open(ipath, 'r',encoding='utf-8') as f:
                ntbk = nbf.read(f, nbf.NO_CONVERT)
                
            for cell in ntbk.cells:
                    # breakpoint() 
                    if condition: 
                        source =  cell['source']
                        amatch = re.search(condition, source)
                        if amatch:
                            ...
                            found = True # breakpoint()
                    else: 
                         found=False 
            if found:             
                print(f"Cell found here   : {'/'.join(ipath.parts[-2:])} ")  
            else:
                # breakpoint() 
                print(f"NO  cell found here: {'/'.join(ipath.parts[-2:])} ") 
                new_cell = nbf.v4.new_code_cell(source=content)
                if 'id' in new_cell:
                    del new_cell['id']
                cell_tags = cell.get('metadata', {}).get('tags', [])
                for tag in tags: 
                    if tag not in cell_tags:
                        cell_tags.append(tag)
                new_cell['metadata']['tags'] = cell_tags
# Step 3: Insert the new cell at a specific position (e.g., second position)
                ntbk.cells.insert(1, new_cell)
                
                with open(ipath, 'w',encoding='utf-8') as f:
                    ...
                    nbf.write(ntbk, f)
                    
                print(f'Notebook written {"/".join(ipath.parts[-2:])}')

    
        except Exception as e: 
                print(f'Insert did not work for this file : {ipath} {e}')
        

def make_yaml(notebook_list):
    for nb in notebook_list:
            yaml_dir = Path(nb.parts[0]) / 'yml/'
            new_yaml_path = yaml_dir / nb.with_suffix('.yml').name.lower() 
            # path_without_extension = nb.with_suffix('')
            path_without_extension = nb

# Remove the first level of folders ("/home" in this case)
            toc_entry = Path(*path_without_extension.parts[2:])
            # print(f'makes yml for: {nb}')
            update_toc_yaml(Path(*nb.parts[1:]), yaml_dir /'generic.yml', new_yaml_path)
        
       # update_toc_yaml(nb, org_yaml_path, new_yaml_path)
              


def zip_directory_with_pathlib(directory_path, output_zip):
    """
    Zips all files in a directory into a single zip file using pathlib,
    ensuring the target directory for the zip file is created if it doesn't exist.

    Args:
        directory_path (str or Path): Path to the directory to be zipped.
        output_zip (str or Path): Path for the output zip file.

    Returns:
        None
    """
    directory_path = Path(directory_path).resolve()
    output_zip = Path(output_zip).resolve()

    # Ensure the source directory exists
    if not directory_path.is_dir():
        raise ValueError(f"{directory_path} is not a valid directory.")

    # Create the target directory for the zip file if it doesn't exist
    output_zip.parent.mkdir(parents=True, exist_ok=True)

    # Check for conflicts with existing files/directories
    if output_zip.exists():
        if output_zip.is_dir():
            raise PermissionError(f"{output_zip} already exists as a directory.")
        else:
            print(f"Overwriting existing file: {output_zip}")

    # Create the zip file
    with ZipFile(output_zip, 'w') as zipf:
        for file_path in directory_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(directory_path)
                zipf.write(file_path, arcname)

    print(f"All files in {directory_path} have been zipped into {output_zip}")

def make_replication(zip=True,destinationdir = 'mfbook/replication/mfbook'):
        toc_files = get_toc_files('mfbook')

        image_pairs = (search(toc_files,r'\b[\w\-]+\.png\b',notfound=False,returnfound=True,silent=0)
                      + search(toc_files,r'\b[\w\-]+\.PNG\b',notfound=False,returnfound=True,silent=0)
                       )
        image_paths = [notebook_path.parent / filename for filename, notebook_path in image_pairs]


        with tempfile.TemporaryDirectory() as clean_folder:
            print("Temp dir:", clean_folder)
            extra_files = [
                Path('mfbook/content/models/pak.pcim'),
                Path('mfbook/content/Overview.ipynb'),
                Path('build.py'),
                Path('modelutil_cli.py'),
                Path('Reproducibility README.md'),
                Path('Reproducibility README.ipynb'),
                Path('mfbook/references.bib'),
                Path('mfbook/_toc.yml'),
              #  Path('mfbook/mfinstall.cmd'),
              # Path('mfbook/mfgo.cmd'

                Path('mfbook/_config.yml'),
            ]
            if zip:
                copy_files_with_structure(toc_files + extra_files + image_paths,
                                      clean_folder,
                                      clear_output=True,
                                      clear_widgets=True,
                                      clear_index=False)
                zip_directory_with_pathlib(clean_folder,destinationdir+'.zip' )
            else:
                copy_files_with_structure(toc_files + extra_files + image_paths,
                                      destinationdir,
                                      clear_output=True,
                                      clear_widgets=True,
                                      clear_index=False)
                

def extract_headings(toc_files):
    """
    Extract the first markdown heading from each notebook using nbformat.
    
    Parameters:
    toc_files (list of str): Paths to Jupyter notebook files.
    
    Returns:
    list of tuples: Each tuple contains (path, heading), where heading is the
                    first line in a markdown cell starting with '#'.
    """
    result = []

    for path in toc_files:
        if not path.is_file() or path.suffix != ".ipynb":
            print(str(path), "[Invalid or not a notebook file]")
            continue

        try:
            with open(path, 'r', encoding='utf-8') as f:
                notebook = nbf.read(f, as_version=4)

            heading = None
            for cell in notebook.cells:
                if cell.cell_type == "markdown":
                    for line in cell.source.splitlines():
                        stripped_line = line.lstrip()
                        if stripped_line.startswith("#"):
                            heading = stripped_line.strip()[2:]
                            break
                    if heading:
                        break

            result.append((path, heading if heading else "[No heading found]"))
        except Exception as e:
            result.append((path, f"[Error reading notebook - {e}]"))

    return result

from typing import NamedTuple, List
class NotebookInfo(NamedTuple):
    path: Path
    heading: str
    short_path: str

def extract_headings(toc_files) -> List[NotebookInfo]:
    """
    Extract the first markdown heading from each notebook using nbformat.
    
    Parameters:
    toc_files (list of Path): Paths to Jupyter notebook files.
    
    Returns:
    list of NotebookInfo: Each entry contains (full path, heading, short path without 'mfbook/content/').
    """
    from urllib.parse import quote

    result = []
    chapter = 0 
    for path,level in toc_files:
        if not path.is_file() or path.suffix != ".ipynb":
            print(str(path), "[Invalid or not a notebook file]")
            continue

        try:
            with open(path, 'r', encoding='utf-8') as f:
                notebook = nbf.read(f, as_version=4)

            heading = None
            for cell in notebook.cells:
                if cell.cell_type == "markdown":
                    for line in cell.source.splitlines():
                        stripped_line = line.lstrip()
                        if stripped_line.startswith("#"):
                            heading = stripped_line.strip()[2:]  # Remove '# ' prefix
                            break
                    if heading:
                        break
            if level==1:
                chapter = chapter + 1
                section = 0
                heading = (f'{chapter:4} {heading}')
            elif level == 2:
                section = section + 1 
                heading = (f'{chapter:4}.{section:1}    {heading}')  
            elif level == 0:
                heading == heading  
            else:
                breakpoint() 
                
            safe_path = quote(str(path).replace('\\','/'))
            short_path = str(path.relative_to("mfbook/content"))
            #short_path = PosixPath(path.relative_to("mfbook/content")).as_posix()
            html_text = f'<a href="{safe_path}" target="_blank">{heading if heading else "[No heading found]"}</a>'
            result.append(NotebookInfo(path=path, heading=html_text, short_path=f'{short_path}'))
        except Exception as e:
            result.append(NotebookInfo(path=path, heading=f"[Error reading notebook - {e}]", short_path="[error]"))

    return result


from typing import List

def headings_to_markdown_table() -> str:
    """
    Create a Markdown table from a list of NotebookInfo entries.

    Columns: name | path | note
    """
    toc_files = get_toc_files_level('mfbook')
    notebook_infos = extract_headings(toc_files)

    lines = [
        "| name | path | note |",
        "|:------|:------|------|"
    ]

    for info in notebook_infos:
        name = info.heading.replace('|', '\\|')  # Escape pipe characters
        path = info.short_path
        lines.append(f"| {name} | {path} |  |")

    res =  "\n".join(lines)
    return res

            
# Call the function to start the notebooks
# start_notebooks(notebook_list)

#%% main

if __name__ == '__main__':
     
     import sys
     print('Modelutil called with', sys.argv)
    
    
     parser = argparse.ArgumentParser(description="CLI tool for jupyterbook.")
     bookdir_arg = {
        "type": str,
        "default": "mfbook",
        "help": "Directory of the jupyter book"
    }
     parser.add_argument('-b','--bookdir', **bookdir_arg)
    
     # Add subparsers for the sub-commands
     subparsers = parser.add_subparsers(dest="subcommand", help="Available sub-commands")
     # Common argument to be used in all subparsers
    
     box_parser = subparsers.add_parser("box", help="Renumber boxes in the jupyterbook")
     
     open_parser = subparsers.add_parser("open", help="Open all notebooks in the jupyter book ")
     
     list_parser = subparsers.add_parser("list", help="List all files in the jupyter book")
   
     search_parser = subparsers.add_parser("search", help="Search all files in the jupyter book")
     search_parser.add_argument('-p','--pattern', help='Regex search pattern ')
     search_parser.add_argument('-o','--open', action="store_true", help='Open files with pattern ')
     search_parser.add_argument('-ns','--nsilent', help='Not Silent ',action="store_false")

     insert_parser = subparsers.add_parser("insert", help="All notebooks which does not fulfill condition will have cell with content inserted")
   
     insert_parser.add_argument('-c','--colab', action="store_true", help='Insert a Colab enabeling cell ')
     insert_parser.add_argument('-a','--auto', action="store_true", help='Insert a auto load cell ')


     # Parse the arguments
     args = parser.parse_args()
     

    
     # Handle sub-commands
     if args.subcommand == "open":
         print(f"Open")
         toc_files  = get_toc_files(fileloc=args.bookdir)    
         start_notebooks(toc_files)    
         
     elif args.subcommand == "box":
         print('Box is run')
         toc_files  = get_toc_files(fileloc=args.bookdir)
         box_nr_cells(toc_files)
             
     elif args.subcommand == "list":
  
        toc_files  = get_toc_files(fileloc=args.bookdir)
        print(*[name for name  in toc_files],sep='\n')
        
     elif args.subcommand == "search":
         print('Search is run')

         toc_files  = get_toc_files(fileloc=args.bookdir)
        
         found_files = search(toc_files,pat=args.pattern, silent = args.nsilent)
         if  args.open: 
             start_notebooks(found_files)
         

     elif args.subcommand == "insert":
         print('insert is run')
         toc_files  = get_toc_files(fileloc=args.bookdir)
         if args.colab: 
             insert_cell(toc_files)
         if args.auto:
             insert_cell(toc_files,
            content="""\
%load_ext autoreload
%autoreload 2
"""  ,
     condition= r'autoreload',
     tag='remove_cell')
             



     elif args.subcommand is None:
        # Handle the case where no sub-command is given
        print(f"Using book directory: {args.bookdir}")    
    
    
 #%% run   
     toc_files = get_toc_files(args.bookdir)
     all_notebooks = get_all_notebooks()
     
     
     if 0:
         insert_cell(toc_files) 
     
     if 0: 
         insert_cell(toc_files,
         content="""\
     #This is code to manage dependencies if the notebook is executed in the google colab cloud service
     if 'google.colab' in str(get_ipython()):
       import os
       os.system('apt -qqq install graphviz')
       os.system('pip -qqq install ModelFlowIb ipysheet  --no-dependencies ')
     """            ) 

     
     if 0: 
        print(*[name for name  in toc_files],sep='\n')
     if 0:    
        start_notebooks(toc_files)    
        
     if 0: 
        box_nr_cells(toc_files)
        
     if 0:
        search(toc_files,r'ipysheet  --no-dependencies',replace = ' ', notfound=False,silent=0,fileopen=0)
        search(toc_files,r'\[.*\]\(\)',notfound=False,silent=0,fileopen=0,printmatch=1)
        search(toc_files,r'savefigs',notfound=False,silent=0,fileopen=0)
        search(toc_files,r'{index} .* \.equp',notfound=False,silent=0)
        search(toc_files,'::{image}',notfound=False,silent=0)
        
#%% ``` 
     #   w = search(toc_files, r"^({(?:[iI]mage|[oO]nly)}[\s\S]*?^)```")
        #search(toc_files,r':::{ge',replace= ':::{image',notfound=False,silent=0,fileopen=0)
        search(toc_files,r"^```({note}[\s\S]*?)^```", replace = r":::\1\n:::",savecell=False,silent=0,fileopen=0,flags=re.MULTILINE)

#%% Replication 
     if 0:
#%% Replication          
        extra_files = [Path('mfbook/content/models/pak.pcim'),
                       Path('mfbook/content/Overview.ipynb'),
                  #     Path('mfbook/mfinstall.cmd'),
                   #    Path('mfbook/mfgo.cmd'),  # Problem  gmail blocks sending 
                   
                       ]
        toc_files_ipynb = [f for f in toc_files if f.suffix == ".ipynb"]
        repl_files = toc_files_ipynb + extra_files
        copy_files_with_structure(repl_files, '/replication',
         clear_output=True,clear_widgets=True,clear_index=True )
        zip_directory_with_pathlib('/replication','/replication_zip/mfbook.zip')
#%% clean book 
     if 0:
#%%  clean book   
        image_pairs = (search(toc_files,r'\b[\w\-]+\.png\b',notfound=False,returnfound=True,silent=0)
                      + search(toc_files,r'\b[\w\-]+\.PNG\b',notfound=False,returnfound=True,silent=0)
                       )
        image_paths = [notebook_path.parent / filename for filename, notebook_path in image_pairs]


        with tempfile.TemporaryDirectory() as clean_folder:
            print("Temp dir:", clean_folder)
            extra_files = [
                Path('mfbook/content/models/pak.pcim'),
                Path('mfbook/content/Overview.ipynb'),
                Path('build.py'),
                Path('modelutil_cli.py'),
                Path('Reproducibility README.md'),
                Path('mfbook/references.bib'),
                Path('mfbook/_toc.yml'),
              #  Path('mfbook/mfinstall.cmd'),
              # Path('mfbook/mfgo.cmd'

                Path('mfbook/_config.yml'),
            ]
            copy_files_with_structure(toc_files + extra_files + image_paths,
                                      clean_folder,
                                      clear_output=True,
                                      clear_widgets=True,
                                      clear_index=False)
            # copy_png_files(toc_files, clean_folder)
            zip_directory_with_pathlib(clean_folder, 'mfbook/replication/mfbook.zip')
        
#%% test 

        


     if 0:
        toc_test = [toc_files[1]]
        insert_colab(toc_test)
     if 0:
        toc_test = [toc_files[1]]
        make_yaml(toc_files)
    # hide_cells(toc_files)
     if 0:
        _=  search(toc_files,r"^\(([^)]+)\)="     ,notfound=False,silent=1,printmatch=1,showfiles=False,returnfound=True)

    
    
