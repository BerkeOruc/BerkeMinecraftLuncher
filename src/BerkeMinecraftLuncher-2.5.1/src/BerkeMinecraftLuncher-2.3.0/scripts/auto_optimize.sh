#!/bin/bash
# Otomatik Sistem Optimizasyonu
# Minecraft için sistem ayarlarını optimize eder

set -e

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}║           OTOMATIK SISTEM OPTIMIZASYONU                    ║${NC}"
echo -e "${CYAN}║           Minecraft Performans Artırıcı                    ║${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Root kontrolü
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}✗ Bu scripti root olarak çalıştırmayın!${NC}"
    echo -e "${YELLOW}  Normal kullanıcı olarak çalıştırın (sudo şifre soracak).${NC}"
    exit 1
fi

echo -e "${YELLOW}Bu script şu optimizasyonları yapacak:${NC}"
echo "  1. CPU Performance Mode"
echo "  2. Swappiness Azaltma (10)"
echo "  3. Transparent Huge Pages"
echo "  4. I/O Scheduler Optimizasyonu"
echo "  5. Network Optimizasyonları"
echo ""
echo -e "${YELLOW}Devam etmek istiyor musunuz? (y/n)${NC}"
read -r response

if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo -e "${RED}İptal edildi.${NC}"
    exit 0
fi

echo ""
echo -e "${CYAN}[1/5] CPU Performance Mode...${NC}"

# CPU Governor'ı performance'a al
if [ -d "/sys/devices/system/cpu/cpu0/cpufreq" ]; then
    echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null 2>&1
    echo -e "${GREEN}✓ CPU performance mode aktif${NC}"
else
    echo -e "${YELLOW}⚠ CPU frequency scaling desteklenmiyor${NC}"
fi

echo ""
echo -e "${CYAN}[2/5] Swappiness optimizasyonu...${NC}"

# Swappiness'i 10'a düşür
sudo sysctl vm.swappiness=10 > /dev/null
echo -e "${GREEN}✓ Swappiness = 10 (RAM öncelikli)${NC}"

echo ""
echo -e "${CYAN}[3/5] Transparent Huge Pages...${NC}"

# THP'yi aktifleştir
if [ -f "/sys/kernel/mm/transparent_hugepage/enabled" ]; then
    echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled > /dev/null
    echo always | sudo tee /sys/kernel/mm/transparent_hugepage/defrag > /dev/null
    echo -e "${GREEN}✓ Transparent Huge Pages aktif${NC}"
else
    echo -e "${YELLOW}⚠ THP desteklenmiyor${NC}"
fi

echo ""
echo -e "${CYAN}[4/5] I/O Scheduler optimizasyonu...${NC}"

# Disk tipini tespit et ve uygun scheduler'ı ayarla
for disk in /sys/block/sd* /sys/block/nvme*; do
    if [ -d "$disk" ]; then
        disk_name=$(basename "$disk")
        
        # Rotational kontrolü (SSD vs HDD)
        if [ -f "$disk/queue/rotational" ]; then
            rotational=$(cat "$disk/queue/rotational")
            
            if [ "$rotational" -eq 0 ]; then
                # SSD - mq-deadline veya none
                if [ -f "$disk/queue/scheduler" ]; then
                    if grep -q "mq-deadline" "$disk/queue/scheduler"; then
                        echo mq-deadline | sudo tee "$disk/queue/scheduler" > /dev/null
                        echo -e "${GREEN}✓ $disk_name: mq-deadline (SSD)${NC}"
                    elif grep -q "none" "$disk/queue/scheduler"; then
                        echo none | sudo tee "$disk/queue/scheduler" > /dev/null
                        echo -e "${GREEN}✓ $disk_name: none (NVMe)${NC}"
                    fi
                fi
            else
                # HDD - bfq
                if [ -f "$disk/queue/scheduler" ]; then
                    if grep -q "bfq" "$disk/queue/scheduler"; then
                        echo bfq | sudo tee "$disk/queue/scheduler" > /dev/null
                        echo -e "${GREEN}✓ $disk_name: bfq (HDD)${NC}"
                    fi
                fi
            fi
        fi
    fi
done

echo ""
echo -e "${CYAN}[5/5] Network optimizasyonları...${NC}"

# TCP optimizasyonları
sudo sysctl -w net.core.rmem_max=134217728 > /dev/null
sudo sysctl -w net.core.wmem_max=134217728 > /dev/null
sudo sysctl -w net.ipv4.tcp_rmem="4096 87380 134217728" > /dev/null
sudo sysctl -w net.ipv4.tcp_wmem="4096 65536 134217728" > /dev/null
echo -e "${GREEN}✓ Network buffer boyutları artırıldı${NC}"

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}║              ✓ OPTİMİZASYON TAMAMLANDI!                   ║${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}Optimizasyonlar uygulandı!${NC}"
echo ""
echo -e "${YELLOW}NOT:${NC}"
echo "  • Bu optimizasyonlar geçicidir (yeniden başlatmada sıfırlanır)"
echo "  • Kalıcı yapmak için: sudo ./scripts/make_permanent.sh"
echo "  • Geri almak için: sudo ./scripts/restore_defaults.sh"
echo ""
echo -e "${CYAN}Minecraft'ı başlatabilirsiniz:${NC}"
echo "  ./start.sh"
echo ""
