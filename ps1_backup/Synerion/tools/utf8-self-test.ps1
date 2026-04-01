$sample = "UTF-8 check — 한글 OK"

Write-Output "Profile: $PROFILE"
Write-Output "CodePage:"
cmd /c chcp

Write-Output "`nConsole encodings:"
Write-Output ("InputEncoding   = " + [Console]::InputEncoding.WebName)
Write-Output ("OutputEncoding  = " + [Console]::OutputEncoding.WebName)
Write-Output ("PsOutputEncoding = " + $OutputEncoding.WebName)

Write-Output "`nPython env:"
Write-Output ("PYTHONUTF8      = " + $env:PYTHONUTF8)
Write-Output ("PYTHONIOENCODING = " + $env:PYTHONIOENCODING)

Write-Output "`nPowerShell sample:"
Write-Output $sample

Write-Output "`nPython sample:"
python -c "print('UTF-8 check — 한글 OK')"
