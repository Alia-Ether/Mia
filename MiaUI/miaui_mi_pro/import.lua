--╔═════════════════════════════╗                       
--║  Link: t.me/FrontendVSCode                       ║                         
--║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
--║  lang: lua                                       ║                     
--║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
--║  build:3.10.15                                   ║
--║  files: import.lua                               ║    
--╚═════════════════════════════╝       


local info = debug.getinfo(1, "S")
local base = info.source:sub(2):match("(.*)/")

package.path = base .. "/?.lua;" .. base .. "/?/init.lua;" .. package.path

local anim = require("anim")
local full = require("full_palette")

local Mia = {}

------------------------------------------------
-- USER CONFIG PATH
------------------------------------------------

local HOME = os.getenv("HOME") or "."
local CONFIG_DIR = HOME .. "/.config/miaui"
local CONFIG_FILE = CONFIG_DIR .. "/config.lua"

------------------------------------------------
-- DEFAULT CONFIG TEMPLATE
------------------------------------------------

local DEFAULT_CONFIG = [[
-- ============================================
-- MiaUI User Config
-- ~/.config/miaui/config.lua
-- ============================================

return {

    ------------------------------------------------
    -- DEFAULT SPEED FOR ANIMATIONS
    ------------------------------------------------
    default_speed = 0.03,

    ------------------------------------------------
    -- COLOR SCHEMES
    ------------------------------------------------
    schemes = {

        ocean = {
            "#0033ff",
            "#00ccff",
            "#00ffaa",
        },

        sunset = {
            "#ff3300",
            "#ff9900",
            "#6600cc",
        },

        neon = {
            "#ff00ff",
            "#00ffff",
            "#ffff00",
        },

        cyber = {
            "#00ffcc",
            "#ff00ff",
            "#00ff00",
        },

    }
}
]]

------------------------------------------------
-- ENSURE CONFIG EXISTS
------------------------------------------------

local function ensure_config()

    local f = io.open(CONFIG_FILE, "r")
    if f then
        f:close()
        return
    end

    os.execute("mkdir -p " .. CONFIG_DIR)

    local out = io.open(CONFIG_FILE, "w")
    out:write(DEFAULT_CONFIG)
    out:close()

    print("✔ Created default config:")
    print("  " .. CONFIG_FILE)
end

------------------------------------------------
-- LOAD CONFIG
------------------------------------------------

local function load_config()

    local ok, cfg = pcall(dofile, CONFIG_FILE)
    if not ok then
        return {}
    end

    return cfg or {}
end

------------------------------------------------
-- ANSI 256 PALETTE GRID
------------------------------------------------

function Mia.palette()
    anim.palette256(8)
end

------------------------------------------------
-- MODE HEX PRINT
------------------------------------------------

local function new_mode(hex)

    local self = {}
    self.hex = hex

    function self:print(text)
        anim.render(self.hex, text)
        io.write("\n")
    end

    return self
end

function Mia.mode(hex)
    return new_mode(hex)
end

------------------------------------------------
-- CLI ENTRY
------------------------------------------------

local cmd = arg[1]

-- ensure config
ensure_config()

local CONFIG = load_config()
local CUSTOM = CONFIG.schemes or {}

------------------------------------------------
-- HELPERS
------------------------------------------------

local function list_custom()

    if not next(CUSTOM) then
        print("No custom schemes found.")
        return
    end

    print("Custom schemes:")

    for name, _ in pairs(CUSTOM) do
        print("  " .. name)
    end
end

------------------------------------------------
-- COMMANDS
------------------------------------------------

-- ---------- PALETTE ----------
if cmd == "palette" then

    Mia.palette()

-- ---------- FULL ----------
elseif cmd == "full" then

    full.run()

-- ---------- ANIM ----------
elseif cmd == "anim" and arg[2] then

    local name = arg[2]
    local text = arg[3] or ""

    -- LIST
    if name == "list" then
        list_custom()
        return Mia
    end

    -- builtin
    if type(anim[name]) == "function" then

        anim[name](text)

    -- custom scheme
    elseif CUSTOM[name] then

        anim.scheme(text, CUSTOM[name], CONFIG.default_speed)

    else

        print("Animation not found:", name)
        print()
        print("Built-in:")
        print("  rainbow wave pulse cycle neon fire")
        print()
        list_custom()
        print()
        print("Config file:")
        print("  " .. CONFIG_FILE)
    end

-- ---------- HEX MODE ----------
elseif arg[1] and arg[2] then

    Mia.mode(arg[1]):print(arg[2])

-- ---------- HELP ----------
else

    print("Usage:")
    print("  mia palette")
    print("  mia full")
    print("  mia anim list")
    print("  mia anim rainbow TEXT")
    print("  mia anim cyber TEXT")
    print("  mia #ff00ff TEXT")

end

return Mia