import os
from app import create_app
from waitress import serve

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    serve(app, host='0.0.0.0', port=port) 