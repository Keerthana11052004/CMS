import os
import platform
from app import create_app
from waitress import serve
import socket

# Windows compatibility for site-packages
if platform.system() == "Windows":
    site_packages_path = os.path.join(
        os.environ['LOCALAPPDATA'],
        'Packages',
        'PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0',
        'LocalCache', 'local-packages', 'Python313', 'site-packages'
    )
    if site_packages_path not in os.sys.path:
        os.sys.path.append(site_packages_path)

url_prefix = "/cms"
app = create_app(url_prefix=url_prefix)

if __name__ == '__main__':
    port = 5000
    host = '0.0.0.0'
    

    print(f"🚀 Starting CMS server on http://localhost:{port}{url_prefix}")
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except:
        ip = "127.0.0.1"
    print(f"🌍 Accessible on network: http://{ip}:{port}{url_prefix}")

    # Start server with Waitress
    serve(app, host=host, port=port)
