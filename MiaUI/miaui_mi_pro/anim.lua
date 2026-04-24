--╔═════════════════════════════╗                       
--║  Link: t.me/FrontendVSCode                       ║                         
--║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
--║  lang: lua                                       ║                     
--║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
--║  build:3.10.15                                   ║
--║  files: anim.lua                                 ║    
--╚═════════════════════════════╝       
  
                                                          


local anim = {}

------------------------------------------------
-- RESET
------------------------------------------------

function anim.reset()
    return "\27[0m"
end

------------------------------------------------
-- TRUECOLOR FOREGROUND
------------------------------------------------

function anim.fg_true(hex)

    if not hex or #hex ~= 7 then
        return anim.reset()
    end

    local r = tonumber(hex:sub(2,3), 16)
    local g = tonumber(hex:sub(4,5), 16)
    local b = tonumber(hex:sub(6,7), 16)

    return string.format("\27[38;2;%d;%d;%dm", r, g, b)
end

------------------------------------------------
-- ANSI 256 BACKGROUND
------------------------------------------------

function anim.bg256(idx)
    return string.format("\27[48;5;%dm", tonumber(idx))
end

------------------------------------------------
-- Render single color text
------------------------------------------------

function anim.render(hex, label)

    io.write("\r")
    io.write(anim.fg_true(hex))
    io.write(label)
    io.write(anim.reset())
    io.flush()
end

------------------------------------------------
-- DRAW ANSI CELL
------------------------------------------------

function anim.cell256(idx)

    local label = string.format("%3d", idx)

    io.write(anim.bg256(idx))
    io.write(" " .. label .. " ")
    io.write(anim.reset())
end

------------------------------------------------
-- ANSI 256 PALETTE
------------------------------------------------

function anim.palette256(per_row)

    per_row = per_row or 8

    for i = 0, 255 do

        anim.cell256(i)

        if (i + 1) % per_row == 0 then
            io.write("\n")
        end
    end

    io.write("\n")
end

------------------------------------------------
-- HEX → ANSI256
------------------------------------------------

function anim.hex_to_256(hex)

    local r = tonumber(hex:sub(2,3), 16)
    local g = tonumber(hex:sub(4,5), 16)
    local b = tonumber(hex:sub(6,7), 16)

    local function q(v)
        return math.floor(v / 51)
    end

    return 16 + 36*q(r) + 6*q(g) + q(b)
end

------------------------------------------------
-- PALETTE FROM HEX LIST
------------------------------------------------

function anim.palette_hex(list, per_row)

    per_row = per_row or 8
    local i = 0

    for _, hex in ipairs(list) do

        anim.cell256(anim.hex_to_256(hex))

        i = i + 1
        if i % per_row == 0 then
            io.write("\n")
        end
    end

    io.write("\n")
end

------------------------------------------------
-- LOAD USER CONFIG
------------------------------------------------

local function load_config()

    local home = os.getenv("HOME")
    if not home then return {} end

    local path = home .. "/.config/miaui/config.lua"

    local ok, cfg = pcall(dofile, path)

    if ok and type(cfg) == "table" then
        return cfg
    end

    return {}
end

------------------------------------------------
-- CONFIG
------------------------------------------------

local CONFIG = load_config()

CONFIG.default_speed = CONFIG.default_speed or 0.05
CONFIG.schemes = CONFIG.schemes or {}

------------------------------------------------
-- GET COLOR SCHEME
------------------------------------------------

function anim.get_scheme(name)

    if CONFIG.schemes[name] then
        return CONFIG.schemes[name]
    end

    return nil
end

------------------------------------------------
-- SLEEP
------------------------------------------------

local function sleep(sec)
    os.execute("sleep " .. tonumber(sec))
end

------------------------------------------------
-- SCHEME ANIMATION
------------------------------------------------

function anim.scheme(text, scheme, speed)

    speed = speed or CONFIG.default_speed or 0.05

    local offset = 0

    while true do

        io.write("\r")

        for i = 1, #text do

            local hex = scheme[(i + offset - 1) % #scheme + 1]

            io.write(anim.fg_true(hex))
            io.write(text:sub(i,i))
        end

        io.write(anim.reset())
        io.flush()

        offset = offset + 1
        sleep(speed)
    end
end

------------------------------------------------
-- BUILTIN SCHEMES
------------------------------------------------

local BUILTIN = {

    rainbow = {
        "#ff0000","#ff7f00","#ffff00",
        "#00ff00","#00ffff","#0000ff",
        "#8b00ff"
    },

    fire = {
        "#330000","#ff0000","#ff6600",
        "#ffaa00","#ffff00"
    },

    neon = {
        "#ff00ff","#00ffff","#00ff00",
        "#ffff00"
    }
}

------------------------------------------------
-- BASIC ANIMS
------------------------------------------------

function anim.rainbow(text)
    return anim.scheme(text, BUILTIN.rainbow)
end

function anim.fire(text)
    local s = anim.get_scheme("fire") or BUILTIN.fire
    return anim.scheme(text, s)
end

function anim.neon(text)
    local s = anim.get_scheme("neon") or BUILTIN.neon
    return anim.scheme(text, s)
end

function anim.wave(text)
    return anim.scheme(text, BUILTIN.rainbow, 0.08)
end

function anim.pulse(text)
    return anim.scheme(text, {"#ffffff","#888888","#444444"}, 0.12)
end

function anim.cycle(text)
    return anim.scheme(text, BUILTIN.rainbow, 0.02)
end

------------------------------------------------
-- CUSTOM SCHEME NAME CALL
------------------------------------------------

function anim.custom(name, text)

    local s = anim.get_scheme(name)

    if not s then
        return false
    end

    anim.scheme(text, s)
    return true
end

return anim
