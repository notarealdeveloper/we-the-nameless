-- Keep filename/title discovery in sync with epistle_items in book-subset.
local lfs = require("lfs")
local M = {}

function M.books(directory)
    local books = {}
    for filename in lfs.dir(directory) do
        local stem = filename:match("^([%w-]+)%.tex$")
        if stem and lfs.attributes(directory .. "/" .. filename, "mode") == "file" then
            local words = {}
            for word in stem:gmatch("[^-]+") do
                words[#words + 1] = word:sub(1, 1):upper() .. word:sub(2):lower()
            end
            books[#books + 1] = {stem = stem, title = table.concat(words, " ")}
        end
    end
    table.sort(books, function(a, b) return a.stem < b.stem end)
    return books
end

function M.contents(directory)
    for _, book in ipairs(M.books(directory)) do
        tex.sprint("\\EpistleContentsEntry{" .. book.title .. "}")
    end
end

function M.include(directory)
    for _, book in ipairs(M.books(directory)) do
        -- Start a new book without a second page break after its destination.
        tex.sprint("\\clearpage\\EpistleBook{" .. book.title .. "}")
        tex.sprint("\\input{" .. directory .. "/" .. book.stem .. "}")
    end
end

return M
