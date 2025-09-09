import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection
import numpy as np
import csv

def add_paddle(ax, xmin, ymin, zmin, xmax, ymax, zmax, fill=False, color='gray'):
    # Define corners
    p = np.array([
        [xmin, ymin, zmin],
        [xmax, ymin, zmin],
        [xmax, ymax, zmin],
        [xmin, ymax, zmin],
        [xmin, ymin, zmax],
        [xmax, ymin, zmax],
        [xmax, ymax, zmax],
        [xmin, ymax, zmax]
    ])
    # Edges for wireframe
    edges = [
        [p[0], p[1]], [p[1], p[2]], [p[2], p[3]], [p[3], p[0]],
        [p[4], p[5]], [p[5], p[6]], [p[6], p[7]], [p[7], p[4]],
        [p[0], p[4]], [p[1], p[5]], [p[2], p[6]], [p[3], p[7]]
    ]
    ax.add_collection3d(Line3DCollection(edges, colors='gray', linewidths=0.5))
    if fill:
        # Faces for solid box
        faces = [
            [p[0], p[1], p[2], p[3]],
            [p[4], p[5], p[6], p[7]],
            [p[0], p[1], p[5], p[4]],
            [p[2], p[3], p[7], p[6]],
            [p[1], p[2], p[6], p[5]],
            [p[0], p[3], p[7], p[4]]
        ]
        ax.add_collection3d(Poly3DCollection(faces, facecolors=color, linewidths=0, alpha=0.8))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Geometry parameters
paddle_thickness = 2
plane_spacing = 20
index_to_paddle = {}
index = 0
for layer in range(11):
    z_start = layer * (paddle_thickness + plane_spacing)
    if layer % 2 == 0:
        for i in range(13):
            coords = (i * 23, 0, z_start, (i + 1) * 23, 150, z_start + paddle_thickness)
            index_to_paddle[index] = coords
            index += 1
            coords = (i * 23, 150, z_start, (i + 1) * 23, 300, z_start + paddle_thickness)
            index_to_paddle[index] = coords
            index += 1
    else:
        for i in range(15):
            coords = (0, i * 20, z_start, 150, (i + 1) * 20, z_start + paddle_thickness)
            index_to_paddle[index] = coords
            index += 1
            coords = (150, i * 20, z_start, 300, (i + 1) * 20, z_start + paddle_thickness)
            index_to_paddle[index] = coords
            index += 1
print(index)

# Read the mapping from map2.txt
mapping = {}
with open('map2.txt', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if row:
            a, b = int(row[0]), int(row[1])
            mapping[b] = a

# Read MRDhitT and MRDhitDetID from event.txt
paddle_times = {}
with open('event.txt', 'r') as f:
    lines = f.readlines()
    for line in lines[1:]:  # Skip header
        parts = line.split()
        if len(parts) == 2:
            t, detid = float(parts[0]), int(parts[1])
            print(f"detid: {detid}, t: {t}")
            if detid in mapping:
                idx = mapping[detid]
                # If multiple hits per paddle, you can choose to average, min, max, etc.
                # Here, we take the earliest time (min)
                if idx not in paddle_times or t < paddle_times[idx]:
                    paddle_times[idx] = t

print(f"Activated paddles: {len(paddle_times)}")
print(f"Active paddle indices: {list(paddle_times.keys())}")
print(f"Time values: {list(paddle_times.values())}")

# Normalize times for colormap
if paddle_times:
    times = np.array(list(paddle_times.values()))
    tmin, tmax = times.min(), times.max()
else:
    tmin, tmax = 0, 1

norm = plt.Normalize(vmin=tmin, vmax=tmax)
cmap = plt.cm.viridis

# Draw paddles with color by time
for idx, (xmin, ymin, zmin, xmax, ymax, zmax) in index_to_paddle.items():
    if idx in paddle_times:
        color = cmap(norm(paddle_times[idx]))
        add_paddle(ax, xmin, ymin, zmin, xmax, ymax, zmax, fill=True, color=color)
    else:
        add_paddle(ax, xmin, ymin, zmin, xmax, ymax, zmax, fill=False, color='gray')

# Add colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, pad=0.1)
cbar.set_label('MRDhitT (ns)')

# View settings
ax.set_xlim([0, 310])
ax.set_ylim([0, 330])
ax.set_zlim([0, 11 * (paddle_thickness + plane_spacing)])
ax.set_box_aspect([310, 330, 11 * (paddle_thickness + plane_spacing)])
ax.set_xlabel('X (cm)')
ax.set_ylabel('Y (cm)')
ax.set_zlabel('Z (cm)')
#ax.set_title('Activated Paddles Highlighted in Yellow')
plt.tight_layout()
plt.show()
