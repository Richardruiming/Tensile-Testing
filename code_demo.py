

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import argparse





argparse.ArgumentParser(description="Plot tensile test data from a CSV file.")
parser = argparse.ArgumentParser(description="Plot tensile test data from a CSV file.")
parser.add_argument('--cross_area','-ca', type=float, default=1.0, help='Cross-sectional area of the sample in mm^2 (default: 1.0 mm^2)')
parser.add_argument('--input_file', '-i', type=str, default='input_force_displacement.csv', help='Input CSV file containing force and displacement data (default: input_force_displacement.csv)')
parser.add_argument('--output_file', '-o', type=str, default='output_stress_strain.txt', help='Output file to save the analysis results (default: output_stress_strain.txt)')
args = parser.parse_args()



df = pd.read_csv(args.input_file)
#times 2 to the first column
df['strain'] = df['Displacement'] * 2
df['Stress'] = df['Force'] / args.cross_area




#find the slope of the first 50 points
slope = np.polyfit(df['strain'][:50], df['Stress'][:50], 1)[0]
print(f"Initial slope: {slope:.2f} MPa/mm")

#find the equation of the line, offset to the right by 0.2
line_eq = np.poly1d(np.polyfit(df['strain'][:50] + 0.2, df['Stress'][:50], 1))
print(f"Equation of the line: y = {line_eq.coefficients[0]:.2f}x + {line_eq.coefficients[1]:.2f}")
#find the intersection point of this line and the stress-strain curve
intersection_x = (df['Stress'] - line_eq.coefficients[1]) / line_eq.coefficients[0]
intersection_y = line_eq(intersection_x)

#find the closest point in the stress-strain curve to the intersection point
closest_index = (np.abs(df['strain'] - intersection_x)).idxmin()
intersection_x = df['strain'][closest_index]
intersection_y = df['Stress'][closest_index]



print(f"Intersection point: ({intersection_x:.2f}, {intersection_y:.2f})")


#find the maximum stress and the corresponding strain
max_stress = df['Stress'].max()

with open(args.output_file, 'w') as f:
    f.write(f"Initial slope: {slope:.2f} MPa/mm\n")
    f.write(f"Equation of the line: y = {line_eq.coefficients[0]:.2f}x + {line_eq.coefficients[1]:.2f}\n")
    f.write(f"Maximum stress: {max_stress:.2f} MPa at strain {intersection_x:.2f} \n")
    f.write(f"Intersection point: ({intersection_x:.2f}, {intersection_y:.2f})\n")
print(f"Results saved to {args.output_file}")

import tkinter.messagebox as msg

result_str = (
    f"Initial slope: {slope:.2f} MPa/mm\n"
    f"Equation of the line: y = {line_eq.coefficients[0]:.2f}x + {line_eq.coefficients[1]:.2f}\n"
    f"Maximum stress: {max_stress:.2f} MPa at strain {intersection_x:.2f} \n"
    f"Intersection point: ({intersection_x:.2f}, {intersection_y:.2f})"
)

msg.showinfo("Tensile Test Results", result_str)



#plot the line_equation on the same graph with the stress and strain data
#the y value of the graph goes up to the max stress
plt.figure(figsize=(10, 6))
plt.xlim(0, df['strain'].max() + 0.5)
plt.ylim(0, max_stress * 1.1)
plt.plot(df['strain'], df['Stress'], label='Stress-Strain Data', color='blue')
plt.plot(df['strain'], line_eq(df['strain']), label='Initial Linear Fit', color='orange')  
plt.axhline(y=max_stress, color='red', linestyle='--', label='Max Stress')
plt.axvline(x=intersection_x, color='green', linestyle='--', label='Intersection Point')
plt.axhline(y=intersection_y, color='green', linestyle='--')
plt.scatter(intersection_x, intersection_y, color='green', zorder=5, label='Intersection Point')
plt.xlabel('Strain (mm/mm)')
plt.ylabel('Stress (MPa)')
plt.title('Stress-Strain Curve')
plt.legend()
plt.grid() 
plt.show()


