# IP-Finder
IP Finder – A GUI tool to discover any network device (IP cameras, routers, etc.) regardless of its IP range. Uses ARP sniffing/scanning, displays MAC vendor, device type, open ports, and exports results to CSV.


# 🔍 IP Finder - Network Device Discovery Tool

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg)]()

> أداة رسومية احترافية لاكتشاف أي جهاز على الشبكة (كاميرات مراقبة، راوترات، أجهزة إنترنت الأشياء) بغض النظر عن نطاق IP الخاص به.

## ✨ المميزات

| الميزة | الوصف |
|--------|-------|
| 🎯 **كشف تلقائي** | يكتشف الأجهزة دون الحاجة لمعرفة النطاق المسبق |
| 📡 **وضعان للكشف** | استماع سلبي (Sniffer) + مسح نشط (ARP Scan) |
| 🏭 **معرفة الشركة** | يستخرج الشركة المصنعة من عنوان MAC (قاعدة بيانات OUI) |
| 🖥️ **تحديد نوع الجهاز** | يميز بين كاميرات IP، راوترات، طابعات، سيرفرات |
| 🔌 **فحص المنافذ** | يعرض المنافذ المفتوحة (HTTP, RTSP, SSH, وغيرها) |
| 💾 **حفظ النتائج** | تصدير النتائج إلى ملف CSV |
| 🌐 **واجهة عربية** | واجهة رسومية سهلة الاستخدام (Tkinter) |

## 🚀 طريقة الاستخدام

### المتطلبات الأساسية
- نظام تشغيل Windows / Linux
- Python 3.8 أو أحدث
- صلاحيات المدير (لعمل السنيفر)

### التثبيت والتشغيل

```bash
# 1. استنساخ المشروع
git clone https://github.com/syfd74582/IP-Finder.git
cd IP-Finder

# 2. إنشاء بيئة افتراضية (مستحسن)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. تثبيت المتطلبات
pip install -r requirements.txt

# 4. تشغيل البرنامج
python ip_finder.py
```

> **ملاحظة مهمة:** على نظام Windows، يُفضل تشغيل البرنامج كمدير (Run as Administrator) لضمان عمل خاصية الاستماع السلبي بشكل صحيح.

## 🖥️ لقطة شاشة

```
┌─────────────────────────────────────────────────────────────────┐
│  🔍 IP Finder - كشف أجهزة الشبكة                        ─ □ × │
├─────────────────────────────────────────────────────────────────┤
│  واجهة الشبكة: [Ethernet (192.168.1.100)          ▼] [تحديث]   │
│                                                                  │
│  [▶ بدء الاكتشاف] [🔄 إعادة تشغيل]        الحالة: ✓ جاهز       │
│                                                                  │
│  ════════════════════════════════════════════════════════════   │
│  │ IP           │ MAC               │ الشركة      │ النوع    │  │
│  │ 192.168.1.1  │ 00:1C:9E:XX:XX:XX │ Hikvision   │ Camera   │  │
│  │ 192.168.1.2  │ 70:56:81:XX:XX:XX │ TP-Link     │ Router   │  │
│  │ 192.168.1.5  │ 00:15:5D:XX:XX:XX │ Microsoft   │ Generic  │  │
│  ════════════════════════════════════════════════════════════   │
│                                                                  │
│  [💾 حفظ CSV] [🗑 مسح] [📋 تفاصيل]                              │
│                                                                  │
│  [سجل العمليات]                                                 │
│  [14:30:01] بدء الاكتشاف على الواجهة: Ethernet                  │
│  [14:30:15] جهاز جديد: 192.168.1.1 (Hikvision) - Camera        │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 قاعدة بيانات الشركات المصنعة (OUI)

يدعم البرنامج التعرف على أكثر من 50 شركة مصنعة، منها:

| الشركة | الاختصار |
|--------|----------|
| Hikvision | كاميرات مراقبة |
| Dahua | كاميرات مراقبة |
| TP-Link | راوترات، مفاتيح شبكة |
| Cisco | أجهزة شبكة احترافية |
| Ubiquiti | نقاط وصول لاسلكية |
| Apple | أجهزة آبل |
| Samsung | أجهزة متنوعة |
| Netgear | أجهزة شبكة |
| MikroTik | أجهزة شبكة |
| Axis Communications | كاميرات IP |

## 🔧 بنية المشروع

```
IP-Finder/
├── ip_finder.py          # الملف الرئيسي للبرنامج
├── requirements.txt      # الاعتماديات المطلوبة
├── README.md             # توثيق المشروع
├── LICENSE               # ترخيص MIT
└── .gitignore            # ملفات مستثناة من git
```

## 📝 الاعتماديات (Dependencies)

```txt
scapy>=2.4.5    # للتعامل مع حزم الشبكة (ARP, Sniffer)
```

> **ملاحظة:** البرنامج لا يعتمد على `netifaces` لتجنب مشاكل التوافق مع Windows.

## 🤝 المساهمة في التطوير

1. Fork المشروع
2. إنشاء فرع جديد (`git checkout -b feature/amazing`)
3. إجراء التغييرات (`git commit -m 'Add amazing feature'`)
4. رفع التغييرات (`git push origin feature/amazing`)
5. فتح Pull Request

## 📧 التواصل

- **المطور:** syfd74582
- **البريد الإلكتروني:** [your-email@example.com]
- **GitHub:** [github.com/syfd74582](https://github.com/syfd74582)

## 📜 الترخيص

هذا المشروع مرخص تحت رخصة **MIT License** - راجع ملف [LICENSE](LICENSE) للتفاصيل.

---

<div align="center">
  <sub>Built with ❤️ by syfd74582</sub>
</div>
```

