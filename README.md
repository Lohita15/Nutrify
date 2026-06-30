# 🥗 NutriFy – AI-Powered Indian Food Recognition & Calorie Estimation

NutriFy is a full-stack web application that uses Artificial Intelligence to recognize Indian food items from images and estimate their calorie and nutritional information. The application combines YOLOv8n instance segmentation model with a Flask backend and an interactive frontend to help users make healthier food choices.

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
- YOLOv8n-instance segmentation
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
├── README.md
└── LICENSE
```

---

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/Lohita15/Nutrify.git
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

- 🏠 Home Page<img width="1805" height="870" alt="Screenshot 2026-06-30 100331" src="https://github.com/user-attachments/assets/3c1948db-81c6-420f-b050-d3043dad1fe4" />

- 📤 Image Upload<img width="1802" height="892" alt="nf2" src="https://github.com/user-attachments/assets/eaeaa41a-c32b-4d2d-a71e-de61d82e8c8d" />

- 🤖 Food Detection<img width="1775" height="891" alt="Screenshot 2026-06-30 100526" src="https://github.com/user-attachments/assets/4a888ebe-35e1-48d2-9508-2e5fc3f7ebad" />

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
  NGIT CSE 
---

## 📄 License

This project is licensed under the MIT License.

---

⭐ If you found this project useful, consider giving it a star!
