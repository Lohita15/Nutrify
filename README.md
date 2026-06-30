# 🥗 NutriFy – AI-Powered Indian Food Recognition & Calorie Estimation

NutriFy is a full-stack web application that uses Artificial Intelligence to recognize Indian food items from images and estimate their calorie and nutritional information. The application combines YOLOv5 object detection with a Flask backend and an interactive frontend to help users make healthier food choices.

---

## 🚀 Features

- 📷 Upload an image of Indian food
- 🤖 AI-powered food recognition using YOLOv5
- 🔍 Detects food items from images
- 🔥 Estimates calorie information
- 📊 Displays nutritional details
- 🌐 Responsive and user-friendly interface
- ⚡ Flask-based REST backend
- 🎯 Fast and accurate inference

---

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask
- Pandas

### Artificial Intelligence
- YOLOv5
- PyTorch
- OpenCV
- Pillow

---

## 📁 Project Structure

```
Nutrify-main/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── model/
│   │   ├── classifier/
│   │   │   ├── best.pt
│   │   │   └── containers.pt
│   │   └── calories/
│   │       └── calories.xlsx
│   └── nutrify_utils/
│
├── frontend/
│   ├── css/
│   ├── js/
│   ├── index.html
│   ├── upload.html
│   └── results.html
│
├── test_model.py
├── run.sh
├── run.bat
├── yolov5s.pt
├── README.md
└── LICENSE
```

---

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/your-username/Nutrify.git
cd Nutrify-main
```

### Install dependencies

```bash
pip install -r backend/requirements.txt
```

### Run the application

**Windows**

```bash
run.bat
```

or

```bash
python backend/app.py
```

**Linux / macOS**

```bash
chmod +x run.sh
./run.sh
```

---

## 📖 How It Works

1. Upload an image containing Indian food.
2. YOLOv5 detects the food item(s).
3. The classifier identifies the food category.
4. The nutrition database retrieves calorie information.
5. The application displays the detected food along with its estimated calories and nutritional values.

---

## 📸 Screenshots

Add screenshots here:

- 🏠 Home Page
- 📤 Image Upload
- 🤖 Food Detection
- 📊 Nutrition & Calorie Results

---

## 🎯 Future Enhancements

- Multi-food detection
- Portion size estimation
- Daily calorie tracking
- Meal recommendations
- User authentication
- Mobile application

---

## 👩‍💻 Contributors

- Lohita Reddy
- Team Members

---

## 📄 License

This project is licensed under the MIT License.

---

⭐ If you found this project useful, consider giving it a star!
