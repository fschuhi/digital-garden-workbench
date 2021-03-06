#!/usr/bin/env python3

from MarkdownLine import SpacyMode
from TranscriptPage import TranscriptPage
from HAFEnvironment import HAFEnvironment, determineTalkname
from TranscriptIndex import TranscriptIndex
from TranscriptModel import TranscriptModel
from TalkPage import TalkPage, createNewTalkPage
from consts import HAF_YAML_TESTING, RB_YAML_TESTING
import unittest
import filecmp


# *********************************************
# Talk
# *********************************************

class Test_TalkPage(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.haf = HAFEnvironment(HAF_YAML_TESTING)
        cls.transcriptIndex = TranscriptIndex(RB_YAML_TESTING)
        cls.transcriptModel = TranscriptModel(cls.transcriptIndex)        
        return super().setUpClass()

    transcriptName = "0301 Preliminaries Regarding Voice, Movement, and Gesture - Part 1"

    def test_updateWithOldTargetType(self):
        sfnTranscriptMd = self.haf.getTranscriptFilename(self.transcriptName)
        transcriptPage = TranscriptPage(sfnTranscriptMd)
        transcriptPage.applySpacy(self.transcriptModel, mode=SpacyMode.ONLY_FIRST, force=False)
    
        fnTalk = self.haf.getTalkFilename(self.transcriptName)
        talk = TalkPage(fnTalk)
    
        talk.update(transcriptPage, targetType='#^')
        talk.save("tmp/tmp.md")
        self.assertTrue(filecmp.cmp("tmp/tmp.md", fnTalk))
        self.assertTrue(filecmp.cmp("tmp/tmp.md", "testing/data/Test_TalkPage.test_updateWithOldTargetType.md"))


    def test_updateWithNewTargetType(self):
        sfnTranscriptMd = self.haf.getTranscriptFilename(self.transcriptName)
        transcriptPage = TranscriptPage(sfnTranscriptMd)
        transcriptPage.applySpacy(self.transcriptModel, mode=SpacyMode.ONLY_FIRST, force=False)
    
        fnTalk = self.haf.getTalkFilename(self.transcriptName)
        talk = TalkPage(fnTalk)
    
        talk.update(transcriptPage, targetType='#')
        talk.save("tmp/tmp.md")
        self.assertTrue(filecmp.cmp("tmp/tmp.md", "testing/data/Test_TalkPage.test_updateWithNewTargetType.md"))


    def test_createNew(self):
        talkName = determineTalkname(self.transcriptName)
        createNewTalkPage(talkName, self.haf, self.transcriptModel, "tmp/tmp.md")
        self.assertTrue(filecmp.cmp("tmp/tmp.md", "testing/data/Test_TalkPage.test_createNew.md"))


    def test_collectMissingParagraphHeaderTexts(self):
        talkName = "From Insight to Love"
        fnTalk = self.haf.getTalkFilename(talkName)
        talk = TalkPage(fnTalk)
        self.assertEqual(talk.collectMissingParagraphHeaderTexts(), 2)


if __name__ == "__main__":
    unittest.main()
