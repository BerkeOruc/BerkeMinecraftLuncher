#!/bin/bash
# BMC Logo Creator

# ASCII Art Logo
cat > bmc_logo_ascii.txt << 'LOGO'
██████╗ ███╗   ███╗ ██████╗
██╔══██╗████╗ ████║██╔════╝
██████╔╝██╔████╔██║██║     
██╔══██╗██║╚██╔╝██║██║     
██████╔╝██║ ╚═╝ ██║╚██████╗
╚═════╝ ╚═╝     ╚═╝ ╚═════╝
LOGO

echo "✅ ASCII logo oluşturuldu: bmc_logo_ascii.txt"

# ImageMagick varsa PNG oluştur
if command -v convert &> /dev/null; then
    convert -size 256x256 xc:"#1E1E1E" \
      -font "DejaVu-Sans-Mono-Bold" \
      -pointsize 48 \
      -fill "#00FFFF" \
      -gravity center \
      -annotate +0+0 "BMC" \
      bmc_logo.png 2>/dev/null && echo "✅ PNG logo oluşturuldu: bmc_logo.png" || echo "⚠ PNG oluşturulamadı"
else
    echo "⚠ ImageMagick kurulu değil. Sadece ASCII logo oluşturuldu."
    echo "  PNG logo için: sudo pacman -S imagemagick"
fi

echo ""
echo "Logo dosyaları:"
ls -lh bmc_logo* 2>/dev/null || echo "  bmc_logo_ascii.txt"
