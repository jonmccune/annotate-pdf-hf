#!/usr/bin/python

# For 2.3 <= python < 2.7:
#   sudo aptitude install python-pip
#   sudo pip install argparse

###
# Goal: Easily stick our own headers and footers on top of an existing
# PDF document.  Originally conceived to make it easier to bulk print
# papers for reviewing while keeping track of meta-information such as
# the paper's "number" in the reviewing system.
###

import os
import argparse
import tempfile
from subprocess import call
import shutil
from socket import gethostname

# Annoyingly doubling up all the backslashes in this:
LaTeXtemplate = """
\\documentclass[8pt]{article}
% Use tiny margins; we want our annotations way out of the way
\\usepackage[top=1in,bottom=1in,left=.75in,right=.75in]{geometry}
% Get precise control over headers and footers
\\usepackage{fancyhdr}
% Be able to include somebody else's PDF file
\\usepackage{pdfpages}
\\begin{document}
\\pagestyle{fancy}
\\includepdf[pages=-,pagecommand={\\lfoot{LeftFooter}\\rfoot{RightFooter}\\lhead{LeftHeader}\\rhead{RightHeader}\\chead{CenterHeader}\\thispagestyle{fancy}}]{InFile}
\\end{document}
"""

# Steps:
## 0. parse args
parser = argparse.ArgumentParser(description='Magic header/footer annotation inserter')
parser.add_argument('-i','--infile', help='Input PDF File', required=True)
parser.add_argument('-l','--lhead',  help='Left Header',    required=False) # No default intentionally
parser.add_argument('-c','--chead',  help='Center Header',  required=False, default='Hostname: '+gethostname())
parser.add_argument('-r','--rhead',  help='Right Header',   required=False, default='Generated: \\today')
parser.add_argument('-f','--lfoot',  help='Left Footer',    required=False, default="")
parser.add_argument('-o','--rfoot',  help='Right Footer',   required=False, default="")
args = vars(parser.parse_args())

# Populate template variables that we are guaranteed to have
infile = args['infile'].replace('.pdf', '')

# lhead is special since we use a different argument's value if
# nothing is provided as input
lhead = args['lhead'] or infile

## 1. mk temp dir
temp_dir = tempfile.mkdtemp()
print "Intermediate results in directory: " + temp_dir + "\n"

## 2. substitute arguments into .tex working file
LaTeXtemplate = LaTeXtemplate.replace('InFile', os.getcwd()+'/'+infile).replace('LeftHeader', lhead).replace('CenterHeader', args['chead']).replace('RightHeader', args['rhead']).replace('LeftFooter', args['lfoot']).replace('RightFooter', args['rfoot'])

print LaTeXtemplate

## 3. write .tex template into temp dir
tex_file = temp_dir + '/' + infile + '-annotated.tex'
print "TeX file: " + tex_file + "\n"
FILE = open(tex_file,"w")
FILE.writelines(LaTeXtemplate)
FILE.close()

## 4. build with pdflatex
oldcwd = os.getcwd()
os.chdir(temp_dir)
call(['pdflatex', tex_file])

## 5. copy result
os.chdir(oldcwd)
shutil.copy(temp_dir + '/' + infile + '-annotated.pdf', '.')

## 6. wipe out temp junk
shutil.rmtree(temp_dir)

