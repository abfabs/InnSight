#!/usr/bin/env python3

from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
