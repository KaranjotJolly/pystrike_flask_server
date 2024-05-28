# app.py
from flask import Flask, request, jsonify, send_file
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

app = Flask(__name__)

@app.route('/run_code', methods=['POST'])
def run_code():
    code = request.json.get('code')
    # Execute the code and capture the output
    try:
        # Setup a secure environment for the execution
        exec_globals = {}
        exec_locals = {}
        exec(code, exec_globals, exec_locals)
        # Check for any generated figures
        if plt.get_fignums():
            fig = plt.gcf()
            buf = io.BytesIO()
            FigureCanvas(fig).print_png(buf)
            buf.seek(0)
            return send_file(buf, mimetype='image/png')
        else:
            return jsonify({'output': exec_locals.get('output', 'No output')})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
