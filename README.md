# New-Gen-Attendance-System
A smart, secure attendance automation system using Computer Vision and Firebase. Features real-time face recognition with anti-spoofing (blink detection), cloud database synchronization, and ESP32 hardware integration for remote logging.

# New-Gen Attendance System 📸✅
A robust, AI-powered attendance management solution that eliminates manual logging and prevents proxy attendance. This system leverages **Computer Vision** for facial recognition and **Firebase** for real-time cloud storage, ensuring a secure and seamless experience.

## 🚀 Features
- **Real-Time Face Recognition**: Instantly identifies registered students via webcam using the `face_recognition` library (by Adam Geitgey).
- **Anti-Spoofing Security**: Implements **liveness detection** (Eye Aspect Ratio/Blink Detection) using `dlib` landmarks to prevent attendance via static photos.
- **Cloud Integration**: Syncs student data, attendance logs, and profile images in real-time using **Google Firebase** (Realtime Database & Storage).
- **Hardware Integration**: Communicates with **ESP32** devices via WiFi sockets, enabling external triggers (like door locks, SMS modules, or visual indicators) upon successful attendance.
- **Smart Cooldown**: Prevents multiple entries for the same user within a short timeframe (30-second buffer).
- **Dynamic UI**: Displays student details, attendance status, and profile photos dynamically on a custom background interface.

## 🛠️ Tech Stack
- **Language**: Python 3.x
- **Computer Vision**: OpenCV (`cv2`), `cvzone`, `dlib`
- **Face Recognition**: `face_recognition` library
- **Database**: Firebase Admin SDK (Realtime Database & Storage)
- **GUI**: Custom OpenCV overlays
- **Hardware Comms**: Python `socket` module (TCP/IP)

## 📂 Project Structure
New-Gen-Attendance-System/
├── AddDataToDataBase.py # Script to upload student info to Firebase
├── EncodingImages.py # Encodes faces from /Images and uploads to Cloud Storage
├── main.py # Core script: Recognition, Liveness Check, & UI
├── Resources/ # UI Assets (backgrounds, modes)
├── Images/ # Student profile photos (ID.png)
├── serviceAccountKey.json # Firebase credentials (not included)
└── shape_predictor_68... # Dlib landmark model

## ⚙️ Setup & Installation
### 1. Prerequisites
Install the required Python libraries. Note: `dlib` and `face_recognition` may require CMake and Visual Studio build tools on Windows.
pip install opencv-python numpy face-recognition cvzone firebase-admin dlib pygame scipy

### 2. Firebase Setup
1. Create a project on the [Firebase Console](https://console.firebase.google.com/).
2. Set up **Realtime Database** and **Storage**.
3. Generate a private key (Service Account) from Project Settings > Service Accounts.
4. Download the JSON file, rename it to `serviceAccountKey.json`, and place it in the project root.
5. Update the `databaseURL` and `storageBucket` in the Python scripts.

### 3. Hardware Requirements (Optional)
- **Webcam**: For facial scanning.
- **ESP32 Module**: If using the hardware trigger feature. Update the `esp32_ip` in `main.py` to match your device's local IP.

### 4. Dlib Model
Download the `shape_predictor_68_face_landmarks.dat` file (required for blink detection) and place it in the root directory.
[Download Link](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2) (Extract before use).

## 🏃 Usage

### Step 1: Register Students
Add student images to the `Images/` folder named by their ID (e.g., `12345.png`). Then run the database script to upload their metadata:
python AddDataToDataBase-AttendanceSystem.py

### Step 2: Encode Faces
Generate facial encodings and upload the images to Firebase Storage:
python EncodingImages-AttendanceSystem.py

### Step 3: Run the System
Launch the main application:
python main-AttendanceSystem.py

- The system will open the webcam interface.
- **Blink to verify liveness**: The system waits for an eye blink to confirm a real person is present.
- Upon verification, attendance is marked, and data is sent to the ESP32.

## 📊 Database Schema

The system organizes data in Firebase as follows:
- **Students/**: Contains individual student objects (Name, Major, Year, Last Attendance, etc.).
- **Absentees_Student**: A managed list of IDs currently marked absent.
- **Present_Student**: A managed list of IDs marked present for the session.

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📜 License

This project is open-source.
