# 🌐 SINKROW – Enterprise Hotspot Billing & Gateway (Django + FreeRADIUS)

This is a **public demo version** of a professional network management and billing system originally developed for SASKE Company and deployed at **Minia University**.

The system demonstrates advanced backend architecture, real-time AAA authentication, and seamless integration between high-level web frameworks and low-level network protocols.

> 🛡️ The original production source code and sensitive security configurations are private.  
> This repository is for professional portfolio showcasing and technical evaluation purposes only.

---

## 📌 Live Demo & Overview

🟢 **Video Demo**: [SINKROW Final Showcase](https://youtu.be/1IVa3OVKIIY)  
📌 **Note**: The system manages real-time hardware interfaces. This demo highlights the software architecture and the management dashboard.

---

## 🎯 Project Overview

**SINKROW** is designed to provide a robust alternative to proprietary hotspot solutions. It handles user authentication, session management, and bandwidth billing through a centralized Django-based platform.  
It was specifically engineered to solve connectivity challenges in high-traffic environments, supporting **50+ concurrent locations** with centralized data tracking.

---

## 🧠 Key Features

- 🔐 **Advanced AAA Integration**: Dynamic management of FreeRADIUS via Django ORM.
- 📊 **Real-Time Usage Monitoring**: Live tracking of data consumption and session time.
- 🛠️ **Network Automation**: Automated handling of `iptables` rules and `coovachilli` configurations.
- 🚦 **Bandwidth Control**: Multi-tier subscription plans with speed limiting.
- 🖥️ **Centralized Admin Dashboard**: Full control over users, vouchers, and site-wide analytics.
- 🚀 **Infrastructure as Code**: Managed via Systemd units and custom automation scripts.

---

## 🛠️ Key Engineering Challenges Solved

### 1. Unified Authentication (Django + RADIUS)
I engineered a bridge between the **Django ORM** and **FreeRADIUS** to allow real-time user validation. This includes custom `RadCheck` and `RadReply` logic to manage sessions dynamically.

### 2. Real-Time Data Tracking
Implemented a background service to monitor data consumption. The dashboard provides users with real-time feedback on:
- 📊 **Bandwidth Consumption**
- ⏳ **Remaining Session Time**
- 🚀 **Connection Speed Tiers**

### 3. Infrastructure Automation (DevOps)
Automated the persistence of firewall rules and network gateway services using **Systemd units** and custom **Bash scripts**, ensuring the system recovers instantly after any reboot.

---

## 📈 Performance & Impact
- **Scalability:** Supports 50+ concurrent hotspot locations from a single dashboard.
- **Reliability:** Achieved 99.9% uptime by migrating from legacy hardware-specific software to a robust Linux-based stack.
- **Optimization:** 40% improvement in authentication speed compared to default RADIUS configurations.

---

## 🛠️ Tech Stack

| Layer          | Technologies Used                                      |
|----------------|--------------------------------------------------------|
| **Core Backend**| Python (v3.13), Django (v5.x)                         |
| **Database** | MySQL / PostgreSQL (Optimized for Radius schemas)      |
| **AAA Server** | FreeRADIUS (Integrated with Django Backend)            |
| **Hotspot GW** | CoovaChilli (Captive Portal Gateway)                   |
| **Networking** | Linux `iptables`, DNS Redirect, Systemd Services       |
| **OS / Environment**| Ubuntu Server 24.04 LTS, Proxmox VE, Docker        |
| **Dashboard UI**| Django Templates, Bootstrap 5, Chart.js                |
| **Testing** | Django Test Suite (Unit & Integration tests)           |

---

## 📂 Project Structure

```bash
sinkrow-hotspot/
├── core/                # Global Django settings and config
├── apps/
│   ├── accounts/        # User profiles and AAA logic
│   ├── billing/         # Subscription plans and data tracking
│   └── radius/          # FreeRADIUS bridge and schema management
├── services/            # Linux service files (systemd) and bash scripts
├── templates/           # Captive portal and admin dashboard views
├── static/              # Assets for the customized UI
├── docker/              # Deployment and orchestration files
├── tests/               # Backend logic and integration tests
├── manage.py
└── README.md

```
---

## 📸 Project Showcase

#[https://drive.google.com/file/d/1RsXctbVS5dC2IZMZFRnddEyfwNXX04ev/view?usp=sharing]

---

> 🛡️ **Intellectual Property Notice:**
> All architecture, network logic, and production implementations are the property of **Sultan Abdelkareem / SASKE Company**. Unauthorized commercial replication, redistribution, or reuse is strictly prohibited.

---

## 🔐 License

This project is released as a technical demo for professional review and portfolio purposes only.  
Please review the [LICENSE](./LICENSE) for full terms and restrictions.

---

# 👤 Author

## Sultan Abdelkareem
### Sr. Full-Stack Developer | Django, React, DevOps | 8+ Yrs
📧 sultanelsultan4@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/sultan-abd-alkareem/)  
🌐 [Portfolio](https://effulgent-shortbread-2bf423.netlify.app)
