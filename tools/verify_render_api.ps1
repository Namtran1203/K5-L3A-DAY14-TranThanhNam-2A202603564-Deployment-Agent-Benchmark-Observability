$ErrorActionPreference = 'Stop'
$base = 'https://nam-day14-agent.onrender.com'
$secureKey = Read-Host 'Enter the AGENT_API_KEY from Render (input is hidden)' -AsSecureString
$pointer = [IntPtr]::Zero

try {
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    $apiKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    $headers = @{ 'X-API-Key' = $apiKey }
    $body = @{ user_id = 'day14-verification'; question = 'Reply with a short greeting.' } | ConvertTo-Json -Compress

    function Send-TestRequest {
        try {
            $response = Invoke-WebRequest -Uri "$base/ask" -Method Post -Headers $headers `
                -ContentType 'application/json' -Body $body -UseBasicParsing
            return [int]$response.StatusCode
        }
        catch {
            if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
                return [int]$_.Exception.Response.StatusCode.value__
            }
            throw
        }
    }

    $first = Send-TestRequest
    Write-Host "Authenticated request: HTTP $first"
    if ($first -ne 200) {
        throw 'Expected HTTP 200. Check that the key matches AGENT_API_KEY in Render.'
    }

    $statuses = @($first)
    for ($i = 2; $i -le 15; $i++) {
        $status = Send-TestRequest
        $statuses += $status
        if ($status -eq 429) { break }
    }

    Write-Host "Load test status codes: $($statuses -join ', ')"
    if ($statuses -contains 429) {
        Write-Host 'Rate limit verified: HTTP 429 observed.'
    }
    else {
        Write-Warning 'HTTP 429 was not observed. Wait 60 seconds for the rate window to clear, then run again.'
        exit 1
    }
}
finally {
    if ($pointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    }
    $apiKey = $null
    $headers = $null
    $secureKey.Dispose()
}
