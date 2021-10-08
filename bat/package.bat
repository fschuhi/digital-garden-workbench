@echo off
echo.
set /p doit=do it?
if not "%doit%"=="do it" (
   echo aborted
   goto :EOF
)
echo .

python transcripts.py --script reindexTranscripts
echo .

python summaries.py --script updateSummary
echo .

python summaries.py --script updateParagraphsLists
echo .

python index.py --script topTalks
echo .

python index.py --script topParagraphs
echo .

python HAFScripts.py --script transferFilesToPublish
echo .

echo.
echo INTENTION: "publish" from the publish vault
goto :EOF

:EOF
echo.