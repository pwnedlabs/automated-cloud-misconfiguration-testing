import json
from datetime import datetime
import os

def generate_iam_report():
    # Load IAM rules data
    with open('matches.json') as f:
        rules_data = json.load(f)
    
    # Load IAM permissions data
    with open('valid-gcp-perms.json') as f:
        permissions_data = json.load(f)

    generated_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create report directory if it doesn't exist
    os.makedirs("report", exist_ok=True)

    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GCP Security Report | IAM Permissions</title>
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
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    
    .card-header h5 {{
      margin: 0;
      font-weight: 600;
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
    
    .rule-card {{
      border-left: 4px solid var(--bs-warning);
      margin-bottom: 1.5rem;
      border-radius: 0 8px 8px 0;
      box-shadow: 0 4px 6px rgba(0,0,0,0.05);
      transition: all var(--transition-speed);
    }}
    
    .rule-card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 8px 15px rgba(0,0,0,0.08);
    }}
    
    .rule-card .card-header {{
      background-color: rgba(251, 188, 5, 0.05);
      border-bottom: 1px solid rgba(251, 188, 5, 0.1);
    }}
    
    .permission-list {{
      max-height: 500px;
      overflow-y: auto;
      padding-right: 10px;
    }}
    
    .permission-list::-webkit-scrollbar {{
      width: 8px;
    }}
    
    .permission-list::-webkit-scrollbar-track {{
      background: #f1f1f1;
      border-radius: 10px;
    }}
    
    .permission-list::-webkit-scrollbar-thumb {{
      background: #ccc;
      border-radius: 10px;
    }}
    
    .permission-list::-webkit-scrollbar-thumb:hover {{
      background: #aaa;
    }}
    
    .permission-item {{
      padding: 0.5rem 0.75rem;
      border-radius: 6px;
      margin-bottom: 0.5rem;
      background-color: rgba(66, 133, 244, 0.05);
      border-left: 3px solid var(--bs-primary);
      transition: all var(--transition-speed);
    }}
    
    .permission-item:hover {{
      background-color: rgba(66, 133, 244, 0.1);
      transform: translateX(3px);
    }}
    
    .rule-permissions {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-top: 0.75rem;
    }}
    
    .rule-permission-item {{
      padding: 0.3rem 0.6rem;
      border-radius: 4px;
      background-color: rgba(52, 168, 83, 0.05);
      border-left: 2px solid var(--bs-secondary);
      font-family: monospace;
      font-size: 0.9rem;
    }}
    
    .source-link {{
      margin-top: 0.5rem;
      display: inline-block;
      color: var(--bs-primary);
      text-decoration: none;
    }}
    
    .source-link:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>
  <!-- Animated Gradient Line -->
  <div class="animated-gradient"></div>
  
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
          <li class="nav-item">
            <a class="nav-link active" href="iam.html"><i class="bi bi-key"></i>IAM</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="cloud-storage-buckets.html"><i class="bi bi-archive"></i>Storage</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="compute-engine.html"><i class="bi bi-pc"></i>Compute</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="cloud-run.html"><i class="bi bi-cloud"></i>Cloud Run</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <div class="container" style="padding-top: 80px;">
    <!-- Header -->
    <div class="page-header">
      <div class="container">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1><i class="bi bi-key"></i>IAM Permissions</h1>
            <p class="text-muted">Generated on {generated_on}</p>
          </div>
          <div>
            <span class="badge bg-primary">{len(rules_data)} rules matched</span>
            <span class="badge bg-secondary">{len(permissions_data)} permissions</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="row mb-5">
      <div class="col-md-4">
        <div class="summary-card">
          <div class="summary-icon icon-warning">
            <i class="bi bi-shield-exclamation"></i>
          </div>
          <h5 class="card-title"><i class="bi bi-shield-exclamation"></i>Rules Matched</h5>
          <p class="display-4">{len(rules_data)}</p>
          <p class="text-muted">Security rules matching your configuration</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="summary-card">
          <div class="summary-icon icon-primary">
            <i class="bi bi-key-fill"></i>
          </div>
          <h5 class="card-title"><i class="bi bi-key-fill"></i>Permissions</h5>
          <p class="display-4">{len(permissions_data)}</p>
          <p class="text-muted">Total permissions detected</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="summary-card">
          <div class="summary-icon icon-danger">
            <i class="bi bi-shield-lock"></i>
          </div>
          <h5 class="card-title"><i class="bi bi-shield-lock"></i>Admin Permissions</h5>
          <p class="display-4">{sum(1 for p in permissions_data if 'admin' in p.lower())}</p>
          <p class="text-muted">Admin-level permissions found</p>
        </div>
      </div>
    </div>

    <!-- IAM Rules Section -->
    <div class="card mb-5">
      <div class="card-header">
        <h4 class="mb-0"><i class="bi bi-shield-exclamation me-2"></i>IAM Security Rules Matched</h4>
      </div>
      <div class="card-body">
"""

    # Generate rules list
    for rule in rules_data:
        html_content += f"""
        <div class="rule-card mb-4">
          <div class="card-header">
            <h5>{rule['rule']}</h5>
          </div>
          <div class="card-body">
            <p>{rule['description']}</p>
            <a href="{rule['source']}" target="_blank" class="source-link">
              <i class="bi bi-link-45deg"></i> View Source
            </a>
            <div class="rule-permissions">
"""
        for permission in rule['permissions']:
            html_content += f'<div class="rule-permission-item">{permission}</div>'
        html_content += """
            </div>
          </div>
        </div>
"""

    html_content += """
      </div>
    </div>

    <!-- IAM Permissions Section -->
    <div class="card">
      <div class="card-header">
        <h4 class="mb-0"><i class="bi bi-key-fill me-2"></i>IAM Permissions</h4>
      </div>
      <div class="card-body">
        <div class="permission-list">
"""

    # Generate permissions list - let's group them by service
    services = {}
    for perm in permissions_data:
        service = perm.split('.')[0] if '.' in perm else 'Other'
        if service not in services:
            services[service] = []
        services[service].append(perm)
    
    # Sort services alphabetically
    for service in sorted(services.keys()):
        html_content += f"""
          <div class="mb-4">
            <h5 class="mb-3">{service}</h5>
            <div class="row">
"""
        for perm in sorted(services[service]):
            # Highlight admin permissions
            is_admin = 'admin' in perm.lower()
            admin_class = 'border-danger' if is_admin else ''
            
            html_content += f"""
              <div class="col-md-6 mb-2">
                <div class="permission-item {admin_class}">
                  {perm}
                </div>
              </div>
"""
        html_content += """
            </div>
          </div>
"""

    html_content += """
        </div>
      </div>
    </div>
  </div>

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

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

    # Save the HTML file
    with open("report/report/iam-perm.html", "w") as f:
        f.write(html_content)
    
    print("✅ IAM HTML report generated successfully")
    print("💾 Report saved as report/iam-perm.html")

# Generate the report
generate_iam_report()