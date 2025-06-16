from flask import Flask, request, render_template, send_file
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
@app.route('/')

def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        percentage = float(request.form['linear_points_percentage'])/100
        cross_sectional_area = float(request.form['cross_sectional_area'])
        linear_line_offset = float(request.form['linear_line_offset'])
        file = request.files['csv_file']

        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()
        df['strain'] = df['Displacement'] * 2
        df['Stress'] = df['Force'] / cross_sectional_area

        n_points = max(2, int(len(df) * percentage))
        slope = np.polyfit(df['strain'][:n_points], df['Stress'][:n_points], 1)[0]
        line_eq = np.poly1d(np.polyfit(df['strain'][:n_points] + linear_line_offset, df['Stress'][:n_points], 1))

        intersection_x = (df['Stress'] - line_eq.coefficients[1]) / line_eq.coefficients[0]
        closest_index = (np.abs(df['strain'] - intersection_x)).idxmin()
        intersection_x = df['strain'][closest_index]
        intersection_y = df['Stress'][closest_index]
        max_stress = df['Stress'].max()

        plt.figure(figsize=(10, 6))
        plt.plot(df['strain'], df['Stress'], label='Stress-Strain Data', color='blue')
        plt.plot(df['strain'], line_eq(df['strain']), label='Initial Linear Fit', color='orange')
        plt.axhline(y=max_stress, color='red', linestyle='--', label='Max Stress')
        plt.axvline(x=intersection_x, color='green', linestyle='--', label='Intersection Point')
        plt.axhline(y=intersection_y, color='green', linestyle='--')
        #set the maximum of the y axis to 1.2 times the maximum stress
        plt.ylim(0, 1.1 * max_stress)
        plt.scatter(intersection_x, intersection_y, color='green', zorder=5)
        plt.xlabel('Strain (mm/mm)')
        plt.ylabel('Stress (MPa)')
        plt.title('Stress-Strain Curve')
        plt.legend()
        plt.grid()

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.read()).decode()

        return render_template('result.html',
                               slope=round(slope, 2),
                               eq=f"y = {line_eq.coefficients[0]:.2f}x + {line_eq.coefficients[1]:.2f}",
                               max_stress=round(max_stress, 2),
                               intersection=f"({intersection_x:.2f}, {intersection_y:.2f})",
                               plot_url=plot_url)
    except Exception as e:
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    from os import environ
    port = int(environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)