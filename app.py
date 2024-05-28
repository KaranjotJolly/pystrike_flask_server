# app.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import os
import io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
import skimage
import xgboost
import scipy
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

logging.basicConfig(level=logging.DEBUG)

@app.route('/run_code', methods=['POST'])
def run_code():
    code = request.json.get('code')
    app.logger.debug(f"Received code: {code}")
    # Execute the code and capture the output
    try:
        exec_globals = {}
        exec_locals = {}
        exec(code, exec_globals, exec_locals)
        # Check for any generated figures
        if plt.get_fignums():
            fig = plt.gcf()
            buf = io.BytesIO()
            FigureCanvas(fig).print_png(buf)
            buf.seek(0)
            plt.close(fig)  # Close the figure to avoid memory issues
            return send_file(buf, mimetype='image/png')
        else:
            output = exec_locals.get('output', 'No output')
            app.logger.debug(f"Output: {output}")
            return jsonify({'output': output})
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
