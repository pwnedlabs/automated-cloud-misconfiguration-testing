import json
from datetime import datetime
import os

def generate_cloud_storage_report():
    # Load bucket data
    with open('bucket-output.json') as f:
        bucket_data = json.load(f)
    
    generated_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create report directory if it doesn't exist
    os.makedirs("report", exist_ok=True)

    # Count public buckets - fixed logic
    public_buckets = sum(1 for bucket in bucket_data if bucket["iam_status"].startswith("Public access detected"))
    
    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GCP Security Report | Cloud Storage</title>
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
            <a class="nav-link" href="iam.html"><i class="bi bi-key"></i>IAM</a>
          </li>
          <li class="nav-item">
            <a class="nav-link active" href="cloud-storage-buckets.html"><i class="bi bi-archive"></i>Storage</a>
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
            <h1><i class="bi bi-archive"></i>Cloud Storage Buckets</h1>
            <p class="text-muted">Generated on {generated_on}</p>
          </div>
          <div>
            <span class="badge bg-primary">{len(bucket_data)} buckets</span>
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
          <h5 class="card-title"><i class="bi bi-globe"></i>Public Buckets</h5>
          <p class="display-4">{public_buckets}</p>
          <p class="text-muted">Buckets with public access</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="summary-card">
          <div class="summary-icon icon-success">
            <i class="bi bi-shield-lock"></i>
          </div>
          <h5 class="card-title"><i class="bi bi-shield-lock"></i>Private Buckets</h5>
          <p class="display-4">{len(bucket_data) - public_buckets}</p>
          <p class="text-muted">Secured buckets</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="summary-card">
          <div class="summary-icon icon-primary">
            <i class="bi bi-calendar3"></i>
          </div>
          <h5 class="card-title"><i class="bi bi-calendar3"></i>Oldest Bucket</h5>
          <p class="display-4">{min(bucket['created_time'] for bucket in bucket_data) if bucket_data else 'N/A'}</p>
          <p class="text-muted">First created bucket</p>
        </div>
      </div>
    </div>

    <!-- Buckets List -->
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h4 class="mb-0"><i class="bi bi-list-ul me-2"></i>Bucket Details</h4>
        <div>
          <span class="legend-item"><span class="risk-indicator risk-high"></span>Public</span>
          <span class="legend-item"><span class="risk-indicator risk-low"></span>Private</span>
        </div>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Bucket Name</th>
                <th>Location</th>
                <th>Storage Class</th>
                <th>Created</th>
                <th>Access Status</th>
              </tr>
            </thead>
            <tbody>
"""

    for bucket in bucket_data:
        is_public = bucket["iam_status"].startswith("Public access detected")
        iam_status = bucket["iam_status"]
        
        if is_public:
            status_class = "public-access"
            badge_class = "badge-public"
            row_class = "bucket-row-public"
            icon = "bi-folder-symlink"
        else:
            status_class = "private-access"
            badge_class = "badge-private"
            row_class = ""
            icon = "bi-folder"
        
        html_content += f"""
              <tr class="{row_class}">
                <td>
                  <i class="bi {icon} bucket-icon"></i>
                  <strong>{bucket['bucket_name']}</strong>
                </td>
                <td>{bucket['location']}</td>
                <td>{bucket['storage_class']}</td>
                <td>{bucket['created_time']}</td>
                <td>
                  <span class="badge {badge_class}">
                    {'Public' if is_public else 'Private'}
                  </span>
                  <small class="{status_class} d-block mt-1">{iam_status}</small>
                </td>
              </tr>
"""

    html_content += """
            </tbody>
          </table>
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
    with open("report/report/cloud-storage-buckets.html", "w") as f:
        f.write(html_content)
    
    print("✅ Cloud Storage HTML report generated successfully")

# Generate the report
generate_cloud_storage_report()