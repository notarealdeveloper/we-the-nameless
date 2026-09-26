-- Keep directory/title discovery in sync with epistle_items in book-subset.
local lfs = require("lfs")
local M = {}

function M.books(directory)
    local books = {}
    for dirname in lfs.dir(directory) do
        local number, slug = dirname:match("^(%d+)%-([%w-]+)$")
        if number and slug ~= "on-the-lamb" and not slug:match("^exile%-")
            and lfs.attributes(directory .. "/" .. dirname, "mode") == "directory" then
            local words, chapters = {}, {}
            for word in dirname:gmatch("[^-]+") do
                words[#words + 1] = word:sub(1, 1):upper() .. word:sub(2):lower()
            end
            for filename in lfs.dir(directory .. "/" .. dirname) do
                if filename:match("^%d+%.tex$")
                    and lfs.attributes(directory .. "/" .. dirname .. "/" .. filename, "mode") == "file" then
                    chapters[#chapters + 1] = dirname .. "/" .. filename:gsub("%.tex$", "")
                end
            end
            table.sort(chapters)
            if #chapters > 0 then
                books[#books + 1] = {stem = dirname, title = table.concat(words, " "), chapters = chapters}
            end
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
        tex.sprint("\\clearpage\\EpistleBook{" .. book.title .. "}")
        for _, chapter in ipairs(book.chapters) do
            tex.sprint("\\input{" .. directory .. "/" .. chapter .. "}")
        end
    end
end

return M
