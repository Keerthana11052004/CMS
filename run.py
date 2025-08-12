import os
import platform
from app import create_app
from waitress import serve

# Only do this on Windows
if platform.system() == "Windows":
    site_packages_path = os.path.join(
        os.environ['LOCALAPPDATA'],
        'Packages',
        'PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0',
        'LocalCache', 'local-packages', 'Python313', 'site-packages'
    )
    if site_packages_path not in os.sys.path:
        os.sys.path.append(site_packages_path)

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    host = '0.0.0.0'
    print(f"🚀 Starting server on http://localhost:{port}")
    print(f"🌍 Accessible on network: http://{os.popen('hostname -I').read().strip()}:{port}")
    serve(app, host=host, port=port)
