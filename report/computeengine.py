import json
from datetime import datetime



def get_navigation(active_page):
    """Return navigation HTML with the specified page marked as active."""
    nav_items = {
        "iam": ("iam-perm.html", "bi-key", "IAM"),
        "storage": ("cloud-storage-buckets.html", "bi-archive", "Storage"),
        "compute": ("compute-engine.html", "bi-pc", "Compute"),
        "cloud-run": ("cloud-run.html", "bi-cloud", "Cloud Run")
    }

    nav_links = "\n".join([
        f'''          <li class="nav-item">
            <a class="nav-link {"active" if page == active_page else ""}" href="{href}">
              <i class="bi {icon}"></i>{label}
            </a>
          </li>'''
        for page, (href, icon, label) in nav_items.items()
    ])

    return f"""
  <!-- Navigation -->
  <nav class="navbar navbar-expand-lg navbar-light fixed-top">
    <div class="container">
      <a class="navbar-brand" href="index.html">
        <i class="bi bi-shield-check"></i>GCP Security Report
      </a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
{nav_links}
        </ul>
      </div>
    </div>
  </nav>
"""


def get_footer(generated_on):
    """Return footer HTML with the specified generation timestamp."""
    return f"""
  <!-- Footer -->
  <footer>
    <div class="container">
      <div class="row">
        <div class="col-md-6">
          <p class="footer-text"><i class="bi bi-shield-check"></i>GCP Security Report</p>
        </div>
        <div class="col-md-6 text-md-end">
          <p class="mb-0">Generated on {generated_on}</p>
        </div>
      </div>
    </div>
  </footer>
"""


def get_css_styles():
    """Return CSS styles for consistent report styling."""
    with open("report/styles.css", "r") as css_file:
        return f"<style>\n{css_file.read()}\n</style>"


def generate_compute_report(generated_on):
    """Generate security report for Compute Engine instances."""
    try:
        with open('/home/hac/Desktop/New_ssd_backup/automated-cloud-misconfiguration-testing/compute_instances.json') as f:
            instances = json.load(f)
    except FileNotFoundError:
        print("⚠️ Compute instance data file not found. Skipping Compute report.")
        return

    total_instances = len(instances)
    default_sa_count = sum(i.get("is_default_sa") for i in instances)
    public_ip_count = sum(any(n.get("external_ips") for n in i.get("networking", [])) for i in instances)
    high_risk_count = sum(
        i.get("is_default_sa") and any(n.get("external_ips") for n in i.get("networking", []))
        for i in instances
    )

    summary_cards = f"""
    <!-- Summary Cards -->
    <div class="row mb-5">
      <div class="col-md-4">
        <div class="summary-card">
          <div class="summary-icon icon-primary"><i class="bi bi-hdd"></i></div>
          <h5 class="card-title">Total Instances</h5>
          <div class="display-4">{total_instances}</div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="summary-card">
          <div class="summary-icon icon-success"><i class="bi bi-person-badge"></i></div>
          <h5 class="card-title">Default SA Used</h5>
          <div class="display-4">{default_sa_count}</div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="summary-card">
          <div class="summary-icon icon-danger"><i class="bi bi-exclamation-triangle"></i></div>
          <h5 class="card-title">High Risk</h5>
          <div class="display-4">{high_risk_count}</div>
        </div>
      </div>
    </div>
    """

    instance_cards = "\n".join([
        f"""
      <div class="card">
        <div class="card-header">{i["name"]} <span class="badge bg-secondary ms-2">{i["zone"]}</span></div>
        <div class="card-body">
          <p><strong>Service Account:</strong> {i["service_accounts"]}</p>
          <p><strong>Public IPs:</strong> {", ".join(ip for n in i["networking"] for ip in n["external_ips"]) or "None"}</p>
          <p><strong>Metadata</strong> {i["metadata"]}</p>


        </div>
      </div>"""
        for i in instances
    ])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GCP Security Report | Compute Engine</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">

  <style>
    :root {{
      --bs-primary: #4285f4;
      --bs-secondary: #34a853;
      --bs-warning: #fbbc05;
      --bs-danger: #ea4335;
      --card-shadow: 0 6px 18px rgba(0,0,0,0.08);
      --transition-speed: 0.3s;
      --border-radius: 12px;
    }}
    
    body {{
      font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
      background-color: #f8f9fa;
      position: relative;
      min-height: 100vh;
    }}
    
    .navbar {{
      backdrop-filter: blur(10px);
      background-color: rgba(255, 255, 255, 0.85) !important;
      box-shadow: 0 2px 15px rgba(0,0,0,0.05);
      transition: all 0.4s ease;
    }}
    
    .navbar-brand {{
      font-weight: 700;
      color: var(--bs-primary) !important;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    
    .navbar-brand i {{
      font-size: 1.5rem;
    }}
    
    .nav-link {{
      font-weight: 500;
      color: #5f6368 !important;
      transition: all var(--transition-speed);
      border-radius: 6px;
      padding: 8px 15px !important;
      margin: 0 5px;
      position: relative;
    }}
    
    .nav-link:hover {{
      color: var(--bs-primary) !important;
      background-color: rgba(66, 133, 244, 0.08);
    }}
    
    .nav-link.active {{
      color: var(--bs-primary) !important;
      background-color: rgba(66, 133, 244, 0.12);
    }}
    
    .nav-link i {{
      margin-right: 8px;
      font-size: 1.1rem;
    }}
    
    .animated-gradient {{
      background: linear-gradient(-45deg, #4285f4, #34a853, #fbbc05, #ea4335);
      background-size: 400% 400%;
      animation: gradient 15s ease infinite;
      height: 6px;
      width: 100%;
      position: absolute;
      top: 0;
      left: 0;
    }}
    
    @keyframes gradient {{
      0% {{
        background-position: 0% 50%;
      }}
      50% {{
        background-position: 100% 50%;
      }}
      100% {{
        background-position: 0% 50%;
      }}
    }}
    
    .page-header {{
      background: linear-gradient(135deg, rgba(66, 133, 244, 0.05) 0%, rgba(52, 168, 83, 0.05) 100%);
      padding: 3rem 0;
      margin-bottom: 2rem;
      border-radius: var(--border-radius);
    }}

    .page-header h1 {{
      font-weight: 700;
      color: #202124;
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .page-header .badge {{
      font-size: 1rem;
      padding: 0.6rem 1rem;
      border-radius: 30px;
    }}
    
    .card {{
      border: none;
      border-radius: var(--border-radius);
      box-shadow: var(--card-shadow);
      margin-bottom: 2rem;
      overflow: hidden;
      transition: all var(--transition-speed);
    }}
    
    .card:hover {{
      transform: translateY(-5px);
      box-shadow: 0 12px 24px rgba(0,0,0,0.12);
    }}
    
    .card-header {{
      border-bottom: 1px solid rgba(0,0,0,0.05);
      background-color: white;
      font-weight: 600;
      padding: 1rem 1.5rem;
    }}
    
    .card-body {{
      padding: 1.5rem;
    }}
    
    .summary-card {{
      text-align: center;
      height: 100%;
      padding: 1.5rem;
      border-radius: var(--border-radius);
      box-shadow: var(--card-shadow);
      background-color: white;
      transition: all var(--transition-speed);
    }}
    
    .summary-card:hover {{
      transform: translateY(-5px);
      box-shadow: 0 12px 24px rgba(0,0,0,0.12);
    }}
    
    .summary-card i {{
      font-size: 2.2rem;
      margin-bottom: 1rem;
    }}
    
    .summary-card .display-4 {{
      font-weight: 700;
      color: var(--bs-primary);
    }}
    
    .summary-card .card-title {{
      font-weight: 600;
      color: #202124;
      display: flex;
      align-items: center;
      gap: 8px;
      justify-content: center;
      margin-bottom: 1rem;
    }}
    
    .summary-icon {{
      width: 70px;
      height: 70px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 1rem;
    }}
    
    .icon-primary {{
      background-color: rgba(66, 133, 244, 0.1);
      color: var(--bs-primary);
    }}
    
    .icon-success {{
      background-color: rgba(52, 168, 83, 0.1);
      color: var(--bs-secondary);
    }}
    
    .icon-warning {{
      background-color: rgba(251, 188, 5, 0.1);
      color: var(--bs-warning);
    }}
    
    .icon-danger {{
      background-color: rgba(234, 67, 53, 0.1);
      color: var(--bs-danger);
    }}
    
    .badge {{
      padding: 0.5rem 0.8rem;
      font-weight: 500;
      border-radius: 30px;
    }}
    
    .badge-public {{
      background-color: var(--bs-danger);
    }}
    
    .badge-private {{
      background-color: var(--bs-secondary);
    }}
    
    .risk-indicator {{
      width: 24px;
      height: 24px;
      border-radius: 50%;
      display: inline-block;
      margin-right: 10px;
      vertical-align: middle;
    }}
    
    .risk-high {{
      background-color: var(--bs-danger);
    }}
    
    .risk-medium {{
      background-color: var(--bs-warning);
    }}
    
    .risk-low {{
      background-color: var(--bs-secondary);
    }}
    
    .legend-item {{
      display: inline-flex;
      align-items: center;
      margin-right: 1.5rem;
      font-weight: 500;
    }}

    footer {{
      background-color: #202124;
      color: #ffffff;
      padding: 2rem 0;
      position: relative;
      margin-top: 4rem;
    }}
    
    .footer-text {{
      margin-bottom: 0;
      display: flex;
      align-items: center;
    }}
    
    .footer-text i {{
      margin-right: 10px;
      font-size: 1.2rem;
    }}
    
    table.table {{
      border-radius: var(--border-radius);
      overflow: hidden;
    }}
    
    table.table thead th {{
      background-color: rgba(66, 133, 244, 0.05);
      border-bottom: none;
      padding: 0.75rem 1.5rem;
      font-weight: 600;
    }}
    
    table.table tbody tr {{
      transition: all var(--transition-speed);
    }}
    
    table.table tbody tr:hover {{
      background-color: rgba(66, 133, 244, 0.05);
    }}
    
    table.table td {{
      padding: 1rem 1.5rem;
      vertical-align: middle;
    }}
    
    .public-access {{
      color: var(--bs-danger);
      font-weight: 500;
    }}
    
    .private-access {{
      color: var(--bs-secondary);
      font-weight: 500;
    }}
    
    .bucket-icon {{
      font-size: 1.3rem;
      margin-right: 0.5rem;
    }}
    
    .bucket-row-public {{
      background-color: rgba(234, 67, 53, 0.05);
    }}
  </style>


</head>
<body>
  <div class="animated-gradient"></div>
  {get_navigation("compute")}
  <div class="container" style="padding-top: 80px;">
    <div class="page-header">
      <div class="container">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1><i class="bi bi-pc"></i> Compute Engine Instances</h1>
            <p class="text-muted">Generated on {generated_on}</p>
          </div>
          <div>
            <span class="badge bg-primary">{total_instances} instances</span>
          </div>
        </div>
      </div>
    </div>
    {summary_cards}
    {instance_cards}
  </div>
  {get_footer(generated_on)}
</body>
</html>
"""

    with open("report/report/compute-engine.html", "w") as f:
        f.write(html_content)
        print("✅ Compute Engine report generated: compute-engine.html")


generate_compute_report(datetime)