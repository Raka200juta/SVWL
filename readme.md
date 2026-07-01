# 🔐 SVWL – Streamlit Vulnerable Web Lab
## OWASP Top 10 2025 – Interactive Security Learning Platform

> Platform edukasi keamanan web interaktif berbasis Python + Streamlit,
> terinspirasi dari DVWA (Damn Vulnerable Web Application).

---

## 📦 Instalasi & Menjalankan

```bash
# 1. Clone atau copy file
pip install -r requirements.txt

# 2. Jalankan lab
streamlit run app.py
```

---

## 🎯 Modul yang Tersedia

| Kode | Kategori OWASP                         | Teknik Eksploitasi              | Poin |
|------|----------------------------------------|---------------------------------|------|
| A01  | Broken Access Control                  | IDOR – ID manipulation          | 100  |
| A02  | Cryptographic Failures                 | MD5 rainbow table crack         | 100  |
| A03  | Injection                              | SQL Injection – auth bypass     | 100  |
| A04  | Insecure Design                        | Brute force OTP (no rate limit) | 100  |
| A05  | Security Misconfiguration              | Debug endpoint exposure         | 100  |
| A06  | Vulnerable & Outdated Components       | Log4Shell JNDI injection sim.  | 100  |
| A07  | XSS / Injection (Output)               | Stored XSS via HTML injection   | 100  |
| A08  | SSRF                                   | AWS metadata service access     | 100  |
| A09  | Logging & Monitoring Failures          | Undetected malicious actions    | 100  |
| A10  | Auth Failures + JWT                    | JWT None Algorithm Attack       | 100  |

**Total: 1000 poin**

---

## 🛡️ Level Keamanan

- **Low** → Implementasi rentan (untuk eksploitasi dan pembelajaran)
- **Medium** → Proteksi parsial (masih ada celah)
- **High** → Implementasi aman (sebagai referensi best practice)

---

## ⚠️ DISCLAIMER

Platform ini dibuat **HANYA untuk tujuan edukasi keamanan siber**.
Semua kerentanan adalah simulasi dalam lingkungan terisolasi (tanpa koneksi nyata).
Jangan terapkan teknik ini pada sistem yang bukan milik Anda.