-- Sentence start times for the subtitles (tools/build_sentence_timings.py). T[clip] = comma list of the start of
-- sentence 2, 3, ... in 1/10 seconds (sentence 1 starts at 0). Parsed on demand by Subtitles.lua.
local addonName = ...
local T = {
["96931_description"]="14,78,128,166,203,242",
["96979_description"]="50,119,139,177,228",
["96999_description"]="24,61,99,132,149",
}
if SpeakStone_RegisterSentenceTimings then
    SpeakStone_RegisterSentenceTimings(addonName, T, 10)
else
    SpeakStonePendingSentenceTimings = SpeakStonePendingSentenceTimings or {}
    table.insert(SpeakStonePendingSentenceTimings, { name = addonName, timings = T, unit = 10 })
end
