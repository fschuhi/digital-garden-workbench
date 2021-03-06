#!/usr/bin/env python3

import os
import yaml
from util import *
from MarkdownLine import MarkdownLine, MarkdownLines
from util import *


from enum import Enum
class ObsidianNoteType(Enum):
    UNKNOWN = 0
    TRANSCRIPT = 1
    TALK = 2
    INDEX_ENTRY = 3
    INDEX = 4


class MyDumper(yaml.Dumper):

    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)


# *********************************************
# class ObsidianNote
# *********************************************

class ObsidianNote:
    def __init__(self, type: ObsidianNoteType, path):
        self.type = type # type: ObsidianNoteType

        self.path = path        
        self.basename = os.path.basename(path)
        self.basenameWithoutExt = os.path.splitext(os.path.basename(path))[0]
        self.notename = basenameWithoutExt(self.basenameWithoutExt)

        textLines = loadLinesFromTextFile(path)

        self.markdownLines = None # type: MarkdownLines

        # IMPORTANT: frontmatter is *not* markdown
        self.yaml = extractYaml(textLines)
        if self.yaml:
            skipAtBeginning = len(loadFrontmatter(textLines)) + 2
            textLines = [line for index, line in enumerate(textLines) if index >= skipAtBeginning]

        self.assignTextLines(textLines)


    @property
    def text(self):
        return self.markdownLines.asText()

    @text.setter
    def text(self, text):
        self.markdownLines = MarkdownLines.fromText(text)


    def getYamlValue(self, key: str) -> str:
        if self.yaml and (key in self.yaml):
            return self.yaml[key]

    def collectTextLines(self) -> list[str]:
        return self.markdownLines.collectTextLines()
    
    def assignTextLines(self, textLines: list[str]):
        self.markdownLines = MarkdownLines(textLines)


    def collectMarkdownLines(self) -> MarkdownLines:
        return MarkdownLines.fromText(self.text)

    def assignMarkdownLines(self, markdownLines: MarkdownLines):
        self.text = markdownLines.asText()


    def determineTags(self) -> list[str]:        
        tags = []
        for ml in self.markdownLines:
            if re.match("^ *#[A-Za-z]+", ml.text):
                tagsInLine = [x.strip(' ') for x in ml.text[1:].split('#')]
                tags.extend(tagsInLine)
        return tags

    def generateYamlLines(self):
        lines = []
        if self.yaml:
            lines.append("---")
            # https://stackoverflow.com/questions/25108581/python-yaml-dump-bad-indentation
            # added indent=3
            lines.extend(yaml.dump(self.yaml, Dumper=MyDumper, default_flow_style=False, indent=3).splitlines())            
            lines.append("---")        
        return lines

    def save(self, path=None):
        if path is None: path = self.path
        out = []

        out.extend(self.generateYamlLines())

        markdownTextLines = self.markdownLines.collectTextLines()
        out.extend(markdownTextLines)
        saveLinesToTextFile(path, out)


if __name__ == "__main__":
    pass
