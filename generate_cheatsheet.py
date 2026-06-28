import os
import numpy as np
import cv2

# Mediapipe hand connections
CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4), # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8), # Index
    (5, 9), (9, 10), (10, 11), (11, 12), # Middle
    (9, 13), (13, 14), (14, 15), (15, 16), # Ring
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20) # Pinky
]

def draw_landmarks_on_blank_image(landmarks_array, img_size=400):
    img = np.ones((img_size, img_size, 3), dtype=np.uint8) * 255 # White background
    
    # landmarks_array is 63 floats: x, y, z for 21 points.
    points = []
    for i in range(21):
        x = landmarks_array[i*3]
        y = landmarks_array[i*3 + 1]
        
        # Scale back to image coordinates
        px = int(x * img_size)
        py = int(y * img_size)
        points.append((px, py))
        
    # Draw connections
    for start, end in CONNECTIONS:
        if start < len(points) and end < len(points):
            cv2.line(img, points[start], points[end], (0, 255, 0), 3)
            
    # Draw points
    for i, p in enumerate(points):
        # highlight fingertips
        color = (0, 0, 255) if i in [4, 8, 12, 16, 20] else (255, 0, 0)
        cv2.circle(img, p, 5, color, -1)
        
    return img

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(root_dir, "data", "raw_landmarks")
    output_dir = os.path.join(root_dir, "models")
    
    labels = sorted([d for d in os.listdir(data_dir) if not d.startswith(".")])
    
    # We will arrange them in a grid
    cols = 4
    rows = (len(labels) + cols - 1) // cols
    img_size = 300
    
    grid_img = np.ones((rows * img_size, cols * img_size, 3), dtype=np.uint8) * 255
    
    for i, label in enumerate(labels):
        folder = os.path.join(data_dir, label)
        files = [f for f in os.listdir(folder) if f.endswith(".npy")]
        if not files:
            continue
            
        # Take the first file as a representative sample
        filepath = os.path.join(folder, files[0])
        data = np.load(filepath)
        
        # Generate the visualization
        hand_img = draw_landmarks_on_blank_image(data, img_size=img_size)
        
        # Put the label text
        cv2.putText(hand_img, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        row = i // cols
        col = i % cols
        
        y_start = row * img_size
        y_end = y_start + img_size
        x_start = col * img_size
        x_end = x_start + img_size
        
        grid_img[y_start:y_end, x_start:x_end] = hand_img
        
    out_path = os.path.join(output_dir, "gesture_cheatsheet.png")
    cv2.imwrite(out_path, grid_img)
    print(f"Generated cheatsheet at {out_path}")

if __name__ == "__main__":
    main()
