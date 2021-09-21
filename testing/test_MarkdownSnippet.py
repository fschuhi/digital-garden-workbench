#!/usr/bin/env python3

from util import convertMatchedObsidianLink, loadStringFromTextFile, saveLinesToTextFile, saveStringToTextFile, searchObsidianLink
from HAFEnvironment import HAFEnvironment
from MarkdownSnippet import MarkdownSnippet
from consts import HAF_YAML, HAF_YAML_TESTING
import unittest

import filecmp

# *********************************************
# MarkdownSnippet
# *********************************************

class Test_MarkdownSnippet(unittest.TestCase):


    def test_searchMarkupLink(self):
        match = searchObsidianLink("asdf [[Link1]] wert und [[weiterer Link]]")
        self.assertEqual(match.group('note'), "Link1")

        match = searchObsidianLink("ein [[Link2#header]] und [[weiterer Link]]")
        self.assertEqual(match.group('note'), "Link2")
        self.assertEqual(match.group('header'), "header")

        match = searchObsidianLink("ein [[Link3#header|bla]] und [[weiterer Link]]")
        self.assertEqual(match.group('note'), "Link3")
        self.assertEqual(match.group('header'), "header")
        self.assertEqual(match.group('shown'), "bla")

        match = searchObsidianLink("ein [[Link4#^reier|reier]] und [[weiterer Link]]")
        self.assertEqual(match.group('note'), "Link4")
        self.assertEqual(match.group('blockid'), "reier")
        self.assertEqual(match.group('shown'), "reier")


    def test_collectLinkMatches(self):
        ms = MarkdownSnippet("Das ist ein [[Link]] und noch ein [[Link]] das war es.")
        spans = [m.span() for m in ms.collectLinkMatches()]
        self.assertListEqual(spans, [(12,20), (34,42)])


    def test_collectLinkSpans(self):
        ms = MarkdownSnippet("Das ist ein [[Link]] und noch ein [[Link]] das war es.")
        spans = ms.collectLinkSpans()
        self.assertListEqual(spans, [(12,20), (34,42)])


    def test_removeFootnotes(self):
        originalText = "Das ist ein [[Link]] und noch ein [[Link]] das war es."
        ms = MarkdownSnippet(originalText)
        ms.removeFootnotes()
        self.assertEquals(ms.text, originalText)
        self.assertEqual(ms.footnotes, [])

        ms = MarkdownSnippet("Das ist ein [[Link]] hier^[ist eine Footnote] noch ein [[Link]] das war es.")
        ms.removeFootnotes()
        self.assertEqual(ms.text, "Das ist ein [[Link]] hier noch ein [[Link]] das war es.")
        self.assertEqual(ms.footnotes, [('^[ist eine Footnote]', 25)])


    def test_removeAllLinks(self):
        originalText = "Das ist ein [[Link]] hier^[ist eine Footnote] noch ein [[Link]] das war es."

        ms = MarkdownSnippet(originalText)
        ms.removeAllLinks()
        self.assertEqual(ms.text, "Das ist ein Link hier^[ist eine Footnote] noch ein Link das war es.")

        ms = MarkdownSnippet(originalText)
        ms.removeFootnotes()
        self.assertEqual(ms.footnotes, [('^[ist eine Footnote]', 25)])
        ms.removeAllLinks()
        self.assertEqual(ms.text, "Das ist ein Link hier noch ein Link das war es.")
        self.assertEqual(ms.footnotes, [('^[ist eine Footnote]', 21)])

        ms.restoreFootnotes()
        self.assertEqual(ms.text, "Das ist ein Link hier^[ist eine Footnote] noch ein Link das war es.")


    def test_cutSpanWithoutFootnotes(self):
        ms = MarkdownSnippet("Das ist ein [[Link1]] und noch ein [[Link2]] das war es.")
        spans = ms.collectLinkSpans()
        self.assertListEqual(spans, [(12,21), (35,44)])

        match = ms.searchMarkupLink()
        self.assertIsNotNone(match)
        cutText1 = ms.cutSpan(match.span())
        self.assertEqual(cutText1, "[[Link1]]")
        self.assertEqual(ms.text, "Das ist ein  und noch ein [[Link2]] das war es.")

        match = ms.searchMarkupLink()
        self.assertIsNotNone(match)
        cutText2 = ms.cutSpan(match.span())
        self.assertEqual(cutText2, "[[Link2]]")
        self.assertEqual(ms.text, "Das ist ein  und noch ein  das war es.")


    def test_cutSpanWithFootnotes(self):
        originalText = "Das ist ein [[Link1]] hier^[ist eine Footnote] noch ein [[Link2]] das war es."
        ms = MarkdownSnippet(originalText)
        ms.removeFootnotes()
        self.assertEqual(ms.text, "Das ist ein [[Link1]] hier noch ein [[Link2]] das war es.")
        self.assertEqual(ms.footnotes, [('^[ist eine Footnote]', 26)])

        cutText1 = ms.cutSpan(ms.searchMarkupLink().span())
        cutText2 = ms.cutSpan(ms.searchMarkupLink().span())
        self.assertEqual(ms.text, "Das ist ein  hier noch ein  das war es.")

        ms.restoreFootnotes()
        self.assertEqual(ms.text, "Das ist ein  hier^[ist eine Footnote] noch ein  das war es.")


    def test_replaceLinksWithoutFootnote(self):
        ms = MarkdownSnippet("Das ist ein [[Link1]][[Link2]] das war es.")
        ms.replaceLinks(lambda match: f"/{match.group('complete')}/")
        self.assertEqual(ms.text, "Das ist ein /Link1//Link2/ das war es.")


    def test_replaceLinksWithFootnote(self):
        root = "https://publish.obsidian.md/rob-burbea/"

        ms = MarkdownSnippet("Das ist ein [[Link1]] hier^[ist eine Footnote] noch ein [[Link2]] das war es.")
        ms.replaceLinks(lambda match: f"/{match.group('note')}/")
        self.assertEqual(ms.text, "Das ist ein /Link1/ hier^[ist eine Footnote] noch ein /Link2/ das war es.")

        haf = HAFEnvironment(HAF_YAML)
        links = []
        ms = MarkdownSnippet("Das ist ein [[0301 Preliminaries Regarding Voice, Movement, and Gesture - Part 1#^1-1|1-1]] hier^[ist eine Footnote] Link.")
        ms.replaceLinks(lambda match: f"{convertMatchedObsidianLink(match, root)}")
        links.append(ms.text)

        ms = MarkdownSnippet("[[Digital Gardens#Shannon]]")
        ms.replaceLinks(lambda match: f"{convertMatchedObsidianLink(match, root)}")
        links.append(ms.text)

        ms = MarkdownSnippet("[[Digital Gardens#Magic Dust]]")
        ms.replaceLinks(lambda match: f"{convertMatchedObsidianLink(match, root)}")
        links.append(ms.text)

        saveLinesToTextFile("tmp/ms.txt", links)
        self.assertTrue(filecmp.cmp("tmp/ms.txt", "testing/data/Test_MarkdownSnippet.test_replaceLinksWithFootnote.txt"))


    def test_convertMatchedObsidianLink(self):
        text = loadStringFromTextFile("testing/data/Test_MarkdownSnippet.test_convertMatchedObsidianLink.md")
        ms = MarkdownSnippet(text)
        root = "https://publish.obsidian.md/rob-burbea/"
        ms.replaceLinks(lambda match: f"{convertMatchedObsidianLink(match, root)}")
        saveStringToTextFile("tmp/tmp.md", ms.text)
        self.assertTrue(filecmp.cmp("tmp/tmp.md", "testing/data/Test_MarkdownSnippet.test_convertMatchedObsidianLink_converted.md"))


    def test_replaceLinksInOneTranscript(self):
        haf = HAFEnvironment(HAF_YAML_TESTING)
        talkName = "0301 Preliminaries Regarding Voice, Movement, and Gesture - Part 1"        
        sfnTranscriptMd = haf.getTranscriptFilename(talkName)
        text = loadStringFromTextFile(sfnTranscriptMd)
        ms = MarkdownSnippet(text)
        root = "https://publish.obsidian.md/rob-burbea/"
        ms.replaceLinks(lambda match: f"{convertMatchedObsidianLink(match, root)}")
        saveStringToTextFile("tmp/tmp.md", ms.text)
        self.assertTrue(filecmp.cmp("tmp/tmp.md", "testing/data/Test_MarkdownSnippet.test_replaceLinksInOneTranscript.md"))


if __name__ == "__main__":
    unittest.main()