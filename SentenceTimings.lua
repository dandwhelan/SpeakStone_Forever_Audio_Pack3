-- Sentence start times for the subtitles (tools/build_sentence_timings.py). T[clip] = comma list of the start of
-- sentence 2, 3, ... in 1/10 seconds (sentence 1 starts at 0). Parsed on demand by Subtitles.lua.
local addonName = ...
local T = {
}
if SpeakStone_RegisterSentenceTimings then
    SpeakStone_RegisterSentenceTimings(addonName, T, 10)
else
    SpeakStonePendingSentenceTimings = SpeakStonePendingSentenceTimings or {}
    table.insert(SpeakStonePendingSentenceTimings, { name = addonName, timings = T, unit = 10 })
end
