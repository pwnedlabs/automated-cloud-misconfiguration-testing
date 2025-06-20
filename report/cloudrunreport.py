import json
from datetime import datetime
import os

def generate_cloud_run_report():
    # Load Cloud Run data
    with open('cloudrun_processed_us-central1.json') as f:
        cloudrun_data = json.load(f)
    
    generated_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create report directory if it doesn't exist
    #os.makedirs("report", exist_ok=True)

    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GCP Security Report | Cloud Run Services</title>
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
    
    .badge-default-sa {{
      background-color: var(--bs-warning);
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
    
    .service-card {{
      transition: all var(--transition-speed);
      height: 100%;
    }}
    
    .service-card .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    
    .service-card .card-header h5 {{
      margin: 0;
      font-weight: 600;
    }}
    
    .service-card .card-body {{
      padding: 1.5rem;
    }}
    
    .service-card .badge {{
      font-size: 0.8rem;
      font-weight: 500;
    }}
    
    .service-card .card-footer {{
      background-color: rgba(0,0,0,0.02);
      border-top: 1px solid rgba(0,0,0,0.05);
      padding: 0.75rem 1.5rem;
    }}
    
    .service-card p {{
      margin-bottom: 0.75rem;
      display: flex;
      align-items: center;
    }}
    
    .service-card p i {{
      margin-right: 8px;
      color: var(--bs-primary);
      width: 20px;
      text-align: center;
    }}
    
    .service-card p strong {{
      font-weight: 600;
      margin-right: 5px;
    }}
    
    .service-card table {{
      margin-top: 1rem;
    }}
    
    .service-card table td {{
      padding: 0.5rem 0.75rem;
      font-size: 0.85rem;
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
    
    .env-vars-table {{
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid rgba(0,0,0,0.1);
    }}
    
    .env-vars-table thead th {{
      background-color: rgba(66, 133, 244, 0.05);
      border-bottom: none;
      padding: 0.75rem;
      font-weight: 600;
    }}
    
    .table-sm td {{
      padding: 0.5rem 0.75rem;
    }}
    
    .bg-high-subtle {{
      background-color: rgba(234, 67, 53, 0.1);
    }}
    
    .bg-medium-subtle {{
      background-color: rgba(251, 188, 5, 0.1);
    }}
    
    .bg-low-subtle {{
      background-color: rgba(52, 168, 83, 0.1);
    }}
    
    .border-high {{
      border-color: var(--bs-danger) !important;
      border-width: 2px !important;
    }}
    
    .border-medium {{
      border-color: var(--bs-warning) !important;
      border-width: 2px !important;
    }}
    
    .border-low {{
      border-color: var(--bs-secondary) !important;
      border-width: 2px !important;
    }}

    .legend-item {{
      display: inline-flex;
      align-items: center;
      margin-right: 1.5rem;
      font-weight: 500;
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
            <a class="nav-link" href="iam-perm.html"><i class="bi bi-key"></i>IAM</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="cloud-storage-buckets.html"><i class="bi bi-archive"></i>Storage</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="compute-engine.html"><i class="bi bi-pc"></i>Compute</a>
          </li>
          <li class="nav-item">
            <a class="nav-link active" href="cloud-run.html"><i class="bi bi-cloud"></i>Cloud Run</a>
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
            <h1><i class="bi bi-cloud"></i>Cloud Run Services</h1>
            <p class="text-muted">Generated on {generated_on}</p>
          </div>
          <div>
            <span class="badge bg-primary">{len(cloudrun_data)} services</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="row mb-5">
      <div class="col-md-4">
        <div class="summary-card">
          <div class="summary-icon icon-danger">
            <i class="bi bi-globe"></i>
          </div>
          <h5 class="card-title"><i class="bi bi-globe"></i>Public Access</h5>
          <p class="display-4">{sum(1 for svc in cloudrun_data if svc["public_access"] == "Public")}</p>
          <p class="text-muted">Services with public ingress</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="summary-card">
          <div class="summary-icon icon-warning">
            <i class="bi bi-person-badge"></i>
          </div>
          <h5 class="card-title"><i class="bi bi-person-badge"></i>Default SAs</h5>
          <p class="display-4">{sum(1 for svc in cloudrun_data if svc["is_default_sa"])}</p>
          <p class="text-muted">Using default service accounts</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="summary-card">
          <div class="summary-icon icon-primary">
            <i class="bi bi-code"></i>
          </div>
          <h5 class="card-title"><i class="bi bi-code"></i>Env Variables</h5>
          <p class="display-4">{sum(len(svc["environment_variables"]) for svc in cloudrun_data)}</p>
          <p class="text-muted">Total environment variables</p>
        </div>
      </div>
    </div>

    <!-- Services List -->
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h4 class="mb-0"><i class="bi bi-list-ul me-2"></i>Service Details</h4>
        <div>
          <span class="legend-item"><span class="risk-indicator risk-high"></span>Public</span>
          <span class="legend-item"><span class="risk-indicator risk-medium"></span>Default SA</span>
          <span class="legend-item"><span class="risk-indicator risk-low"></span>Private</span>
        </div>
      </div>
      <div class="card-body">
        <div class="row row-cols-1 row-cols-md-2 g-4">
"""

    for service in cloudrun_data:
        # Determine risk level
        if service["public_access"] == "Public":
            risk_level = "high"
            access_badge = "badge-public"
        else:
            risk_level = "low"
            access_badge = "badge-private"
        
        if service["is_default_sa"]:
            sa_badge = "badge-default-sa"
            if risk_level != "high":
                risk_level = "medium"
        else:
            sa_badge = "bg-secondary"
        
        # Format environment variables
        env_vars = ""
        if service["environment_variables"]:
            env_vars = "<table class='table table-sm env-vars-table'><thead><tr><th>Name</th><th>Value</th></tr></thead><tbody>"
            for var in service["environment_variables"]:
                env_vars += f'<tr><td class="font-monospace">{var["name"]}</td><td class="font-monospace">{var["value"]}</td></tr>'
            env_vars += "</tbody></table>"
        
        html_content += f"""
          <div class="col">
            <div class="card service-card border-{risk_level}">
              <div class="card-header bg-{risk_level}-subtle">
                <h5>{service["name"]}</h5>
                <span class="badge {access_badge}">{service["public_access"]}</span>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <span class="badge bg-primary">{service["region"]}</span>
                  <span class="badge {sa_badge}">{'Default' if service["is_default_sa"] else ''} Service Account</span>
                </div>
                
                <p><i class="bi bi-calendar"></i><strong>Created:</strong> {service["creation_time"]}</p>
                <p><i class="bi bi-link-45deg"></i><strong>URL:</strong> <a href="{service["url"]}" target="_blank">{service["url"]}</a></p>
                <p><i class="bi bi-person-badge"></i><strong>Service Account:</strong> <span class="font-monospace">{service["service_account"]}</span></p>
                <p><i class="bi bi-funnel"></i><strong>Ingress:</strong> {service["ingress_settings"]}</p>
                
                <div class="mt-4">
                  <h6><i class="bi bi-code-square me-2"></i>Environment Variables</h6>
                  {env_vars if env_vars else '<p class="text-muted">No environment variables</p>'}
                </div>
              </div>
              <div class="card-footer">
                <small class="text-muted">Last modified: {service["last_modified"]}</small>
              </div>
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
    with open("report/report/cloud-run.html", "w") as f:
        f.write(html_content)
    
    print("✅ Cloud Run HTML report generated successfully")

# Generate the report
generate_cloud_run_report()