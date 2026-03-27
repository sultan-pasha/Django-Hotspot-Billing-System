# 🌐 SINKROW: Enterprise-Grade Hotspot Billing & Management System

[![Project Demo](https://img.shields.io/badge/Demo-Watch%20on%20YouTube-red?style=for-the-badge&logo=youtube)](https://youtu.be/1IVa3OVKIIY)

## 📌 Project Overview
**SINKROW** is a centralized network management platform designed to handle complex authentication and billing for large-scale Hotspot networks. Built with a "Security-First" approach, it replaces traditional closed-source solutions (like MikroTik) with a fully customizable, Linux-based architecture.

This project was successfully deployed and recognized by **Minia University** for solving real-world connectivity and user management challenges.

---

## 🏗️ Technical Architecture
The system operates on a multi-layer stack to ensure zero-downtime and high scalability:
- **Core Engine:** Python 3.13 / Django 5.x
- **AAA Protocol:** FreeRADIUS (Integrated via Django ORM)
- **Network Gateway:** CoovaChilli (Captive Portal)
- **Traffic Control:** Linux `iptables` & `systemd` automation
- **Frontend:** React.js + Redux for real-time data visualization

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

## 📸 Project Gallery
#[https://drive.google.com/file/d/1RsXctbVS5dC2IZMZFRnddEyfwNXX04ev/view?usp=sharing]

---

## 👤 Author
**Sultan Abdelkareem**
*Senior Full-Stack Engineer | Founder of SASKE Company*
[LinkedIn](https://www.linkedin.com/in/sultan-abd-alkareem/) | [Portfolio](https://effulgent-shortbread-2bf423.netlify.app)
