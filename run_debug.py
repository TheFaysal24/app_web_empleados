#!/usr/bin/env python
import os
os.environ['FLASK_DEBUG'] = '1'
os.environ['FLASK_ENV'] = 'development'

# Import Flask app
from app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
