local require = require
local package = package
local _G = _G
local cipr = {}

local old_require = _G.require
_G.require = function (path)
    local path = path:gsub('%.', '_'):gsub('%/', '_')
    return old_require(path)
end
local require = _G.require

-- Import from ResourceDirectory
function cipr.import(package_name)
    return require(package_name)
end

return cipr