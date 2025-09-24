# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 19:50:51 2022

builds a jupyterbook 

look at the cheatcheet. 

build.py builds the html site 
            and copies all /_build/ png,svg and pdf files to the root
			to enable figures in the latex build 
           

python build.py # creates mfbook/  as html 
python build.py latex # creates mfbook/ as html and latex
python build.py latex nopdf # create latex source but not pdf (for use with tex) 
python build.py copy # if you are ib this will copy to the location to host web version in github 
python build.py <a toc file name, no in the mfbook folder ending in .yml>  will create a proofreading version only from this toc 

python build.py makezip # creates a zipfile for replication

to create another book, it should be in papers/<a folder ending in book> # this will create the book in the folder. 
python build.py testbook  # creates testbook/   as html



@author: ibhan
"""
from subprocess import run
import webbrowser as wb
from pathlib import Path
from shutil import copy, copytree
import yaml 

 
import sys

import modelutil_cli  as mu 

import re
print('Build  called with:', sys.argv)
options = sys.argv 
# raise Exception('stop')
for aname in options: 
    if aname.endswith('book'):
        bookdir = aname
        break
else:
    bookdir = 'mfbook' 
    
for aname in options: 
    if aname.endswith('.yml'):
        testtoc = 'yml/'+aname
        test = True 
        break
else:
    testtoc = ''   
    test = False
 
print(f'{testtoc=} {test=}')    
 
doall = '--all' if 'all' in options else ''
buildloc = Path(f'{bookdir}/_build/')
buildhtml = buildloc / 'html'
# (destination := Path(fr'C:/modelbook/IbHansen.github.io/{bookdir}')).mkdir(parents=True, exist_ok=True)
fileloc = str((buildhtml / 'index.html').absolute())

#print(f'{fileloc=}\n{destination=}')
print(f'{fileloc=}\n') #dropped destination
latexroot = mu.get_latex_root(bookdir)   

tocloc     = Path(bookdir) /'_toc.yml'
if test: 
    toctestloc     = Path(bookdir) /testtoc

toccopyloc = Path(bookdir) /'_toc_copy.yml'
copy(tocloc,toccopyloc)

if test:    
    copy(toctestloc,tocloc)
        
# breakpoint()
try:
   # xx0 = run(f'jb build {bookdir}/ {doall} --path-output {bookdir}/ibstest/')
    xx0 = run(f'jb build {bookdir}/ {doall} ')
except Exception as e:
    print(f'Error in call to jupyterbook  {e} ')
finally:     
    copy(toccopyloc,tocloc)



if not xx0.returncode:
    wb.open(rf'file://{fileloc}', new=2)
else: 
    exit()   
    
          


#%% 
latexdir = Path(f'{bookdir}/_build/jupyter_execute/content')
for dir in sorted(Path(f'{bookdir}/_build/jupyter_execute').glob('**')):
    # print(f'{dir=}')
    for i, picture in enumerate(sorted(dir.glob('*.png'))):
        # print(picture) 
        try:
            copy(picture,latexdir)
        except:
            # print(f'Not copied{picture}')
            ...
    for i, picture in enumerate(sorted(dir.glob('*.svg'))):
        # print(picture) 
        try:
            copy(picture,latexdir)
        except:
            ...
            # print(f'Not copied{picture}')
    for i, picture in enumerate(sorted(dir.glob('*.pdf'))):
        # print(picture) 
        try:
            copy(picture,latexdir)
        except:
            ...
            # print(f'Not copied{picture}')
            
#%%    

def replace_latex_citations(latex_string):
    """
    Replaces the LaTeX citation format from {[}...{]}) to {(}...{)})
    in the provided LaTeX string.

    Parameters:
    latex_string (str): A string containing LaTeX source code.

    Returns:
    str: The modified LaTeX string with updated citation format.
    """
    # Regex pattern to find the citations
    pattern = r'\{\[\}(\\hyperlink{cite\.Reference:id\d+}\{\d+\})\{\]\}'

    # Replacement pattern
    replacement = r'{(}\1{)}'

    # Replace the pattern in the string
    modified_string = re.sub(pattern, replacement, latex_string)

    return modified_string



def modify_latex_tabels(latex_source):
    # Split the source into lines
    # print(latex_source)
    lines = latex_source.split('\n')
    
    # Prepare to collect modified lines
    modified_lines = []
    
    # Define the target line start to search for
    target_start = r'\begin{tabulary}{\linewidth}[t]'
    # Define the line to insert
    insert_line = r'\renewcommand{\arraystretch}{1.1}'
    
    # Iterate through each line in the original source
    for line in lines:
        # Check if the line starts with the target start
        if line.strip().startswith(target_start):
            # Insert the new command line before the target line
            modified_lines.append(insert_line)
            
            # Modify the parameters inside the tabulary line
            # Remove vertical bars and replace 'T' with 'l'
            part1, part2 = line.strip() .rsplit('{', 1)
            modified_part = part2.replace('|', '').replace('T', 'l')
            line = part1 + '{' + modified_part
        
        # Add the current line to the modified lines
        modified_lines.append(line)
    
    # Join the modified lines back into a single string
    modified_latex_source = '\n'.join(modified_lines)
    
    return modified_latex_source

def remove_selective_hlines_in_tabulary(latex_source):
    import re
    
    # Split the document into parts based on the tabulary environments
    parts = re.split(r'(\\begin{tabulary}.*?\\end{tabulary})', latex_source, flags=re.DOTALL)
    pattern = re.compile(r'(\\begin\{tabulary\}\{\\linewidth\}\[t\]\{l)(l*)\}')

    print(f'{len(parts)=}')
    def replace_l(match):
        # Get the full match parts
        part1 = match.group(1)
        part2 = match.group(2)
        # Replace all 'l' with 'L' in part2
        part2 = part2.replace('l', 'L')
        return part1 + part2 +'}'
    
    # Function to remove \hline from a single tabulary block
    def process_tabulary_block(block):
        lines = block.split('\n')
        result_lines = []
        hline_count = 0
        is_inside_tabulary = False
        # print(f'{lines[0]=}')

        for line in lines:
            # print(f'{line=}')

            if '\\begin{tabulary}' in line:
               # result_lines.append(r'\afterpage{\clearpage}') # to avoid flowing over the bottom  
                is_inside_tabulary = True
                hline_count = 0  # Reset hline count for each tabulary block
                # print(f'{is_inside_tabulary=}')

            
            if is_inside_tabulary:

                if line.strip() == '\\hline':
                    # print(f'hit {line=}')

                    hline_count += 1
                    # Keep the first two and the last \hline
                    if hline_count == 1 or  hline_count == 2 :
                        result_lines.append(line)
                elif '\\end{tabulary}' in line.strip():
                    result_lines.append('\\hline')

                    is_inside_tabulary = False
                    result_lines.append(line)
                else:
                    
                    result_lines.append(line)
            else:
                result_lines.append(line)

        return '\n'.join(result_lines)

    # Apply the processing only to parts that are tabulary blocks
    processed_parts = []
    for part in parts:
        if '\\begin{tabulary}' in part:
            new_part = process_tabulary_block(part)
            new_part = pattern.sub(replace_l, new_part)
            processed_parts.append(new_part)
            
        else:
            processed_parts.append(part)
    
    # Join all parts back into the full document
    modified_latex_source = ''.join(processed_parts)
    return modified_latex_source

def modify_latex_tabularx(latex_source):
    """
Modifies LaTeX tabularx environments in the provided text.

This function processes the LaTeX text, finds and comments out
tabularx environments, and converts tabulary environments back
to tabularx.

Args:
    latex_source (str): The input LaTeX text.

Returns:
    str: The modified LaTeX text with tabularx changes.
"""

    lines= latex_source.split('\n')

    # Pattern to match the line starting with \textbackslash{}begin{tabularx}
    tabularx_pattern = re.compile(r"^\\textbackslash\{\}begin\\\{tabularx")
                                #      \textbackslash{}begin\{tabularx\}\{\textbackslash{}textwidth\}\{>\{\textbackslash{}raggedright\textbackslash{}arraybackslash\}p\{3cm\}>\{\textbackslash{}raggedright\textbackslash{}arraybackslash\}p\{4cm\}>\{\textbackslash{}raggedright\textbackslash{}arraybackslash\}X\}

    # Function to unescape LaTeX text
    def unescape_latex(text):
        return text.replace('\\textbackslash{}', '\\').replace(r'\{', '{').replace(r'\}', '}')

    # Find and replace patterns
    modified_lines = []
    tabularx_line = None

    for line in lines:
        # Check if the line matches the tabularx pattern
        if tabularx_pattern.match(line.strip()):
            # print(f'Hit {line.strip()}=')
            tabularx_line = unescape_latex(line.strip())
            modified_lines.append(f"% {line.strip()}\n")  # Comment out the original tabularx line
        elif line.strip().startswith(r'\begin{tabulary}') and tabularx_line:
            modified_lines.append(f"{tabularx_line}\n")
        elif line.strip().startswith(r'\end{tabulary}') and tabularx_line:
            modified_lines.append(r'\end{tabularx}'+'\n')
            tabularx_line = None
        else:
            if line.strip().startswith('latexcommand'):
                cmdline = unescape_latex(line.strip()[len('latexcommand'):])
                modified_lines.append(cmdline)
            else:    
                if len(line):
                    modified_lines.append(line)
            
    return '\n'.join(modified_lines)        




def replace_latex_admonition(content: str) -> str:
    r"""
    Replace LaTeX admonition with custom shadow box style.

    This function replaces:
    - \begin{sphinxadmonition}{note}{Box ...} ... \end{sphinxadmonition}
      with
      \begin{sphinxShadowBox}\sphinxstylesidebartitle{\sphinxstylestrong{Box ...} ... \end{sphinxShadowBox}

    Parameters:
    content (str): The LaTeX content to be modified.

    Returns:
    str: The modified LaTeX content with the replacements made.
    """
    # Define the regex pattern for the specific sphinxadmonition box
    pattern = re.compile(
        r"\\begin{sphinxadmonition}{note}{Box(.*?)}(.*?)\\end{sphinxadmonition}",
        re.DOTALL
    )

    # Define the replacement function
    def replacement(match):
        title = match.group(1)
        content = match.group(2)
        replaced = (
            "\\begin{sphinxShadowBox}"
            f"\\sphinxstylesidebartitle{{\\sphinxstylestrong{{Box{title}}}}}{content}"
            "\\end{sphinxShadowBox}"
        )
        return replaced

    # Perform the replacement
    content = pattern.sub(replacement, content)
    
    return content





# Example usage:
# update_toc_yaml('path/to/your/notebook.ipynb', 'path/to/toc.yml')

        
def latex_process(latexroot ):
    r"""
    Processes a LaTeX file generated by Sphinx to address common issues.

    This function takes the root name of a LaTeX file generated by Sphinx (`latexroot`) as input and performs the following actions:

    1. **Adds missing packages:** Checks if the `.tex` file includes the `makeidx` package, necessary for generating an index. If missing, it inserts the `\usepackage{makeidx}` line at the beginning.
    2. **Fixes index entries:** Removes unnecessary `\spxentry` commands from the `.idx` file, which can clutter the index.
    3. **Inserts missing elements:** Adds the following elements to the `.tex` file at specific locations:
        - `\usepackage{makeidx}` (if missing)
        - `\addcontentsline{toc}{chapter}{\indexname}` to include the "Index" entry in the table of contents
        - `{\huge\bfseries\raggedright Foreword\par}` to create a large, bold, right-aligned heading for the Foreword
        - `\renewcommand{\cleardoublepage}{\clearpage}` to avoid blank pages between chapters
        - `\newpage % taksigelse` (Danish for "acknowledgements") to start a new page for the acknowledgements section
    4. **Removes unwanted elements:** Removes the following elements from the `.tex` file:
        - All `\spxentry` commands
        - Chapters titled "Index" and "Reference" (including their labels)
        - Unnecessary Sphinx directives related to the index and reference chapters

    Args:
        latexroot (str): The root name of the LaTeX file (e.g., "book").

    Raises:
        IOError: If there are errors reading or writing the `.tex` file.

    """


    r'''It seems that the generated .tex file is missing a \usepackage{makeidx} 
    and that the .idx file contains a lot of unvanted \spxentry  so we fix these two problems 
    
    and more problems which makes it look not so nice
    ''' 
    
    latexfile =  f'{bookdir}/_build/latex/{latexroot}.tex'
    
    with open(latexfile,'rt',encoding="utf8") as f:
        latex= f.read()
        
    lf= '\n'
    
   # now a list of some text inserted at specific places in the .tex file
   # the place is defined by the first string in the tupple. 
    insertbefore = [
        (r'\makeindex',r'\usepackage{makeidx} '), 
        (r'\printindex',r'\addcontentsline{toc}{chapter}{\indexname}'),   # forgot the foreword heading, so it is inserted 
         (r'''\sphinxAtStartPar
Over the decades''',r'{\huge\bfseries\raggedright Foreword\par}'),
        (r'\title',r'\renewcommand{\cleardoublepage}{\clearpage}'),       # to avoid blank pages between chapters 

        (r"""\begin{DUlineblock}{0em}
\item[] \sphinxstylestrong{\Large Acknowledgements}
\end{DUlineblock}""",
         r"\newpage % taksigelse  ")]
    
    for before,insert in insertbefore: 
        if not insert in latex:
            latex = latex.replace(before,insert+lf+before)

    # Now some text to purge from the text  
  
    purge =[r'\spxentry',
            r'\chapter{Index}',
            r'\label{\detokenize{genindex:index}}\label{\detokenize{genindex::doc}}',
            r'\chapter{Reference}',
            r'\label{\detokenize{Reference:reference}}\label{\detokenize{Reference::doc}}',
            r'''\sphinxstepscope


\chapter{Index}
\label{\detokenize{genindex:index}}\label{\detokenize{genindex::doc}}
\sphinxstepscope

''',
r'''\sphinxstepscope




\sphinxstepscope''',
] 
    for p in purge:
       latex = latex.replace(p,'')
    
    # in the preamble 
    latex = latex.replace(r'\usepackage{geometry}',
    r'''\usepackage{geometry}
\usepackage {tabularx} 
\usepackage{afterpage} 
\usepackage{lscape}                        
''' )
    latex = replace_latex_citations(latex)
    latex = modify_latex_tabels(latex)
    latex = remove_selective_hlines_in_tabulary(latex)
    latex = replace_latex_admonition(latex)
    latex = modify_latex_tabularx(latex)
    latex = latex.replace(r'\sphinxAtStartPar',r'\par\sphinxAtStartPar')
    
    # breakpoint() 
    with open(latexfile,'wt',encoding="utf8") as f:
        f.write(latex) 


#%%    
def is_acrobat_running():
    import subprocess

    try:
        output = subprocess.check_output('tasklist', encoding='utf-8')
        # print(output)
        if 'AcroRd32.exe' in output:
            return True 

        return 'Acrobat.exe' in output
    except:
        return False
    

if 'latex-pdf' in options or 'pdf-latex' in options or 'latex' in options:
    
     while is_acrobat_running():
        input("Shut Acrobat before continuing. Once closed, press Enter to continue...")
    
        # Check again after the user has given input
        if is_acrobat_running():
            print("Acrobat is still running! Please close it.")
    
     if test:    
        copy(toctestloc,tocloc)
        
     try:
         xx0 = run(f'jb build {bookdir}/ --builder=latex')   
     except Exception as e:
         print(f'Error in call to jupyterbook latex {e} ')
     finally:     
         copy(toccopyloc,tocloc)
         
         
         
  
     latex_process(latexroot)

     # 
     # if the file is processed by miktex it works now, but due to a latexmk issue we use 
     # latexmk, then texindy to process it further and then latexmk to create the final pdf file  
     # 
     if not 'nopdf' in options: 
         if 0:
             
             xx0 = run(f'latexmk -pdf -dvi- -ps- -f {latexroot}.tex'      ,cwd = f'{bookdir}/_build/latex/')
             # xx0 = run(f'texindy    -o "{latexroot}.ind" "{latexroot}.idx"',cwd = f'{bookdir}/_build/latex/')
             xx0 = run(f'makeindex    -o "{latexroot}.ind" "{latexroot}.idx"',cwd = f'{bookdir}/_build/latex/')
             xx0 = run(f'latexmk -pdf -dvi- -ps- -f {latexroot}.tex'      ,cwd = f'{bookdir}/_build/latex/')
             
         else: 
             # First xelatex run
            xx0 = run(f'xelatex -interaction=batchmode -no-shell-escape "{latexroot}.tex"', cwd=f'{bookdir}/_build/latex/')
            
            # Run texindy to generate index
            # xx0 = run(f'texindy -o "{latexroot}.ind" "{latexroot}.idx"', cwd=f'{bookdir}/_build/latex/')
            xx0 = run(f'makeindex    -o "{latexroot}.ind" "{latexroot}.idx"',cwd = f'{bookdir}/_build/latex/')
            # Second xelatex run (to ensure all references are resolved)
            xx0 = run(f'xelatex -interaction=batchmode -no-shell-escape "{latexroot}.tex"', cwd=f'{bookdir}/_build/latex/')
            xx0 = run(f'xelatex -interaction=batchmode -no-shell-escape "{latexroot}.tex"', cwd=f'{bookdir}/_build/latex/')
         # #xx0 = run('latexmk -pdf -f MFModinModelflow.tex',cwd = f'{bookdir}/_build/latex/')
         print(f'PDF generated: see {bookdir}/_build/latex/')

def make_reflist(bookdir):
    toc_files  =  mu.get_toc_files(fileloc=bookdir)

    # reflist =  mu.search(toc_files,r"^\(([^)]+)\)=",notfound=False,silent=1,printmatch=0,showfiles=False,onlymarkdown=True,returnfound=True)
    reflist0 =  mu.search(toc_files,r"^\((.*?)\)=",notfound=False,silent=1,printmatch=0,showfiles=False,onlymarkdown=True,returnfound=True)
    reflist2 =  mu.search(toc_files,r":::\{index\} .+\n:name: *([^\s]+) *",notfound=False,silent=1,printmatch=0,showfiles=False,onlymarkdown=True,returnfound=True)
    
    out0 = '\n'.join([f'[{ref.replace("_"," ")}]({ref}) # nb =  {nb.stem}' for ref,nb in  reflist0])
    out1 = '\n'.join([f'[{ref.replace("_"," ")}]({ref}) # nb =  {nb.stem}' for ref,nb in  reflist2])
    out = f'Reference targets in {bookdir}\nFrom (xxx)=\n'+ out0+'\n\nAnd from index names \n' + out1
    outfile = Path(bookdir) / 'targets.txt'
    with open(outfile,'wt') as f: 
        f.write('References in this jupyter book\n'+out)

    return 

make_reflist(bookdir)

if 'make_zip' in options:
    mu.make_replication()
     
if 'copy' in options:
    try:
        (destination := Path(fr'C:/modelbook/IbHansen.github.io/{bookdir}')).mkdir(parents=True, exist_ok=True)
    except:
        print('you are probably not Ib, so this is impossible')
    else:     
        copytree(buildhtml,destination,dirs_exist_ok=True )
        print('Remember to push the repo ')

if 'copyibtest' in options:
    try:
        (destination := Path(r'C:/modelbook/IbHansen.github.io/MFMod-ModelFlow')).mkdir(parents=True, exist_ok=True)
        (destinationjn := Path(r'C:/modelbook/IbHansen.github.io/MFMod-ModelFlow/jn')).mkdir(parents=True, exist_ok=True)
    except:
        print('you are probably not Ib, so this is impossible')
    else:     
        copytree(buildhtml,destination,dirs_exist_ok=True )
        mu.make_replication(zip=False,destinationdir=destinationjn)
        print('Remember to push the repo ')
        
if 'copywb' in options:
    try:
        (destination := Path(fr'{bookdir}/_to_publication/')).mkdir(parents=True, exist_ok=True)
        (destinationjn := Path(fr'{bookdir}/_to_publication/jn')).mkdir(parents=True, exist_ok=True)
    except:
        print('you are probably not Ib, so this is impossible')
    else:     
        copytree(buildhtml,destination,dirs_exist_ok=True )
        mu.make_replication(zip=False,destinationdir=destinationjn)
        print('Remember to push the repo ')
    