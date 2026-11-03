param([Parameter(Mandatory=$true)][string]$Directory)
# Render the exact public scene primitives to PNG; no third-party packages.
Add-Type -AssemblyName System.Drawing
$scenes = Get-Content -LiteralPath (Join-Path $Directory 'chart-data.json') -Raw | ConvertFrom-Json
foreach ($property in $scenes.PSObject.Properties) {
    $bitmap = New-Object System.Drawing.Bitmap 1000,620
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    foreach ($item in $property.Value) {
        $color = [System.Drawing.ColorTranslator]::FromHtml($item.color)
        $brush = New-Object System.Drawing.SolidBrush $color
        switch ($item.type) {
            'rect' { $graphics.FillRectangle($brush,[single]$item.x,[single]$item.y,[single]$item.w,[single]$item.h) }
            'circle' { $graphics.FillEllipse($brush,[single]($item.x-$item.r),[single]($item.y-$item.r),[single](2*$item.r),[single](2*$item.r)) }
            'line' { $pen = New-Object System.Drawing.Pen $color; $graphics.DrawLine($pen,[single]$item.x,[single]$item.y,[single]$item.x2,[single]$item.y2); $pen.Dispose() }
            'text' {
                $font = New-Object System.Drawing.Font 'Arial',([single]$item.size),([System.Drawing.FontStyle]::Regular),([System.Drawing.GraphicsUnit]::Pixel)
                $graphics.DrawString([string]$item.text,$font,$brush,[single]$item.x,[single]($item.y-$item.size))
                $font.Dispose()
            }
        }
        $brush.Dispose()
    }
    $bitmap.Save((Join-Path $Directory ($property.Name+'.png')),[System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose(); $bitmap.Dispose()
}
