# app.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import io
import sys
import contextlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

logging.basicConfig(level=logging.DEBUG)

@contextlib.contextmanager
def capture_stdout():
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield sys.stdout
    finally:
        sys.stdout = old_stdout

@app.route('/run_code', methods=['POST'])
def run_code():
    code = request.json.get('code')
    app.logger.debug(f"Received code: {code}")
    try:
        exec_globals = {}
        exec_locals = {}
        with capture_stdout() as output:
            exec(code, exec_globals, exec_locals)
        stdout_output = output.getvalue()

        response = {}

        # Check for any generated figures
        if plt.get_fignums():
            fig = plt.gcf()
            buf = io.BytesIO()
            FigureCanvas(fig).print_png(buf)
            buf.seek(0)
            plt.close(fig)  # Close the figure to avoid memory issues
            response['image'] = buf.getvalue().decode('latin1')

        if stdout_output.strip():
            response['output'] = stdout_output
        elif 'image' not in response:
            response['output'] = 'No output'

        app.logger.debug(f"Output: {stdout_output}")
        return jsonify(response)
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
