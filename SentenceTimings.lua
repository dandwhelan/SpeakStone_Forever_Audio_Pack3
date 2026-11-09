-- Sentence start times for the subtitles (tools/build_sentence_timings.py). T[clip] = comma list of the start of
-- sentence 2, 3, ... in 1/10 seconds (sentence 1 starts at 0). Parsed on demand by Subtitles.lua.
local addonName = ...
local T = {
["93030_description"]="18,46,68,116",
["95926_description"]="8,32,92,120,136,156,188",
["96077_description"]="12,64,106,125,133,156,191",
["96931_description"]="14,78,128,166,203,242",
["96979_description"]="50,119,139,177,228",
["96999_description"]="24,61,99,132,149",
["97168_description"]="34,55,99,142,175,219",
["98251_completion"]="7,26,34",
}
if SpeakStone_RegisterSentenceTimings then
    SpeakStone_RegisterSentenceTimings(addonName, T, 10)
else
    SpeakStonePendingSentenceTimings = SpeakStonePendingSentenceTimings or {}
    table.insert(SpeakStonePendingSentenceTimings, { name = addonName, timings = T, unit = 10 })
end
