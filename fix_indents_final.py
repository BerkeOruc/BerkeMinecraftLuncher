#!/usr/bin/env python3
"""Tüm indent hatalarını rekursif olarak düzelt"""

import subprocess
import sys

max_iterations = 50
iteration = 0

while iteration < max_iterations:
    iteration += 1
    
    # Syntax kontrolü
    result = subprocess.run(
        ["python3", "-m", "py_compile", "berke_minecraft_launcher.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ {iteration}. iterasyon: Syntax TAMAM!")
        sys.exit(0)
    
    # Hata mesajını parse et
    error = result.stderr
    
    # Satır numarasını bul
    import re
    match = re.search(r'line (\d+)', error)
    if not match:
        print(f"❌ Hata parse edilemedi: {error[:200]}")
        sys.exit(1)
    
    line_no = int(match.group(1))
    print(f"🔧 {iteration}. iterasyon: Satır {line_no} düzeltiliyor...")
    
    # Dosyayı oku
    with open('berke_minecraft_launcher.py', 'r') as f:
        lines = f.readlines()
    
    if line_no < 1 or line_no > len(lines):
        print(f"❌ Geçersiz satır numarası: {line_no}")
        sys.exit(1)
    
    # Hata tipini belirle
    if "unexpected indent" in error:
        # Fazla indent - azalt
        line = lines[line_no - 1]
        stripped = line.lstrip()
        if line != stripped:
            # 4 boşluk azalt
            current_indent = len(line) - len(stripped)
            new_indent = max(0, current_indent - 4)
            lines[line_no - 1] = ' ' * new_indent + stripped
            print(f"  → {current_indent} → {new_indent} boşluk")
    
    elif "expected an indented block" in error:
        # Eksik indent - artır
        if line_no > 0:
            line = lines[line_no - 1]
            stripped = line.lstrip()
            current_indent = len(line) - len(stripped)
            new_indent = current_indent + 4
            lines[line_no - 1] = ' ' * new_indent + stripped
            print(f"  → {current_indent} → {new_indent} boşluk")
    
    # Dosyaya yaz
    with open('berke_minecraft_launcher.py', 'w') as f:
        f.writelines(lines)

print(f"⚠️ {max_iterations} iterasyon sonunda tamamlanamadı")
sys.exit(1)

