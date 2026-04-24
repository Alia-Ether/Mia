--╔═════════════════════════════╗                       
--║  Link: t.me/FrontendVSCode                       ║                         
--║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
--║  lang: lua                                       ║                     
--║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
--║  build:3.10.15                                   ║
--║  files: full_palette.lua                         ║    
--╚═════════════════════════════╝       



local info = debug.getinfo(1, "S")
local base = info.source:sub(2):match("(.*)/")

package.path = base .. "/?.lua;" .. base .. "/?/init.lua;" .. package.path

local anim = require("anim")

local M = {}

------------------------------------------------
-- READ Color.txt
------------------------------------------------

local function load_colors()

    local path = base .. "/Color.txt"
    local f = io.open(path, "r")

    if not f then
        return nil, "Color.txt not found in " .. path
    end

    local colors = {}

    for line in f:lines() do
        for hex in line:gmatch("[0-9A-Fa-f]+") do
            if #hex == 6 then
                table.insert(colors, "#" .. hex:upper())
            elseif #hex == 3 then
                local h = hex:upper()
                table.insert(colors, "#" ..
                    h:sub(1,1)..h:sub(1,1) ..
                    h:sub(2,2)..h:sub(2,2) ..
                    h:sub(3,3)..h:sub(3,3))
            end
        end
    end

    f:close()
    return colors
end

------------------------------------------------
-- CLEAR SCREEN
------------------------------------------------

local function clear()
    io.write("\27[2J\27[H")
end

------------------------------------------------
-- DRAW PAGE GRID
------------------------------------------------

local function draw_page(colors, page, per_page)

    clear()

    local total_pages = math.ceil(#colors / per_page)

    print("VORTEX FULL PALETTE")
    print("Page " .. page .. " / " .. total_pages)
    print("---------------------------------------")
    print("1 = Prev | 2 = Next | 0 = Exit\n")

    local start = (page - 1) * per_page + 1
    local stop  = math.min(start + per_page - 1, #colors)

    local cols = 8
    local col = 0

    for i = start, stop do

        local hex = colors[i]
        local idx = anim.hex_to_256(hex)

        io.write(anim.bg256(idx))
        io.write("   ")
        io.write(anim.reset())
        io.write(" " .. hex .. "  ")

        col = col + 1

        if col == cols then
            io.write("\n")
            col = 0
        end
    end

    io.write("\n\n")
end

------------------------------------------------
-- MAIN LOOP
------------------------------------------------

function M.run()

    local colors, err = load_colors()

    if not colors then
        print("ERROR:", err)
        return
    end

    local page = 1
    local per_page = 64

    while true do

        draw_page(colors, page, per_page)

        io.write("> ")
        local key = io.read()

        if key == "0" then
            clear()
            break

        elseif key == "1" then
            page = math.max(1, page - 1)

        elseif key == "2" then
            local maxp = math.ceil(#colors / per_page)
            if page < maxp then
                page = page + 1
            end
        end
    end
end

return M