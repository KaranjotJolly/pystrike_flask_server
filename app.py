# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import io
import sys
import contextlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import base64
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

logging.basicConfig(level=logging.DEBUG)

class StdoutCapture:
    def __init__(self):
        self.output = io.StringIO()
        self.figures = []

    def write(self, data):
        self.output.write(data)

    def flush(self):
        pass

    def show_figure(self):
        if plt.get_fignums():
            buf = io.BytesIO()
            FigureCanvas(plt.gcf()).print_png(buf)
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode('utf-8')
            self.figures.append(encoded)
            plt.close(plt.gcf())

@contextlib.contextmanager
def capture_stdout():
    old_stdout = sys.stdout
    capture = StdoutCapture()
    sys.stdout = capture
    try:
        yield capture
    finally:
        sys.stdout = old_stdout

@app.route('/run_code', methods=['POST'])
def run_code():
    code = request.json.get('code')
    app.logger.debug(f"Received code: {code}")
    try:
        exec_globals = {'plt': plt}
        exec_locals = {}

        with capture_stdout() as capture:
            exec(code, exec_globals, exec_locals)
            stdout_output = capture.output.getvalue()
            figures = capture.figures

        response = {'output': stdout_output, 'figures': figures}

        app.logger.debug(f"Output: {stdout_output}")
        return jsonify(response)
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
