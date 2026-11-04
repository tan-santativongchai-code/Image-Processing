import cv2
import os

# Global variables for mouse tracking
drawing = False
ix, iy = -1, -1
fx, fy = -1, -1
current_image = None
clone = None
output_dir = r"D:\MTEC\Image-Processing\Cell Classification and Counting\cell detection dataset\cropped_cell"
current_label = "alive"  # Default label
crop_counters = {"alive": 0, "dead": 0}

# Ensure output folders exist
for label in ['alive', 'dead']:
    os.makedirs(os.path.join(output_dir, label), exist_ok=True)

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, fx, fy, drawing, current_image, clone
    
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            current_image = clone.copy()
            # Draw temporary selection box with current label color
            color = (0, 255, 0) if current_label == "alive" else (0, 0, 255)
            cv2.rectangle(current_image, (ix, iy), (x, y), color, 2)
            
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        fx, fy = x, y
        color = (0, 255, 0) if current_label == "alive" else (0, 0, 255)
        cv2.rectangle(current_image, (ix, iy), (fx, fy), color, 2)
        cv2.imshow("Cell Cropper", current_image)

def interactive_crop(image_path):
    global current_image, clone, current_label, ix, iy, fx, fy
    
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image from {image_path}")
        return
        
    clone = img.copy()
    current_image = img.copy()
    
    cv2.namedWindow("Cell Cropper", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Cell Cropper", 1200, 900)
    cv2.setMouseCallback("Cell Cropper", draw_rectangle)
    
    print("========================================")
    print("         CELL CROPPER CONTROLS          ")
    print("========================================")
    print(" [Drg] Click & drag mouse over a cell")
    print(" [a] Set label to ALIVE (Green box)")
    print(" [d] Set label to DEAD (Red box)")
    print(" [s] Save cropped cell to folder")
    print(" [r] Reset/Clear current box")
    print(" [ESC] Exit and quit")
    print("----------------------------------------")
    print(f"Current active label: -> {current_label.upper()} <-")
    
    while True:
        # Show status overlay text on top of the image window
        display_img = current_image.copy()
        status_text = f"Mode: {current_label.upper()} | Alive: {crop_counters['alive']} | Dead: {crop_counters['dead']}"
        color = (0, 255, 0) if current_label == "alive" else (0, 0, 255)
        cv2.putText(display_img, status_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
        
        cv2.imshow("Cell Cropper", display_img)
        key = cv2.waitKey(1) & 0xFF
        
        # Press 'a' to set label to Alive
        if key == ord('a'):
            current_label = "alive"
            print("\n-> Label set to: ALIVE (Green)")
            
        # Press 'd' to set label to Dead
        elif key == ord('d'):
            current_label = "dead"
            print("\n-> Label set to: DEAD (Red)")
            
        # Press 's' to save the cropped cell
        elif key == ord('s'):
            if ix != -1 and fx != -1:
                x1, x2 = min(ix, fx), max(ix, fx)
                y1, y2 = min(iy, fy), max(iy, fy)
                
                if x2 - x1 > 3 and y2 - y1 > 3:
                    # FIX: Crop directly from the clean 'clone' instead of 'current_image' to avoid capturing the frame lines
                    cell_crop = clone[y1:y2, x1:x2]
                    count = crop_counters[current_label]
                    
                    save_path = os.path.join(output_dir, current_label, f"cell_{count:04d}.png")
                    cv2.imwrite(save_path, cell_crop)
                    print(f"Saved [{current_label}] cell #{count:04d} -> {save_path}")
                    
                    crop_counters[current_label] += 1
                    clone = current_image.copy()
                    ix, iy, fx, fy = -1, -1, -1, -1
                else:
                    print("Selection too small! Try dragging a larger box.")
            else:
                print("No box drawn yet! Click and drag on the image first.")
                
        # Reset selection box
        elif key == ord('r'):
            current_image = clone.copy()
            ix, iy, fx, fy = -1, -1, -1, -1
            print("Selection reset.")
            
        # Press ESC to exit
        elif key == 27:
            print("\nExiting cell cropper. Total saved:")
            print(f" - Alive cells: {crop_counters['alive']}")
            print(f" - Dead cells: {crop_counters['dead']}")
            break
            
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Change this filename to your image file (e.g., "w1-0h.F.100x (1).tif")
    image_filename = r"D:\MTEC\Image-Processing\Cell Classification and Counting\cell detection dataset\Processed\100x\w1-0h.F.100x (1).jpg"
    interactive_crop(image_filename)