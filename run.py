# run.py
from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    # Note: `debug=True` is for development only.
    app.run(debug=True, port=5000)