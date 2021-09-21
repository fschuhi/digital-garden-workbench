#!/usr/bin/env python3

import os
import re
import yaml

def filterExt(filenames: list[str], targetExt):
    targetExt = targetExt if targetExt.startswith('.') else '.' + targetExt
    filteredFilenames = []
    for filename in filenames:
        (filenameWithoutExt, ext) = os.path.splitext(filename)
        if ext == targetExt:
            filteredFilenames.append(filename)
    return filteredFilenames


# *********************************************
# shared types
# *********************************************

from typing import Tuple
TFootnote = Tuple[str, int]
TFootnotes = list[TFootnote]


# *********************************************
# deitalizise
# *********************************************

def deitaliziseWithReplace(text: str, term: str) -> str:
    text = text.replace('_' + term + '_', term)
    text = text.replace('_' + term + ',_', term + ',')
    text = text.replace('_' + term + '._', term + '.')
    text = text.replace('_' + term.capitalize() + '_', term.capitalize())
    text = text.replace('_' + term.capitalize() + ',_', term.capitalize() + ',')
    text = text.replace('_' + term.capitalize() + '._', term.capitalize() + '.')
    return text

def deitaliziseTerm(text: str, term: str) -> str:
    seps = '[,.:;– )’!-]*?'
    text = re.sub(f"_({term})({seps})_", "\\1\\2", text)
    capitalized = term.capitalize()
    text = re.sub(f"_({capitalized})({seps})_", "\\1\\2", text)
    text = re.sub(f"_({capitalized[0]})_+({capitalized[1:]})({seps})_", "\\1\\2\\3", text)
    return text

def deitaliziseTerms(text: str, terms: list[str]) -> str:
    for term in terms:
        text = deitaliziseTerm(text, term)
    return text

def deitalizeTermsWithDiacritics(text: str) -> str:
    return deitaliziseTerms(text, ['jhāna', 'jhānas', 'mudrā', 'mudrās', 'anattā', 'brahmavihāra', 'brahmavihāras', 'muditā', 'upekkhā', \
        'mettā', 'samādhi', 'karuṇā', 'samatha', 'dharma', 'dharmas', 'pīti'] )


# *********************************************
# save/load text files
# *********************************************

def loadStringFromTextFile(sfn) -> str:
    with open(sfn, 'r', encoding='utf-8') as f:
        text = f.read()
        f.close
    return text


def loadLinesFromTextFile(sfn) -> list[str]:
    return loadStringFromTextFile(sfn).splitlines()


def saveStringToTextFile(sfn, text: str):
    with open(sfn, 'w', encoding='utf-8', newline='\n') as f:
        print(text, file=f, end='')
        f.close()


def saveLinesToTextFile(sfn, lines: list[str]):
    with open(sfn, 'w', encoding='utf-8', newline='\n') as f:
        #f.writelines(lines)
        for line in lines:
            print(line, file=f)
        f.close()



# *********************************************
# file system
# *********************************************

def baseNameWithoutExt(sfn):
    return os.path.splitext(os.path.basename(sfn))[0]


def collectFilenames(dir) -> list[str]:
    filenames = []
    for entry in os.scandir(dir):
        if os.path.isfile(entry):
            filenames.append(entry.path)
    return filenames


# *********************************************
# yaml
# *********************************************

def loadYaml(sfnHAFYaml) -> dict[str,str]:
    dict = {}
    with open(sfnHAFYaml, 'r', encoding='utf-8', newline='\n') as stream:
        dict = yaml.load(stream, Loader=yaml.FullLoader)
        stream.close()
    return dict


def extractYaml(lines: list[str]) -> dict[str,str]:
    yamlLines = []
    if lines[0] != '---':
        return None
    for line in lines[1:]:
        if line == '---':
            break
        yamlLines.append(line)
    from io import StringIO
    file_like_io = StringIO('\n'.join(yamlLines))
    import yaml
    dictYaml = yaml.load(file_like_io, Loader=yaml.FullLoader)
    return dictYaml
    

# *********************************************
# regex
# *********************************************

def setMatchField(obj, fieldName, match: re.match, func = None):
    m = match.group(fieldName)
    value = None if m is None else (m if func is None else func(m))
    setattr(obj, fieldName, value if value else None)


# *********************************************
# GUI
# *********************************************

import tkinter
from tkinter import messagebox

def showMessageBox(theMessage, theTitle=None):
    # https://stackoverflow.com/questions/2963263/how-can-i-create-a-simple-message-box-in-python
    window = tkinter.Tk()
    window.wm_withdraw()
    messagebox.showinfo(title=theTitle if theTitle else "showMessageBox", message=theMessage)

def askYesNoCancel(theMessage, theTitle=None):
    window = tkinter.Tk()
    window.wm_withdraw()
    return messagebox.askyesnocancel(title=theTitle if theTitle else "askYesNoCancel", message=theMessage)

def askRUN():
    global askRUN
    if askRUN is None:
        askRUN = True
    if not askRUN:
        return None
    res = askYesNoCancel("RUN  " + thisFunctionName(1) + " ?", "RUN")
    askRUN = res is not None
    return res

# *********************************************
# reflection
# *********************************************

def thisFunctionName(stackLevel: int = 0):
    # https://stackoverflow.com/questions/5067604/determine-function-name-from-within-that-function-without-using-traceback
    import inspect
    return inspect.stack()[1][3] if stackLevel == 0 else inspect.stack()[1+stackLevel][3]


# *********************************************
# canonicalize
# *********************************************

def canonicalizeText(text) -> str:
    text = text.replace('\n', ' ')            
    text = text.rstrip()
    text = re.sub("  +", " ", text )
    text = re.sub("[“”“]", '"', text)
    text = re.sub("[‘’]", '\'', text)    
    text = re.sub("[–-]+","-", text)
    text = re.sub("([^ ])- ([^ ])", "\\1-\\2", text)
    text = re.sub("\.\.\.", "... ", text)
    text = re.sub("([^ ]) ,([^ ])", "\\1, \\2", text)
    text = re.sub("^[0-9]+ ", "", text)
    text = re.sub(" [0-9]+ ", "", text)
    return text


def decontractText(text) -> str:
    text = re.sub("I['’]m", "I am", text )
    text = re.sub("(I|you|You|We|we|They|they)['’]ve", "\\1 have", text )
    text = re.sub("(I|you|You|We|we|They|they)['’]ll", "\\1 will", text )
    text = re.sub("(What|what|It|it|There|there|That|that|She|He|s?he|Who|who|When|when|Here|here|[Ee]verything|cat)['’]s", "\\1 is", text )
    text = re.sub("(Let|let)['’]s", "\\1 us", text )
    text = re.sub("(You|you|We|we|They|they)['’]re", "\\1 are", text )
    text = re.sub("(You|you|We|we|They|they)['’]d", "\\1 would", text )
    text = re.sub("(Do|do|Does|does|Is|is|Have|have|Did|did|Would|would|Should|should|Could|could|Was|was)n['’]t", "\\1 not", text )
    text = re.sub("([Cc])an['’]t", "\\1an not", text)
    text = re.sub("([Ww])on['’]t", "\\1ill not", text)
    return text


def forceLFOnly(dir):
    for filename in collectFilenames(dir):
        lines = loadLinesFromTextFile(filename)
        saveLinesToTextFile(filename, lines)


# *********************************************
# Obsidian links
# *********************************************

# complete: link w/o [[ and ]]
#    link: note or note+target
#       note: md file (actually case insensitive)
#       target: either "#header" or "#^1-1"
#          header: #header
#          blockid: 1-1
#    shown: part of Obsidian link after |

ObsidianLinkPattern = r"\[\[(?P<complete>(?P<link>(?P<note>[^#\]|]+)(?P<target>#((\^(?P<blockid>[^\]|]+))|(?P<header>[^\]|]+)))?)(\|(?P<shown>.+?))?)\]\]"


def searchObsidianLink(text) -> re.Match:
    return re.search(ObsidianLinkPattern, text)


def matchedObsidianLinkToString(match: re.Match, newNote: str=None, retainShown: bool=True) -> str:
    # IMPORTANT: passing newNote might not only convert the link back to the original string but also does some replacement

    note = match.group('note')
    usedNote = newNote if (newNote and newNote.lower() != note.lower()) else note
    s = '[[' + usedNote

    target = match.group('target')
    if target:
        s += target

    shown = match.group('shown')
    if shown:
        if shown != usedNote:
            s += '|' + shown
    else:
        # IMPORTANT: We cannot just replace the originally referenced note (which is backed by an md file) w/ a new note, at least not in all situations.
        # Say, the original link was [[some link]] w/ the page "Some Link.md". That works because Obisidian note references are case-insensitive.
        # In this case we need to still show _some link_ in the preview, so the original needs to be swapped into the "shown" part.
        # Trivially, if we already have a shown part then we can simply replace the old note w/ the new one.
        if newNote and retainShown and newNote.lower() != note.lower():
            s += '|' + note

    return s + ']]'


def convertMatchedObsidianLink(match, root, filter=None):

    # print(match.group(0))

    if filter and not filter(match):
        return match.group(0)

    # print("aaaaaaaaaaaaaaaa")

    import urllib.parse
    link = match.group('link')
    note = match.group('note')
    target = match.group('target')
    header = match.group('header')
    shownLink = match.group('shown')

    encodedNote = urllib.parse.quote_plus(note)

    if not target:
        encodedTarget = ''
    elif target.startswith('#^'):
        encodedTarget = '#^' + urllib.parse.quote_plus(target[2:])
        shownLink = shownLink if shownLink else note
    elif target.startswith('#'):
        encodedTarget = '#' + urllib.parse.quote_plus(target[1:])
        shownLink = shownLink if shownLink else f"{note} > {header}"
    else:
        assert False
    
    if not shownLink:
        shownLink = note

    from html import escape
    shownLink = escape(shownLink)

    # h.obsidian.md/rob-burbea/2020+Vajra+Music/Transcript+pages/0301+Preliminaries+Regarding+Voice%2C+Movement%2C+and+Gesture+-+Part+1#^1-1
    return f'<a data-href="{link}" href="{root}{encodedNote}{encodedTarget}" class="internal-link" target="_blank" rel="noopener">{shownLink}</a>'
