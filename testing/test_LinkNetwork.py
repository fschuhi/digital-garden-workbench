#!/usr/bin/env python3

from util import matchedObsidianLinkToString, saveStringToTextFile
from LinkNetwork import LinkNetwork
from igraph import Graph
from HAFEnvironment import HAFEnvironment
from TranscriptIndex import TranscriptIndex
from TranscriptModel import TranscriptModel
from TranscriptPage import TranscriptPage
from testing import MyTestClass
from consts import HAF_YAML, RB_YAML, VAJRA_MUSIC
import unittest
import os
import re
from igraph import *

# *********************************************
# network
# *********************************************

class Test_LinkNetwork(MyTestClass):

    @classmethod
    def setUpClass(cls) -> None:
        cls.haf = HAFEnvironment(HAF_YAML)
        cls.transcriptIndex = TranscriptIndex(RB_YAML)
        # cls.transcriptModel = TranscriptModel(cls.transcriptIndex)        
        return super().setUpClass()


    def test_1(self):
        network = LinkNetwork(self.haf)
        matches = network.collectReferencedNoteMatches('Brahmavihāras')
        for note, match in matches:
            print(note)
            print('  ' + matchedObsidianLinkToString(match))
            retainShown = note != 'Index'
            print('  ' + matchedObsidianLinkToString(match, 'Brahmaviharas', retainShown))


    def test_2(self):
        network = LinkNetwork(self.haf)
        linkingNotes = network.getBacklinksByNote('Brahmavihāras')
        for linkingNote in linkingNotes:
            print(linkingNote)
            matches = network.getLinkMatchesByNote(linkingNote, 'Brahmavihāras')
            for match in matches:
                print('  ' + matchedObsidianLinkToString(match))
                retainShown = linkingNote != 'index'
                print('  ' + matchedObsidianLinkToString(match, 'Brahmaviharas', retainShown))


    def test_3(self):
        network = LinkNetwork(self.haf)
        oldNote = 'Sīla'
        newNote = 'Sila'
        linkingNotes = network.getBacklinksByNote(oldNote)
        for linkingNote in linkingNotes:
            markdown = network.getMarkdownSnippetByNote(linkingNote)
            oldText = markdown.text
            matches = network.getLinkMatchesByNote(linkingNote, oldNote)
            retainShown = linkingNote != 'index'
            markdown.replaceMatches(matches, lambda match: matchedObsidianLinkToString(match, newNote, retainShown))
            newText = markdown.text
            if newText != oldText:
                sfn = os.path.join("tmp", os.path.basename(network.getFilenameByNote(linkingNote)))
                #sfn = network.getFilenameByNote(linkingNote)
                saveStringToTextFile(sfn, newText)


    def test_pydot(self):
        # we'll probably not use pydot but rather go for igraph
        return
        
        import pydot

        graph = pydot.Dot("my_graph", graph_type="graph", overlap="scale", sep="-0.7")

        import time
        tic = time.perf_counter()
        transcriptFilenames = self.haf.collectTranscriptFilenames(VAJRA_MUSIC)
        for filename in transcriptFilenames:
            termCounts = dict()
            page = TranscriptPage.fromTranscriptFilename(filename)
            page.applySpacy(self.transcriptModel)
            for paragraph in page.paragraphs:
                for k, v in paragraph.termCounts.items():
                    match = re.match("^([^#]+)", k)
                    pageName = match.group(1)
                    if pageName in termCounts:
                        termCounts[pageName] += 1
                    else:
                        termCounts[pageName] = 1
            for k,v in termCounts.items():
                #print(k, v)
                graph.add_edge(pydot.Edge(os.path.basename(filename), k, color="blue"))

        graph.write_svg("tmp/output.svg", encoding="utf-8", prog='fdp')
        toc = time.perf_counter()
        print(f"total time: {toc - tic:0.4f} seconds")


    def test_igraph(self):
        # 20.09.21 currently not researching this way to display connection graphs
        # might be necessary lateron, when the Obsidian-internal display is not coping anymore
        # probably also necessary if Obsidian Publish sticks with its local-graph-only strategy, in this case igraph can come to rescue

        # https://stackoverflow.com/questions/36200707/error-with-igraph-library-deprecated-library
        # pip install python-igraph
        # pip install cairocffi
        
        # https://towardsdatascience.com/newbies-guide-to-python-igraph-4e51689c35b4
        # Create a directed graph
        g = Graph(directed=True)
        # Add 5 vertices
        g.add_vertices(5)

        # Add ids and labels to vertices
        for i in range(len(g.vs)):
            g.vs[i]["id"]= i
            g.vs[i]["label"]= str(i)
        # Add edges
        g.add_edges([(0,2),(0,1),(0,3),(1,2),(1,3),(2,4),(3,4)])
        # Add weights and edge labels
        weights = [8,6,3,5,6,4,9]
        g.es['weight'] = weights
        g.es['label'] = weights

        visual_style = {}
        out_name = "tmp/graph.png"
        # Set bbox and margin
        visual_style["bbox"] = (400,400)
        visual_style["margin"] = 27
        # Set vertex colours
        visual_style["vertex_color"] = 'white'
        # Set vertex size
        visual_style["vertex_size"] = 45
        # Set vertex lable size
        visual_style["vertex_label_size"] = 22
        # Don't curve the edges
        visual_style["edge_curved"] = False
        # Set the layout
        my_layout = g.layout_lgl()
        visual_style["layout"] = my_layout
        # Plot the graph

        # either save to file or show immediately via cairocffi in irfanviews
        #plot(g, out_name, **visual_style)
        #plot(g, **visual_style)
        

if __name__ == "__main__":
    unittest.main()