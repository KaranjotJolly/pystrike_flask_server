# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import io
import sys
import contextlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
import skimage
import xgboost
import scipy
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import base64
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

logging.basicConfig(level=logging.DEBUG)

class OutputCapture(io.StringIO):
    def __init__(self):
        super().__init__()
        self.output_parts = []

    def write(self, data):
        self.output_parts.append(('text', data))
        super().write(data)

    def flush(self):
        pass

    def show_figure(self):
        buf = io.BytesIO()
        FigureCanvas(plt.gcf()).print_png(buf)
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        self.output_parts.append(('image', encoded))
        plt.close(plt.gcf())

@contextlib.contextmanager
def capture_output():
    old_stdout = sys.stdout
    old_show = plt.show
    capture = OutputCapture()
    sys.stdout = capture

    def custom_show(*args, **kwargs):
        old_show(*args, **kwargs)
        capture.show_figure()

    plt.show = custom_show

    try:
        yield capture
    finally:
        sys.stdout = old_stdout
        plt.show = old_show

@app.route('/run_code', methods=['POST'])
def run_code():
    code = request.json.get('code')
    app.logger.debug(f"Received code: {code}")
    try:
        exec_globals = {
            'plt': plt,
            'np': np,
            'pd': pd,
            'sklearn': sklearn,
            'skimage': skimage,
            'xgboost': xgboost,
            'scipy': scipy,
            '__builtins__': __builtins__,
        }
        exec_locals = {}

        with capture_output() as capture:
            exec(code, exec_globals, exec_locals)
            output_parts = capture.output_parts

        response = {'output_parts': output_parts}

        app.logger.debug(f"Output: {output_parts}")
        return jsonify(response)
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
