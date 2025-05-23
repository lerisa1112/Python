# from flask import Flask, render_template, url_for, send_from_directory
# import threading
# import cv2
# import mediapipe as mp
# import numpy as np
# import os
# import uuid

# app = Flask(__name__, static_folder='static')

# PRODUCT_IMAGES = {
#     "product1": {"image": "products/product1.png", "name": "Aviator Goggles", "price": 450.99},
#     "product2": {"image": "products/product2.png", "name": "Retro Round Goggles", "price": 620.50},
#     "product2": {"image": "products/product3.png", "name": "Retro Round Goggles", "price": 620.50},
#     "product2": {"image": "products/product4.png", "name": "Retro Round Goggles", "price": 620.50},
#     "product2": {"image": "products/product5.png", "name": "Retro Round Goggles", "price": 620.50},
#     "product2": {"image": "products/product6.png", "name": "Retro Round Goggles", "price": 620.50},
#     "product2": {"image": "products/product7.png", "name": "Retro Round Goggles", "price": 620.50}





# }

# CAPTURE_DIR = os.path.join(app.static_folder, "captures")
# os.makedirs(CAPTURE_DIR, exist_ok=True)

# @app.route('/')
# def index():
#     return render_template("products.html", products=PRODUCT_IMAGES)

# @app.route('/start_tryon/<product_id>')
# def start_tryon(product_id):
#     product = PRODUCT_IMAGES.get(product_id)
#     if not product:
#         return "Product not found", 404

#     product_rel_path = product['image']
#     product_abs_path = os.path.join(app.static_folder, product_rel_path)

#     if not os.path.exists(product_abs_path):
#         return "Image not found", 404

#     def tryon_thread():
#         cap = cv2.VideoCapture(0)
#         mp_face = mp.solutions.face_mesh
#         face_mesh = mp_face.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

#         overlay_img = cv2.imread(product_abs_path, cv2.IMREAD_UNCHANGED)
#         if overlay_img is None or overlay_img.shape[2] != 4:
#             print("Overlay image must have an alpha channel (RGBA)")
#             return

#         def overlay_transparent(background, overlay, x, y):
#             h, w = overlay.shape[:2]
#             if x + w > background.shape[1] or y + h > background.shape[0]:
#                 return background
#             alpha = overlay[:, :, 3] / 255.0
#             for c in range(3):
#                 background[y:y+h, x:x+w, c] = alpha * overlay[:, :, c] + (1 - alpha) * background[y:y+h, x:x+w, c]
#             return background

#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 break
#             frame = cv2.flip(frame, 1)
#             rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             results = face_mesh.process(rgb)

#             if results.multi_face_landmarks:
#                 landmarks = results.multi_face_landmarks[0].landmark
#                 left = landmarks[33]
#                 right = landmarks[263]
#                 cx = int((left.x + right.x) / 2 * frame.shape[1])
#                 cy = int((left.y + right.y) / 2 * frame.shape[0])
#                 width = int(abs(right.x - left.x) * frame.shape[1] * 2.0)

#                 resized = cv2.resize(overlay_img, (width, int(width * overlay_img.shape[0] / overlay_img.shape[1])))
#                 frame = overlay_transparent(frame, resized, cx - resized.shape[1] // 2, cy - resized.shape[0] // 2)

#                 # Face width for basic shape suggestion
#                 jaw_left = landmarks[234]
#                 jaw_right = landmarks[454]
#                 jaw_width = abs(jaw_right.x - jaw_left.x) * frame.shape[1]
#                 forehead_chin = abs(landmarks[10].y - landmarks[152].y) * frame.shape[0]

#                 face_shape = "round" if jaw_width > forehead_chin else "oval"
#                 cv2.putText(frame, f"Face Shape: {face_shape}", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

#                 # Recommendation
#                 if product_id == "product1":
#                     recommendation = "✅ Best for oval faces" if face_shape == "oval" else "❌ Not ideal"
#                 else:
#                     recommendation = "✅ Best for round faces" if face_shape == "round" else "❌ Not ideal"
#                 cv2.putText(frame, recommendation, (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

#             cv2.imshow("Goggles Try-On - Press 'c' to capture, 'q' to quit", frame)

#             key = cv2.waitKey(1) & 0xFF
#             if key == ord('c'):
#                 filename = f"capture_{uuid.uuid4().hex[:8]}.png"
#                 path = os.path.join(CAPTURE_DIR, filename)
#                 cv2.imwrite(path, frame)
#                 print(f"📸 Image captured and saved as: {filename}")
#             elif key == ord('q'):
#                 break

#         cap.release()
#         cv2.destroyAllWindows()

#     threading.Thread(target=tryon_thread).start()
#     return "Camera launched! Try-on window opened."

# @app.route('/captures/<filename>')
# def get_capture(filename):
#     return send_from_directory(CAPTURE_DIR, filename)

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, url_for, jsonify
import threading
import cv2
import mediapipe as mp
import numpy as np
import os

app = Flask(__name__, static_folder='static')

# Product metadata with image, name, and comment
PRODUCT_DATA = {
    "product1": {"image": "products/product1.png", "name": "Pink Cloudy Lens", "comment": "Trendy and whimsical – perfect for a fun day out!"},
    "product2": {"image": "products/product2.png", "name": "Pearl Cat Eye", "comment": "Elegant style with pearl detailing for classy looks."},
    "product3": {"image": "products/product3.png", "name": "Mint Edge", "comment": "Chic and cool with a minty freshness."},
    "product4": {"image": "products/product4.png", "name": "Studded Black", "comment": "Bold and edgy – makes a confident statement."},
    "product5": {"image": "products/product5.png", "name": "Butterfly Wings", "comment": "Magical fairy vibes with delicate wings."},
    "product6": {"image": "products/product6.png", "name": "Matrix Black", "comment": "Sleek and sharp – Matrix inspired!"}, 
    "product7": {"image": "products/product7.png", "name": "Purple Fantasy", "comment": "Dazzling lavender tones for a dreamy appearance."}
}

@app.route('/')
def product():
    return render_template("products.html", products=PRODUCT_DATA)

@app.route('/start_tryon/<product_id>')
def start_tryon(product_id):
    product_rel_path = PRODUCT_DATA.get(product_id, {}).get("image")
    if not product_rel_path:
        return "Image not found", 404

    product_abs_path = os.path.join(app.static_folder, product_rel_path)

    def tryon_thread():
        cap = cv2.VideoCapture(0)
        mp_face = mp.solutions.face_mesh
        face_mesh = mp_face.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

        overlay_img = cv2.imread(product_abs_path, cv2.IMREAD_UNCHANGED)
        if overlay_img is None:
            print("Error loading overlay image.")
            return

        def overlay_transparent(background, overlay, x, y):
            h, w = overlay.shape[:2]
            if x + w > background.shape[1] or y + h > background.shape[0]:
                return background
            alpha = overlay[:, :, 3] / 255.0
            for c in range(3):
                background[y:y+h, x:x+w, c] = alpha * overlay[:, :, c] + (1 - alpha) * background[y:y+h, x:x+w, c]
            return background

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                left = landmarks[33]
                right = landmarks[263]
                cx = int((left.x + right.x) / 2 * frame.shape[1])
                cy = int((left.y + right.y) / 2 * frame.shape[0])
                glasses_width = int(abs(right.x - left.x) * frame.shape[1] * 2.0)

                resized = cv2.resize(overlay_img, (glasses_width, int(glasses_width * overlay_img.shape[0] / overlay_img.shape[1])))
                frame = overlay_transparent(frame, resized, cx - resized.shape[1] // 2, cy - resized.shape[0] // 2)

            cv2.imshow("Try-On Live Preview", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    threading.Thread(target=tryon_thread).start()
    return "Camera launched!"

@app.route('/product_info/<product_id>')
def product_info(product_id):
    product = PRODUCT_DATA.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({"name": product["name"], "comment": product["comment"]})

if __name__ == '__main__':
    app.run(debug=True)

