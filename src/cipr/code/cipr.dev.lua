local function load_json()
    require 'json'
    return json
end

local system = system
local require = require
local package = package
local json = load_json()
local io = io
local os = os
local _G = _G

local cipr = {}

local old_require = _G.require
_G.require = function (path)
    local path = path:gsub('%.', '/')
    return old_require(path)
end
local require = _G.require

cipr._packageDir = os.getenv('CIPR_PACKAGES')
cipr._projectDir = os.getenv('CIPR_PROJECT')

local ciprcfg
local file = io.open(cipr._projectDir .. '/.ciprcfg', 'r')
if file then
    local contents = file:read('*a')
    if contents and contents ~= '' then
        ciprcfg = json.decode(contents)
    end
    io.close(file)
else
    error('Could not find .ciprcfg', 2)
end

for i=1,#ciprcfg.packages do
    local name = ciprcfg.packages[i]
    local pattern
    pattern = cipr._packageDir .. '/' .. name .. '/?/init.lua'
    package.path = package.path .. ';' .. pattern
    pattern = cipr._packageDir .. '/' .. name .. '/?.lua'
    package.path = package.path .. ';' .. pattern
end

-- Import from installed package store
function cipr.import(package_name)
    return require(package_name)
end


return cipr