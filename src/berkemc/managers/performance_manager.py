"""
Performance monitoring and management
"""

import psutil
import time
import threading
from typing import Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.live import Live
from rich.layout import Layout

class PerformanceManager:
    """System performance monitoring and management"""
    
    def __init__(self, console: Console):
        self.console = console
        self.monitoring = False
        self.monitor_thread = None
        
    def get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        try:
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory info
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk info
            disk = psutil.disk_usage('/')
            
            # Network info
            network = psutil.net_io_counters()
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else 0,
                    'max_frequency': cpu_freq.max if cpu_freq else 0
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'percent': swap.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            }
        except Exception as e:
            self.console.print(f"[red]Sistem bilgisi alınamadı: {e}[/red]")
            return {}
    
    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def create_performance_table(self, info: Dict) -> Table:
        """Create performance monitoring table"""
        table = Table(title="Sistem Performansı", show_header=True, header_style="bold cyan")
        table.add_column("Metrik", style="cyan", width=20)
        table.add_column("Değer", style="white", width=15)
        table.add_column("Durum", style="green", width=20)
        
        # CPU
        cpu_percent = info['cpu']['percent']
        cpu_status = "🟢 İyi" if cpu_percent < 70 else "🟡 Orta" if cpu_percent < 90 else "🔴 Yüksek"
        table.add_row("CPU Kullanımı", f"{cpu_percent:.1f}%", cpu_status)
        
        # Memory
        mem_percent = info['memory']['percent']
        mem_status = "🟢 İyi" if mem_percent < 70 else "🟡 Orta" if mem_percent < 90 else "🔴 Yüksek"
        table.add_row("RAM Kullanımı", f"{mem_percent:.1f}%", mem_status)
        
        # Disk
        disk_percent = info['disk']['percent']
        disk_status = "🟢 İyi" if disk_percent < 70 else "🟡 Orta" if disk_percent < 90 else "🔴 Yüksek"
        table.add_row("Disk Kullanımı", f"{disk_percent:.1f}%", disk_status)
        
        # Swap
        swap_percent = info['swap']['percent']
        swap_status = "🟢 İyi" if swap_percent < 50 else "🟡 Orta" if swap_percent < 80 else "🔴 Yüksek"
        table.add_row("Swap Kullanımı", f"{swap_percent:.1f}%", swap_status)
        
        return table
    
    def create_detailed_info_table(self, info: Dict) -> Table:
        """Create detailed system information table"""
        table = Table(title="Detaylı Sistem Bilgileri", show_header=True, header_style="bold cyan")
        table.add_column("Bileşen", style="cyan", width=20)
        table.add_column("Bilgi", style="white", width=30)
        
        # CPU Details
        table.add_row("CPU Çekirdek", str(info['cpu']['count']))
        table.add_row("CPU Frekans", f"{info['cpu']['frequency']:.0f} MHz")
        table.add_row("Max Frekans", f"{info['cpu']['max_frequency']:.0f} MHz")
        
        # Memory Details
        table.add_row("Toplam RAM", self.format_bytes(info['memory']['total']))
        table.add_row("Kullanılan RAM", self.format_bytes(info['memory']['used']))
        table.add_row("Boş RAM", self.format_bytes(info['memory']['available']))
        
        # Disk Details
        table.add_row("Toplam Disk", self.format_bytes(info['disk']['total']))
        table.add_row("Kullanılan Disk", self.format_bytes(info['disk']['used']))
        table.add_row("Boş Disk", self.format_bytes(info['disk']['free']))
        
        # Network Details
        table.add_row("Gönderilen", self.format_bytes(info['network']['bytes_sent']))
        table.add_row("Alınan", self.format_bytes(info['network']['bytes_recv']))
        
        return table
    
    def start_monitoring(self):
        """Start real-time performance monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Monitoring loop for real-time updates"""
        while self.monitoring:
            try:
                info = self.get_system_info()
                if info:
                    # Update performance data (could be stored for later use)
                    pass
                time.sleep(1)
            except Exception as e:
                self.console.print(f"[red]Monitoring hatası: {e}[/red]")
                break
    
    def show_performance_dashboard(self):
        """Show real-time performance dashboard"""
        try:
            with Live(console=self.console, refresh_per_second=2) as live:
                while True:
                    info = self.get_system_info()
                    if not info:
                        break
                    
                    # Create layout
                    layout = Layout()
                    layout.split_column(
                        Layout(self.create_performance_table(info), name="performance"),
                        Layout(self.create_detailed_info_table(info), name="details")
                    )
                    
                    live.update(layout)
                    
                    # Check for key press (non-blocking)
                    import select
                    import sys
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        break
                        
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.console.print(f"[red]Dashboard hatası: {e}[/red]")
    
    def get_minecraft_recommendations(self) -> List[str]:
        """Get Minecraft performance recommendations based on system"""
        info = self.get_system_info()
        recommendations = []
        
        if not info:
            return ["Sistem bilgisi alınamadı"]
        
        # CPU recommendations
        if info['cpu']['percent'] > 80:
            recommendations.append("CPU kullanımı yüksek - diğer uygulamaları kapatın")
        
        # Memory recommendations
        if info['memory']['percent'] > 85:
            recommendations.append("RAM kullanımı yüksek - Minecraft için daha az RAM ayırın")
        elif info['memory']['total'] < 4 * 1024**3:  # Less than 4GB
            recommendations.append("RAM az - Minecraft için maksimum 2GB ayırın")
        
        # Disk recommendations
        if info['disk']['percent'] > 90:
            recommendations.append("Disk dolu - gereksiz dosyaları silin")
        
        # General recommendations
        if info['cpu']['count'] < 4:
            recommendations.append("Az çekirdekli CPU - tek çekirdek modunu kullanın")
        
        if not recommendations:
            recommendations.append("Sistem Minecraft için uygun görünüyor")
        
        return recommendations

__all__ = ['PerformanceManager']
