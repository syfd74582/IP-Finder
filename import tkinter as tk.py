import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import sys
import os
import socket
import ipaddress
import re
import csv
from datetime import datetime

# محاولة استيراد scapy
try:
    from scapy.all import ARP, Ether, srp, conf, sniff, IP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("Scapy not available, sniffer mode disabled.")

# متغير لتحديد إذا كانت دوال الواجهات تعمل
GET_IFACES_WORKING = False

# محاولة استيراد دوال الواجهات المتقدمة للحصول على الأسماء الوصفية
if SCAPY_AVAILABLE:
    try:
        from scapy.arch.windows import get_windows_if_list
        GET_IFACES_WORKING = True
    except ImportError:
        try:
            from scapy.arch import get_if_list, get_if_addr
            GET_IFACES_WORKING = False
        except:
            GET_IFACES_WORKING = False

# قواعد بيانات بسيطة لتحديد الشركة من MAC (OUI)
OUI_DB = {
    "00:0E:53": "Axis Communications",
    "00:1C:9E": "Hikvision",
    "00:12:C8": "TP-Link",
    "00:1A:6B": "Dahua",
    "00:13:8F": "Samsung Techwin",
    "00:15:5D": "Microsoft",
    "00:50:C2": "IEEE 802.11",
    "00:14:6C": "Hon Hai Precision",
    "00:1E:8F": "Shenzhen Dnake",
    "00:11:22": "Generic",
    "00:23:8B": "Grandstream",
    "00:17:0E": "AVerMedia",
    "00:1B:21": "ACTi",
    "00:04:20": "Vivotek",
    "00:40:8C": "Intel",
    "00:1A:A9": "Realtek",
    "00:1F:1F": "Cisco",
    "00:21:5E": "Buffalo",
    "00:24:01": "ASUSTek",
    "00:25:9C": "Ruckus Wireless",
    "00:26:62": "Huawei",
    "00:30:18": "Siemens",
    "00:90:A9": "Panasonic",
    "00:80:77": "Sony",
    "00:0C:76": "Samsung Electronics",
    "00:17:9A": "Apple",
    "00:23:12": "Apple",
    "00:25:00": "Apple",
    "00:26:BB": "Apple",
    "F8:1E:DF": "Apple",
    "34:15:9E": "Apple",
    "AC:BC:32": "Apple",
    "70:56:81": "TP-Link",
    "54:60:09": "TP-Link",
    "B4:75:0E": "TP-Link",
    "14:91:82": "TP-Link",
    "C0:25:E9": "TP-Link",
    "D8:5D:4C": "TP-Link",
    "00:1C:DF": "Netgear",
    "00:0F:66": "Netgear",
    "20:4E:7F": "Netgear",
    "00:0C:41": "Netgear",
    "00:14:6C": "D-Link",
    "00:1B:11": "D-Link",
    "00:22:B0": "D-Link",
    "00:26:5A": "D-Link",
    "00:1E:58": "D-Link",
    "00:21:91": "ZyXEL",
    "00:13:49": "Zyxel",
    "00:19:CB": "Zyxel",
    "00:0A:42": "Ubiquiti",
    "00:27:22": "Ubiquiti",
    "44:D9:E7": "Ubiquiti",
    "78:8A:20": "Ubiquiti",
    "80:2A:A8": "Ubiquiti",
    "B4:FB:E4": "Ubiquiti",
    "00:18:E7": "MikroTik",
    "00:0C:42": "MikroTik",
    "64:D1:54": "MikroTik",
}

# قوائم المنافذ لتحديد نوع الجهاز
PORTS_FOR_TYPE = {
    "Camera": [80, 443, 554, 8000, 8080, 8899, 37777],
    "Router": [80, 443, 23, 22, 53, 67, 68],
    "Printer": [9100, 515, 631, 80],
    "Server": [80, 443, 22, 3389, 3306, 1433],
    "Generic": [80, 443, 22, 23, 445],
}

def get_vendor(mac):
    """استخراج الشركة المصنعة من عنوان MAC"""
    if not mac or mac == "Unknown":
        return "Unknown"
    mac_clean = mac.upper()
    if '-' in mac_clean:
        mac_clean = mac_clean.replace('-', ':')
    oui = mac_clean[:8]
    return OUI_DB.get(oui, "Unknown")

def scan_ports(ip, timeout=1):
    """فحص المنافذ لتحديد نوع الجهاز"""
    open_ports = []
    all_ports = (PORTS_FOR_TYPE["Camera"] + PORTS_FOR_TYPE["Router"] + 
                 PORTS_FOR_TYPE["Printer"] + PORTS_FOR_TYPE["Server"])
    
    for port in set(all_ports):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except:
            pass
    
    open_ports = sorted(set(open_ports))
    
    if any(p in [554, 8000, 8899, 37777] for p in open_ports):
        device_type = "Camera"
    elif any(p in [23, 22, 53, 67, 68] for p in open_ports):
        device_type = "Router"
    elif any(p in [9100, 515, 631] for p in open_ports):
        device_type = "Printer"
    elif any(p in [3389, 3306, 1433] for p in open_ports):
        device_type = "Server"
    elif open_ports:
        device_type = "Generic"
    else:
        device_type = "Unknown"
    return device_type, open_ports

def get_current_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None

def get_interfaces_with_friendly_names():
    """
    الحصول على قائمة الواجهات بصيغة:
    Ethernet (192.168.1.100)
    Wi-Fi (192.168.1.101)
    VMware Network Adapter VMnet1 (192.168.xx.x)
    """
    interfaces = []
    if not SCAPY_AVAILABLE:
        return interfaces

    # محاولة استخدام get_windows_if_list (تعمل في Windows مع Scapy)
    try:
        if GET_IFACES_WORKING:
            if_list = get_windows_if_list()
            for iface in if_list:
                desc = iface.get('description', 'Unknown')
                ips = iface.get('ips', [])
                ipv4 = next((ip for ip in ips if '.' in ip), None)
                if ipv4:
                    interfaces.append((desc, ipv4))
                else:
                    interfaces.append((desc, "No IP"))
            return interfaces
    except Exception:
        pass

    # طريقة بديلة: استخدام get_if_list والحصول على IP
    try:
        from scapy.arch import get_if_list, get_if_addr
        if_list = get_if_list()
        for iface in if_list:
            try:
                ip = get_if_addr(iface)
                if ip != '0.0.0.0':
                    interfaces.append((iface, ip))
                else:
                    interfaces.append((iface, "No IP"))
            except:
                interfaces.append((iface, "No IP"))
        return interfaces
    except Exception:
        pass

    # إضافة افتراضية
    interfaces.append(("Default Interface", "Use default"))
    return interfaces

class IPFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Finder - كشف أجهزة الشبكة")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        
        # إعدادات RTL للواجهة العربية
        self.root.option_add('*tearOff', False)
        
        # متغيرات
        self.discovered_devices = {}
        self.scanning = False
        self.current_thread = None
        self.interface = None
        self.iface_map = {}  # تخزين خريطة الاسم المعروض إلى الاسم الحقيقي
        
        # إطار التحكم العلوي
        control_frame = ttk.LabelFrame(root, text="التحكم والإعدادات", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # صف: واجهة الشبكة
        iface_row = ttk.Frame(control_frame)
        iface_row.pack(fill="x", pady=5)
        
        ttk.Label(iface_row, text="واجهة الشبكة:").pack(side="right", padx=5)
        self.iface_var = tk.StringVar()
        self.iface_combo = ttk.Combobox(iface_row, textvariable=self.iface_var, width=50, state="readonly")
        self.iface_combo.pack(side="right", padx=5)
        ttk.Button(iface_row, text="تحديث", command=self.refresh_interfaces).pack(side="right", padx=5)
        
        # صف: الأزرار
        btn_row = ttk.Frame(control_frame)
        btn_row.pack(fill="x", pady=10)
        
        self.start_btn = ttk.Button(btn_row, text="بدء الاكتشاف", command=self.start_discovery)
        self.start_btn.pack(side="right", padx=5)
        
        self.restart_btn = ttk.Button(btn_row, text="إعادة تشغيل البرنامج", command=self.restart_app)
        self.restart_btn.pack(side="right", padx=5)
        
        self.status_label = ttk.Label(btn_row, text="جاهز", foreground="green")
        self.status_label.pack(side="right", padx=5)
        
        # إطار النتائج
        result_frame = ttk.LabelFrame(root, text="الأجهزة المكتشفة", padding=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # إنشاء جدول لعرض النتائج
        columns = ("IP", "MAC", "Vendor", "Device Type", "Open Ports", "Detected By", "Time")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("IP", text="IP Address")
        self.tree.heading("MAC", text="MAC Address")
        self.tree.heading("Vendor", text="الشركة المصنعة")
        self.tree.heading("Device Type", text="نوع الجهاز")
        self.tree.heading("Open Ports", text="المنافذ المفتوحة")
        self.tree.heading("Detected By", text="طريقة الاكتشاف")
        self.tree.heading("Time", text="وقت الاكتشاف")
        
        self.tree.column("IP", width=120, anchor='center')
        self.tree.column("MAC", width=140, anchor='center')
        self.tree.column("Vendor", width=150, anchor='center')
        self.tree.column("Device Type", width=100, anchor='center')
        self.tree.column("Open Ports", width=150, anchor='center')
        self.tree.column("Detected By", width=120, anchor='center')
        self.tree.column("Time", width=140, anchor='center')
        
        # شريط تمرير
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="left", fill="y")
        self.tree.pack(side="right", fill="both", expand=True)
        
        # إطار أزرار إضافية
        extra_btn_frame = ttk.Frame(root)
        extra_btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(extra_btn_frame, text="حفظ النتائج إلى CSV", command=self.save_to_csv).pack(side="right", padx=5)
        ttk.Button(extra_btn_frame, text="مسح الجدول", command=self.clear_table).pack(side="right", padx=5)
        ttk.Button(extra_btn_frame, text="تفاصيل الجهاز", command=self.show_device_details).pack(side="right", padx=5)
        
        # سجل الأحداث
        log_frame = ttk.LabelFrame(root, text="سجل العمليات", padding=10)
        log_frame.pack(fill="x", padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state="normal", wrap=tk.WORD)
        self.log_text.pack(fill="both", expand=True)
        
        # تحديث قائمة الواجهات
        self.refresh_interfaces()
    
    def log(self, message, level="info"):
        """إضافة رسالة إلى سجل العمليات"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def refresh_interfaces(self):
        """تحديث قائمة الواجهات بأسماء مفهومة"""
        if not SCAPY_AVAILABLE:
            self.log("Scapy غير متوفر، لا يمكن عرض الواجهات", "error")
            self.iface_combo['values'] = ["Scapy not available"]
            return
        
        try:
            interfaces = get_interfaces_with_friendly_names()
            items = []
            self.iface_map.clear()
            
            # تخزين الخريطة للاستخدام لاحقاً
            for name, ip in interfaces:
                if ip and ip != "No IP":
                    display = f"{name} ({ip})"
                else:
                    display = name
                items.append(display)
                self.iface_map[display] = name
            
            self.iface_combo['values'] = items
            if items:
                self.iface_combo.current(0)
                self.log(f"تم العثور على {len(items)} واجهة")
            else:
                self.log("لم يتم العثور على واجهات", "error")
        except Exception as e:
            self.log(f"خطأ في قراءة الواجهات: {e}", "error")
    
    def get_selected_interface(self):
        """استخراج اسم الواجهة الفعلي من العنصر المختار"""
        selected = self.iface_var.get()
        if not selected:
            return None
        
        # استخدام الخريطة إن وجدت
        if selected in self.iface_map:
            return self.iface_map[selected]
        
        # بدلاً من ذلك، نعود للطريقة القديمة
        if ' (' in selected:
            return selected.split(' (')[0]
        return selected
    
    def start_discovery(self):
        if self.scanning:
            messagebox.showinfo("معلومات", "عملية اكتشاف قيد التشغيل بالفعل")
            return
        
        if not SCAPY_AVAILABLE:
            messagebox.showerror("خطأ", 
                "مكتبة Scapy غير متوفرة.\n\n"
                "للتثبيت: pip install scapy\n"
                "ثم أعد تشغيل البرنامج كمدير (Run as Administrator)")
            return
        
        iface_name = self.get_selected_interface()
        if not iface_name:
            messagebox.showerror("خطأ", "الرجاء اختيار واجهة شبكة صحيحة")
            return
        
        # مسح النتائج السابقة
        self.discovered_devices = {}
        self.clear_table()
        self.scanning = True
        self.start_btn.config(state="disabled", text="جارٍ الاكتشاف...")
        self.restart_btn.config(state="disabled")
        self.status_label.config(text="قيد التشغيل...", foreground="orange")
        self.log(f"بدء الاكتشاف على الواجهة: {iface_name}")
        
        # تشغيل عملية الاكتشاف في thread منفصل
        self.current_thread = threading.Thread(target=self.run_discovery, args=(iface_name,), daemon=True)
        self.current_thread.start()
    
    def run_discovery(self, iface_name):
        """تنفيذ عملية الاكتشاف مع الإضافة الفورية للنتائج"""
        try:
            from scapy.all import conf, sniff, ARP, Ether, srp, IP
            conf.iface = iface_name
            
            discovered = set()
            
            def packet_handler(packet):
                if ARP in packet:
                    src_ip = packet[ARP].psrc
                    src_mac = packet[ARP].hwsrc
                    if src_ip and src_ip != "0.0.0.0" and src_ip not in discovered:
                        discovered.add(src_ip)
                        # إضافة فورية إلى الجدول
                        self.root.after(0, self.add_device_immediate, src_ip, src_mac, 'ARP')
                elif IP in packet:
                    src_ip = packet[IP].src
                    if src_ip not in discovered and src_ip not in ["0.0.0.0", "255.255.255.255"]:
                        discovered.add(src_ip)
                        mac = packet.src if Ether in packet else "Unknown"
                        self.root.after(0, self.add_device_immediate, src_ip, mac, 'IP')
            
            self.log("بدء الاستماع السلبي لمدة 45 ثانية...")
            self.log("نصيحة: أعد تشغيل الجهاز المجهول (كاميرا/راوتر) الآن!")
            
            try:
                sniff(iface=iface_name, prn=packet_handler, store=False, timeout=45, filter="arp or ip")
            except Exception as e:
                self.log(f"خطأ في السنيفر: {e}", "error")
            
            # إذا لم نجد شيئاً، نقوم بمسح ARP
            if not discovered:
                self.log("لم يتم اكتشاف أجهزة بالاستماع، جارٍ المسح النشط...")
                networks = ["169.254.1.0/24", "192.168.1.0/24", "192.168.0.0/24", "10.0.0.0/24"]
                
                for net in networks:
                    self.log(f"مسح ARP على {net}")
                    try:
                        arp = ARP(pdst=net)
                        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
                        result = srp(ether/arp, timeout=3, verbose=False, retry=1)[0]
                        for _, rcv in result:
                            ip = rcv.psrc
                            mac = rcv.hwsrc
                            if ip not in discovered:
                                discovered.add(ip)
                                self.root.after(0, self.add_device_immediate, ip, mac, 'ARP Scan')
                    except Exception as e:
                        self.log(f"خطأ في مسح {net}: {e}", "error")
            
            self.log(f"تم اكتشاف {len(discovered)} جهاز.")
            
        except Exception as e:
            self.log(f"خطأ في عملية الاكتشاف: {e}", "error")
        finally:
            self.scanning = False
            self.root.after(0, self.discovery_finished)
    
    def add_device_immediate(self, ip, mac, detection_method):
        """إضافة جهاز إلى الجدول فوراً (مع تحليل سريع)"""
        if ip in self.discovered_devices:
            return
        
        # تحليل سريع (منافذ)
        device_type = "Unknown"
        open_ports = []
        try:
            device_type, open_ports = scan_ports(ip, timeout=1)
        except Exception as e:
            self.log(f"خطأ في فحص منافذ {ip}: {e}", "error")
        
        vendor = get_vendor(mac)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.discovered_devices[ip] = {
            'mac': mac,
            'vendor': vendor,
            'device_type': device_type,
            'open_ports': open_ports,
            'detected_by': detection_method,
            'time': now_str
        }
        
        ports_str = ', '.join(map(str, open_ports)) if open_ports else "None"
        self.tree.insert("", "end", values=(
            ip, mac, vendor, device_type, ports_str, detection_method, now_str
        ))
        self.log(f"تم اكتشاف {ip} ({vendor}) - {device_type}")
    
    def discovery_finished(self):
        """انتهاء عملية الاكتشاف"""
        self.start_btn.config(state="normal", text="بدء الاكتشاف")
        self.restart_btn.config(state="normal")
        if self.discovered_devices:
            self.status_label.config(text=f"اكتمل: {len(self.discovered_devices)} جهاز", foreground="green")
            self.log(f"اكتمل الاكتشاف بنجاح. تم العثور على {len(self.discovered_devices)} جهاز")
        else:
            self.status_label.config(text="لم يتم اكتشاف أجهزة", foreground="red")
            self.log("لم يتم اكتشاف أي أجهزة. تأكد من التوصيل وأعد تشغيل الجهاز المجهول")
    
    def clear_table(self):
        """مسح الجدول"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.discovered_devices = {}
        self.log("تم مسح الجدول")
    
    def save_to_csv(self):
        """حفظ النتائج إلى ملف CSV"""
        if not self.discovered_devices:
            messagebox.showinfo("لا توجد بيانات", "لا توجد أجهزة لحفظها")
            return
        
        filename = f"devices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["IP", "MAC", "Vendor", "Device Type", "Open Ports", "Detected By", "Time"])
                for ip, info in self.discovered_devices.items():
                    writer.writerow([
                        ip,
                        info['mac'],
                        info['vendor'],
                        info['device_type'],
                        ', '.join(map(str, info['open_ports'])) if info['open_ports'] else "",
                        info['detected_by'],
                        info['time']
                    ])
            messagebox.showinfo("تم الحفظ", f"تم حفظ النتائج في:\n{filename}")
            self.log(f"تم حفظ النتائج في {filename}")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل الحفظ: {e}")
            self.log(f"فشل الحفظ: {e}", "error")
    
    def show_device_details(self):
        """عرض تفاصيل الجهاز المحدد"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("تحديد", "الرجاء تحديد جهاز من الجدول أولاً")
            return
        
        item = selected[0]
        values = self.tree.item(item, "values")
        if not values:
            return
        
        ip = values[0]
        info = self.discovered_devices.get(ip)
        if not info:
            return
        
        details = f"""تفاصيل الجهاز: {ip}

IP Address: {ip}
MAC Address: {info['mac']}
الشركة المصنعة: {info['vendor']}
نوع الجهاز: {info['device_type']}
المنافذ المفتوحة: {', '.join(map(str, info['open_ports'])) if info['open_ports'] else 'لا يوجد'}
طريقة الاكتشاف: {info['detected_by']}
وقت الاكتشاف: {info['time']}

نصائح:
• جرب فتح المتصفح على http://{ip}
• إذا كانت كاميرا: rtsp://{ip}
• استخدم الأمر: ping {ip}"""
        
        messagebox.showinfo(f"تفاصيل الجهاز {ip}", details)
    
    def restart_app(self):
        """إعادة تشغيل البرنامج دون إغلاق النافذة"""
        if self.scanning:
            messagebox.showinfo("معلومات", "لا يمكن إعادة التشغيل أثناء الاكتشاف. انتظر حتى الانتهاء.")
            return
        # إعادة تعيين الحالة
        self.clear_table()
        self.discovered_devices = {}
        self.status_label.config(text="جاهز", foreground="green")
        self.log_text.delete(1.0, tk.END)
        self.log("تم إعادة تشغيل البرنامج")
        # تحديث الواجهات
        self.refresh_interfaces()

def main():
    root = tk.Tk()
    
    # ضبط الخط والإعدادات الأساسية
    root.option_add('*font', 'Tahoma 10')
    
    # محاولة ضبط اتجاه النص للعربية (إذا كان النظام يدعم)
    try:
        root.tk.call('::tk::unsupported::TextDontWrap', 1)
    except:
        pass
    
    # إنشاء التطبيق
    app = IPFinderApp(root)
    
    # رسالة ترحيب
    if not SCAPY_AVAILABLE:
        messagebox.showwarning("Scapy غير متوفر", 
            "مكتبة Scapy غير مثبتة.\n\n"
            "لتثبيتها: افتح موجه الأوامر كمدير واكتب:\n"
            "pip install scapy\n\n"
            "ثم أعد تشغيل البرنامج كمدير (Run as Administrator)")
    else:
        if os.name == 'nt':
            try:
                import ctypes
                if not ctypes.windll.shell32.IsUserAnAdmin():
                    messagebox.showwarning("صلاحيات مدير", 
                        "البرنامج لم يتم تشغيله كمدير.\n\n"
                        "قد لا تعمل خاصية الاستماع بشكل صحيح.\n"
                        "يرجى إعادة تشغيل البرنامج كمدير (Run as Administrator)\n"
                        "للحصول على أفضل النتائج.")
            except:
                pass
    
    root.mainloop()

if __name__ == "__main__":
    main()