function add_new_keys(tag, timestamp, record)
    if record["slice-session-info"] ~= nil then
        -- Add S-NSSAI key
        local sst = tostring(record["slice-session-info"]["Snssai"]["SST"])
        local sd = tostring(record["slice-session-info"]["Snssai"]["SD"])
        record["S-NSSAI"] = sst .. "@" .. sd
        
        -- Add F-SEID key
        local remote_seid = tostring(record["slice-session-info"]["PFCPSession"]["Fseid"]["RemoteSEID"])
        local ip_address = record["slice-session-info"]["PFCPSession"]["Fseid"]["IPAddress"]
        record["F-SEID"] = remote_seid .. "@" .. ip_address
    end
    return 1, timestamp, record
end
