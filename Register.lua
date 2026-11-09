local addonName = ...

local voice = {
    races = {
        Dw = "Dwarf",
        Dy = "Dryad",
        Hu = "Human",
        NE = "Night Elf",
        Or = "Orc",
        Ta = "Tauren",
        Ud = "Undead",
    },
    npc = {
    },
    quest = {
        [97977] = "DyF",
        [97979] = "NEF",
        [97985] = "UdM",
        [98021] = "HuM",
        [98024] = "M",
        [98025] = "NEF",
        [98042] = "NEM",
        [98209] = "NEM",
        [98216] = "DwM",
        [98221] = "DwM",
        [98223] = "DwM",
        [98230] = "DwM",
        [98283] = "M",
        [98298] = "UdM",
        [98299] = "UdM",
        [98300] = "DwM",
        [98310] = "DwM",
        [98313] = "DwM",
        [98322] = "DwM",
        [98340] = "TaM",
        [98341] = "NEM",
        [98362] = "NEM",
        [98386] = "HuM",
        [98387] = "HuM",
        [98392] = "NEF",
        [98393] = "NEM",
        [98397] = "NEM",
        [98398] = "NEF",
        [98403] = "NEM",
        [98407] = "HuM",
        [98423] = "DwM",
        [98424] = "TaM",
        [98427] = "TaM",
        [98435] = "TaM",
        [98461] = "DwF",
        [98545] = "UdM",
        [98574] = "DwM",
        [98575] = "OrM",
        [98576] = "OrM",
        [98581] = "DwM",
        [98601] = "UdM",
        [98815] = "HuM",
        [98823] = { d = "TaF", p = "TaM", c = "TaM" },
        [98824] = "DwM",
        [98887] = "OrM",
        [98888] = "OrM",
        [98895] = "DwM",
        [98896] = "DwM",
        [99046] = "NEF",
        [99048] = "OrM",
        [99051] = "OrM",
        [99052] = "OrM",
        [99080] = "TaM",
        [99082] = "TaM",
        [99108] = "TaM",
        [99130] = "HuM",
        [99131] = "HuM",
        [99134] = "UdM",
        [99141] = "UdM",
        [99142] = "UdM",
        [99156] = "UdF",
        [99411] = "TaM",
    },
}

-- SpeakStone_RegisterSoundPack is defined at the top of
-- the base addon's SpeakStone_Main.lua. If this pack loads
-- first, that global does not exist yet -- queue instead, and
-- the base addon drains the queue itself once it loads.
if SpeakStone_RegisterSoundPack then
    SpeakStone_RegisterSoundPack(addonName, SpeakStoneSoundLengths_Pack_SpeakStone_Forever_Audio_Pack3, voice)
else
    SpeakStonePendingSoundPacks = SpeakStonePendingSoundPacks or {}
    table.insert(SpeakStonePendingSoundPacks,
        { name = addonName, index = SpeakStoneSoundLengths_Pack_SpeakStone_Forever_Audio_Pack3, voice = voice })
end
