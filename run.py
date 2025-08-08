import sys
import os

# Add the site-packages directory to the Python path
site_packages_path = os.path.join(os.environ['LOCALAPPDATA'], 'Packages', 'PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0', 'LocalCache', 'local-packages', 'Python313', 'site-packages')
if site_packages_path not in sys.path:
    sys.path.append(site_packages_path)

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Development only! Use a WSGI server for production.
    app.run(host='0.0.0.0', port=5000, debug=True)