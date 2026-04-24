--╔═════════════════════════════╗                       
--║  Link: t.me/FrontendVSCode                       ║                         
--║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
--║  lang: lua                                       ║                     
--║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
--║  build:3.10.15                                   ║
--║  files: Color.lua                                ║    
--╚═════════════════════════════╝       



local Color = {}

function Color.get_palette(filepath)
    local palette = {}
    local file = io.open(filepath, "r")
    
    if not file then return {"#FFF000"} end

    for line in file:lines() do
        -- Extract hex values only
        local hex = line:match("^#(%x+)")
        if hex then
            table.insert(palette, "#" .. hex)
        end
    end
    
    file:close()
    return palette
end

return Color.get_palette("Color.txt")
