#!/usr/bin/env python3

import unittest
from HAFEnvironment import HAFEnvironment
from ObsidianNote import ObsidianNoteType, ObsidianNote
from consts import HAF_YAML
from MarkdownSnippet import MarkdownSnippet

# *********************************************
# Publishing
# *********************************************

class Test_ObsidianNote(unittest.TestCase):

    haf = HAFEnvironment(HAF_YAML)

    def createNote(self, talkName):
        md = self.haf.getSummaryFilename(talkName)
        return ObsidianNote.fromFile(ObsidianNoteType.SUMMMARY, md)


    def test_yaml(self):
        note = self.createNote("Samadhi in Metta Practice")

        yaml = note.collectYaml()
        self.assertDictEqual(yaml, {'obsidianUIMode': 'preview'})
        
        yaml['bla'] = 'heul'
        self.assertDictEqual(yaml, {'bla': 'heul', 'obsidianUIMode': 'preview'})
        note.assignYaml(yaml)
        yaml = note.collectYaml()
        self.assertDictEqual(yaml, {'bla': 'heul', 'obsidianUIMode': 'preview'})


    def test_changeLine(self):
        note = self.createNote("Samadhi in Metta Practice")

        lines = note.collectLines()
        lines[4] = "asdfasdf"
        note.assignLines(lines)

        lines = note.collectLines()
        self.assertEqual(lines[4], "asdfasdf")


    def test_markdownSnippets(self):
        note = self.createNote("Samadhi in Metta Practice")

        snippets = note.collectMarkdownSnippets()

        assert snippets.asText() == note.text

        res = snippets.searchSection("^#+ Index", "^#+ Paragraphs")
        assert res is not None
        (start, end, matchFrom, matchTo) = res
        self.assertEqual(matchFrom.group(0), "## Index")
        self.assertEqual(matchTo.group(0), "## Paragraphs")

        matchedSnippets = snippets[start:end]
        self.assertEqual(matchedSnippets[0].text, "## Index")
        self.assertNotEqual(matchedSnippets[-1].text, "## Paragraphs")

        (start, end, matchFrom, matchTo) = snippets.searchSection("^#+ asdf", "^#+ wert")
        self.assertIsNone(start)



if __name__ == "__main__":
    unittest.main()