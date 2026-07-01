```markdown
# 🔐 SVWL – Streamlit Vulnerable Web Lab
## OWASP Top 10 2025 – Interactive Security Learning Platform

> An interactive web security learning platform built with Python and Streamlit[cite: 2, 3].

---

## 📦 Installation & Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
streamlit run app.py

```

---

## 🎯 Available Modules

| Code | OWASP Category | Exploitation Technique | Points |
| --- | --- | --- | --- |
| A01 | Broken Access Control | IDOR – ID manipulation | 100 |
| A02 | Cryptographic Failures | MD5 rainbow table crack | 100 |
| A03 | Injection | SQL Injection – auth bypass | 100 |
| A04 | Insecure Design | Brute force OTP (no rate limit) | 100 |
| A05 | Security Misconfiguration | Debug endpoint exposure | 100 |
| A06 | Vulnerable & Outdated Components | Log4Shell JNDI injection sim. | 100 |
| A07 | XSS / Injection (Output) | Stored XSS via HTML injection | 100 |
| A08 | SSRF | AWS metadata service access | 100 |
| A09 | Logging & Monitoring Failures | Undetected malicious actions | 100 |
| A10 | Auth Failures + JWT | JWT None Algorithm Attack | 100 |

**Total: 1000 points**

---

## 🛡️ Security Levels

* **Low** → Vulnerable implementation configured for exploitation and learning.


* **Medium** → Partial protection featuring existing bypasses.


* **High** → Secure implementation serving as a best practice reference.



---

## ⚠️ DISCLAIMER

This platform is developed **strictly for cybersecurity educational purposes**. All vulnerabilities are simulated within an isolated laboratory environment. Do not apply these exploitation techniques to unauthorized external systems.

```

```