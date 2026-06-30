import os
import cv2
import numpy as np
from PIL import Image
import torch
from datetime import datetime
import json

# Calorie database for Indian foods (can be expanded)
CALORIE_DATABASE = {
    "biryani": {"calories_per_100g": 180, "default_portion": 250},
    "dosa": {"calories_per_100g": 168, "default_portion": 150},
    "idli": {"calories_per_100g": 50, "default_portion": 100},
    "samosa": {"calories_per_100g": 262, "default_portion": 100},
    "naan": {"calories_per_100g": 262, "default_portion": 100},
    "roti": {"calories_per_100g": 140, "default_portion": 60},
    "dal": {"calories_per_100g": 48, "default_portion": 200},
    "curry": {"calories_per_100g": 85, "default_portion": 200},
    "rice": {"calories_per_100g": 130, "default_portion": 200},
    "paneer": {"calories_per_100g": 265, "default_portion": 100},
    "chapati": {"calories_per_100g": 155, "default_portion": 55},
    "puri": {"calories_per_100g": 310, "default_portion": 80},
    "tandoori": {"calories_per_100g": 165, "default_portion": 200},
    "masala": {"calories_per_100g": 120, "default_portion": 200},
    "pakora": {"calories_per_100g": 229, "default_portion": 100},
}

RECOMMENDATIONS = {
    "low": "Low calorie food - Great for weight management! 🥗",
    "moderate": "Balanced portion - Perfect for a healthy meal! ⚡",
    "high": "High calorie content - Enjoy in moderation! 🔥",
    "very_high": "Very high calories - Save for special occasions! ⭐"
}


class ImagePreprocessor:
    """Handles image preprocessing for model inference"""
    
    @staticmethod
    def load_image(image_path, target_size=(640, 640)):
        """Load and preprocess image"""
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Invalid image file")
            
            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize while maintaining aspect ratio
            h, w = img_rgb.shape[:2]
            scale = min(target_size[0] / w, target_size[1] / h)
            new_w, new_h = int(w * scale), int(h * scale)
            
            resized = cv2.resize(img_rgb, (new_w, new_h))
            
            # Pad to target size
            padded = np.zeros((target_size[0], target_size[1], 3), dtype=np.uint8)
            padded[:new_h, :new_w] = resized
            
            return padded, img_rgb
            
        except Exception as e:
            raise ValueError(f"Image preprocessing failed: {str(e)}")
    
    @staticmethod
    def normalize_image(img):
        """Normalize image to [0, 1] range"""
        return img.astype(np.float32) / 255.0


class CalorieEstimator:
    """Estimates calories based on detected food"""
    
    @staticmethod
    def estimate_calories(food_name, portion_grams=None):
        """Estimate calories for detected food"""
        food_key = food_name.lower().strip()
        
        # Check if food exists in database
        if food_key in CALORIE_DATABASE:
            food_info = CALORIE_DATABASE[food_key]
            portion = portion_grams or food_info["default_portion"]
            calories = (food_info["calories_per_100g"] / 100) * portion
            return {
                "food": food_name,
                "portion": f"{portion}g",
                "calories": int(calories),
                "calories_per_100g": food_info["calories_per_100g"]
            }
        else:
            # Default estimate for unknown food
            return {
                "food": food_name,
                "portion": f"{portion_grams or 200}g",
                "calories": 200,  # Conservative estimate
                "calories_per_100g": 100
            }
    
    @staticmethod
    def get_recommendation(total_calories):
        """Get health recommendation based on calories"""
        if total_calories < 300:
            return RECOMMENDATIONS["low"]
        elif total_calories < 600:
            return RECOMMENDATIONS["moderate"]
        elif total_calories < 900:
            return RECOMMENDATIONS["high"]
        else:
            return RECOMMENDATIONS["very_high"]


class ResultFormatter:
    """Formats results for API response"""
    
    @staticmethod
    def format_result(detected_foods, total_calories, recommendation):
        """Format detection results"""
        return {
            "food_items": detected_foods,
            "total_calories": total_calories,
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
    
    @staticmethod
    def format_error(error_message):
        """Format error response"""
        return {
            "success": False,
            "error": error_message,
            "timestamp": datetime.now().isoformat()
        }
