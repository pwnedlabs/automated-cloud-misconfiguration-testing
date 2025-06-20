# ☁️ Automated Cloud Misconfiguration Testing (Beta)

**Automated-cloud-misconfiguration-testing** is a security assessment tool currently focused on **Google Cloud Platform (GCP)**. It helps security professionals, red teamers, and cloud engineers **brute-force IAM permissions**, **enumerate services**, and **analyze misconfigurations** using predefined detection rules.

> ⚠️ Currently in **Beta** — expect active development and rapid changes.

---

## ⚠️ Disclaimer

> This tool is intended **solely for educational and ethical testing purposes**.
>
> Please use it **only in environments where you have explicit permission** to perform security testing.
>
> The author **does not hold any responsibility** for misuse or damage caused by unauthorized use of this tool.

---

## ✨ Features

✅ GCP Support:
- 🔐 IAM permission brute-forcing (`testIamPermissions`)
- 📦 Cloud Storage Bucket Enumeration
- 💻 Compute Engine Enumeration
- 🌐 App Engine Enumeration
- 🚀 Cloud Run Enumeration
- 📊 Auto-generated HTML Reports for all services
- 🧠 Rule-based analysis of dangerous/exploitable permissions

🔜 Upcoming:
- ☁️ Google Kubernetes Engine (GKE)
- 🔐 Secret Manager
- 🧩 Cloud Functions
---

## 📦 Directory Structure

```
.
├── main.py
├── modules/
│   ├── compute_engine_enum.py
│   ├── cloudrun.py
│   ├── ...
├── report/
│   ├── cloudstorage.py
│   ├── cloudrunreport.py
│   ├── computeengine.py
│   ├── iam.py
├── roles/
│   └── gcp/roles/*.json   # Role definition files
├── valid-gcp-perms.json   # Output permissions
├── bucket-output.json     # Required for storage reporting
└── ...
```

---

## 🚀 Quick Start

### 🔧 Requirements

```bash
pip install -r requirements.txt
```

### 🏁 Usage

```bash
python3 main.py \
  --access-token <ACCESS_TOKEN> \
  --project-id <PROJECT_ID> \
  --service-account-email <SA_EMAIL> \
  --auto-enum \
  --region <REGION>
```

https://github.com/user-attachments/assets/5cedf6a8-8fce-4806-8956-cf8e176b99fa



---

### 🛠 Supported Flags

| Flag | Description |
|------|-------------|
| `--csp` | Cloud provider (`gcp`, `aws`, `azure`) – default: `gcp` |
| `--bruteforce_gcp_iam` | Brute-force IAM permissions (`yes`/`no`) |
| `--enumerate-gcp` | Enable GCP enumeration – default: `yes` |
| `--access-token` | GCP OAuth2 access token |
| `--project-id` | Target GCP project |
| `--service-account-email` | Service account email (required for IAM testing) |
| `--roles-directory` | Directory containing IAM role definitions |
| `--gcp_permission_analyze` | Analyze GCP permissions using rule engine |
| `--auto-enum` | Auto-perform bruteforce, analysis, and service checks |
| `--region` | GCP region for regional services like Cloud Run |
| `--generate-report` | Generate HTML reports – default: `yes` |
| `--security-reviewer` | Identify misconfigs like over-privileged roles (Currently Not available in Beta) |

---

## 📄 Sample Output

- `valid-gcp-perms.json` – Brute-forced valid permissions
- `bucket-output.json` – Cloud Storage data (required for report)
- `reports/` – Auto-generated GCP misconfig report (coming soon)

---

## 📌 Notes

- `bucket-output.json` must exist to generate the Cloud Storage report.
- All reports are modular — you can import and run any individual report module from the `report/` directory.
- To extend the tool, just add new modules to `modules/` and integrate them via flags in `main.py`.

---

## 📚 Contributing

This tool is in early development. Contributions, issues, and feedback are welcome!

- Add new services under `modules/`
- Add new detection logic under `rules/`
- Improve reporting modules in `report/`

---

## 📜 License

MIT License — free to use, modify, and distribute.

---


