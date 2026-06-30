// ========================================
// NutriFy - Results Page JavaScript
// Displays meal analysis results
// ========================================

window.currentFoods = [];

document.addEventListener('DOMContentLoaded', function () {
    // Get result from session storage
    const resultData = sessionStorage.getItem('mealResult');

    if (!resultData) {
        // No result data, redirect to upload
        window.location.href = '/upload';
        return;
    }

    const result = JSON.parse(resultData);

    // Display results
    displayResults(result);
    setupInteractions();
});

/**
 * Display meal analysis results
 */
function displayResults(result) {
    const { detailed_foods, total_calories, recommendation, filename, food_items } = result;

    // Display food image if available
    if (filename) {
        document.getElementById('resultImage').src = `/uploads/${filename}`;
    }

    // Set the global variable and draw the buttons!
    window.currentFoods = detailed_foods || [];
    renderInteractiveList();

    // Set category badge based on names
    setCategoryBadge(food_items);

    // Animate elements
    animateResultsIn();
}

// --- NEW INTERACTIVE LOGIC ---

window.renderInteractiveList = function() {
    const container = document.getElementById('interactive-food-list');
    if (!container) return;
    container.innerHTML = '';

    let grandTotalCals = 0;
    let totalItemsCount = 0;
    let grandTotalGrams = 0; // NEW: Track total plate weight!

    if (window.currentFoods.length === 0) {
        container.innerHTML = '<span class="food-item-tag">Unknown Food</span>';
    } else {
        // Loop through the data and build the rows
        window.currentFoods.forEach((item, index) => {
            const itemTotalCals = item.count * item.base_calories;
            const itemTotalGrams = item.count * (item.grams_per_unit || 0); // Calculate live grams
            
            grandTotalCals += itemTotalCals;
            grandTotalGrams += itemTotalGrams;
            totalItemsCount += item.count;

            const row = document.createElement('div');
            row.className = 'food-row';
            
            // NEW: Added a smaller grey text block specifically for the grams!
            row.innerHTML = `
                <div class="food-name">${item.name}</div>
                <div class="counter">
                    <button onclick="window.changeCount(${index}, -1)">-</button>
                    <input type="number" min="0" value="${item.count}" onchange="window.setManualCount(${index}, this.value)">
                    <button onclick="window.changeCount(${index}, 1)">+</button>
                </div>
                <div class="food-cals">
                    <div>${itemTotalCals} kcal</div>
                    <div style="font-size: 0.85em; color: #757575; font-weight: normal; margin-top: 2px;">${itemTotalGrams}g</div>
                </div>
            `;
            container.appendChild(row);
        });
    }

    // Live update the giant numbers on the page
   
    const totalCalsEl = document.getElementById('totalCalories');
    if (totalCalsEl) totalCalsEl.textContent = `${grandTotalCals} kcal`;

    const totalWeightEl = document.getElementById('totalMealWeight');
    if (totalWeightEl) totalWeightEl.textContent = `${grandTotalGrams}g`;
    
    // Safety checks for stat updates
    
    // Safety checks for stat updates
    const statCalsEl = document.getElementById('statCalories');
    if (statCalsEl) statCalsEl.textContent = grandTotalCals;
    
    const foodCountEl = document.getElementById('foodCount');
    if (foodCountEl) foodCountEl.textContent = totalItemsCount;

    const mealsPerDayEl = document.getElementById('mealsPerDay');
    if (mealsPerDayEl) {
        const mealsPerDay = grandTotalCals > 0 ? (2000 / grandTotalCals).toFixed(1) : 0;
        mealsPerDayEl.textContent = mealsPerDay;
    }

    // Live update Health Warning & Stars
    updateLiveRecommendation(grandTotalCals);
    setRating(grandTotalCals);
};

window.changeCount = function(index, changeAmount) {
    let newCount = window.currentFoods[index].count + changeAmount;
    if (newCount < 0) newCount = 0; // No negative food!
    window.currentFoods[index].count = newCount;
    window.renderInteractiveList(); // Redraw UI instantly
};

window.setManualCount = function(index, newValue) {
    let parsedValue = parseInt(newValue);
    if (isNaN(parsedValue) || parsedValue < 0) parsedValue = 0;
    window.currentFoods[index].count = parsedValue;
    window.renderInteractiveList(); // Redraw UI instantly
};

function updateLiveRecommendation(totalCals) {
    const recElement = document.getElementById('recommendation');
    if (!recElement) return;

    if (totalCals > 800) {
        recElement.textContent = "High calorie meal. Consider portion control! ⚠️";
        recElement.style.color = "#d32f2f";
    } else if (totalCals < 300) {
        recElement.textContent = "Light snack. Good for a quick energy boost! ⚡";
        recElement.style.color = "#0288d1";
    } else {
        recElement.textContent = "Balanced portion. Perfect for a healthy meal! 🥗";
        recElement.style.color = "var(--primary-color)";
    }
}



/**
 * Set health rating based on calories
 */
function setRating(calories) {
    let rating = 5;
    let ratingText = '5/5 - Excellent';

    if (calories < 200) {
        rating = 4;
        ratingText = '4/5 - Very Healthy';
    } else if (calories < 400) {
        rating = 4.5;
        ratingText = '4.5/5 - Balanced';
    } else if (calories < 600) {
        rating = 3.5;
        ratingText = '3.5/5 - Moderate';
    } else if (calories < 800) {
        rating = 3;
        ratingText = '3/5 - High Calories';
    } else {
        rating = 2.5;
        ratingText = '2.5/5 - Very High';
    }

    const ratingStars = document.querySelector('.rating-stars');
    const ratingTextElement = document.getElementById('ratingText');

    // Create stars based on rating
    let stars = '';
    for (let i = 1; i <= 5; i++) {
        if (i <= Math.floor(rating)) {
            stars += '<span class="star filled">★</span>';
        } else if (i - rating < 1 && rating > Math.floor(rating)) {
            stars += '<span class="star half">★</span>';
        } else {
            stars += '<span class="star empty">★</span>';
        }
    }

    ratingStars.innerHTML = stars;
    ratingTextElement.textContent = ratingText;
}

/**
 * Set category badge
 */
function setCategoryBadge(foodItems) {
    const categoryBadge = document.getElementById('categoryBadge');
    const categoryDescription = document.querySelector('.category-description');

    let category = 'Mixed Meal';
    let description = 'This is a well-balanced meal';

    if (foodItems && foodItems.length > 0) {
        const firstFood = foodItems[0].toLowerCase();

        if (firstFood.includes('dosa') || firstFood.includes('idli')) {
            category = 'South Indian';
            description = 'Traditional South Indian breakfast or meal with good nutrition value';
        } else if (firstFood.includes('biryani') || firstFood.includes('rice')) {
            category = 'Rice Dish';
            description = 'A rice-based main course meal, popular in Indian cuisine';
        } else if (firstFood.includes('naan') || firstFood.includes('roti') || firstFood.includes('bread')) {
            category = 'Bread & Bread Items';
            description = 'Flour-based traditional Indian bread, great source of carbs';
        } else if (firstFood.includes('curry') || firstFood.includes('dal')) {
            category = 'Curry/Lentils';
            description = 'Protein-rich curry or lentil preparation, excellent nutritional value';
        } else if (firstFood.includes('samosa') || firstFood.includes('pakora')) {
            category = 'Snacks/Appetizers';
            description = 'Fried snack items, enjoy in moderation for balanced diet';
        } else {
            category = 'Main Course';
            description = 'A balanced main course meal with good nutrition value';
        }
    }

    categoryBadge.querySelector('.category-text').textContent = category;
    categoryDescription.textContent = description;
}

/**
 * Setup interactions
 */
function setupInteractions() {
    // Share buttons
    const shareButtons = document.querySelectorAll('.btn-share');
    const mealResult = sessionStorage.getItem('mealResult');

    shareButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const shareText = `📊 I just analyzed my meal with NutriFy AI! Check out the results: ${location.href}`;

            const btnContent = this.textContent.trim();
            if (btnContent === '𝕏') {
                // Twitter share
                window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`);
            } else if (btnContent === 'f') {
                // Facebook share
                window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(location.href)}`);
            } else if (btnContent === '🔗') {
                // Copy link
                navigator.clipboard.writeText(location.href);
                this.textContent = '✓ Copied!';
                setTimeout(() => {
                    this.textContent = '🔗';
                }, 2000);
            }
        });
    });

    // Similar foods carousel
    setupSimilarFoods();
}

/**
 * Setup similar foods carousel
 */
function setupSimilarFoods() {
    const similarFoods = {
        'biryani': [
            { name: 'Pulao', emoji: '🍚', calories: 280 },
            { name: 'Khichdi', emoji: '🥘', calories: 220 },
            { name: 'Fried Rice', emoji: '🍛', calories: 250 }
        ],
        'dosa': [
            { name: 'Uttapam', emoji: '🥞', calories: 180 },
            { name: 'Idli', emoji: '⚪', calories: 100 },
            { name: 'Pesarattu', emoji: '🥞', calories: 165 }
        ],
        'samosa': [
            { name: 'Pakora', emoji: '🍛', calories: 229 },
            { name: 'Kachori', emoji: '🥒', calories: 300 },
            { name: 'Spring Roll', emoji: '🥡', calories: 210 }
        ]
    };

    // Get first food item
    const resultData = sessionStorage.getItem('mealResult');
    if (!resultData) return;

    const result = JSON.parse(resultData);
    const foodKey = result.food_items?.[0]?.toLowerCase() || '';

    let suggestions = [];
    for (let key in similarFoods) {
        if (foodKey.includes(key)) {
            suggestions = similarFoods[key];
            break;
        }
    }

    // If no specific suggestions, use random ones
    if (suggestions.length === 0) {
        suggestions = [
            { name: 'Biryani', emoji: '🍛', calories: 450 },
            { name: 'Khichdi', emoji: '🥘', calories: 220 },
            { name: 'Samosa', emoji: '🥒', calories: 262 }
        ];
    }

    const similarFoodsContainer = document.getElementById('similarFoods');
    similarFoodsContainer.innerHTML = '';

    suggestions.forEach(food => {
        const card = document.createElement('div');
        card.className = 'food-card';
        card.innerHTML = `
            <div class="food-image">${food.emoji}</div>
            <h4>${food.name}</h4>
            <p>${food.calories} kcal</p>
        `;
        similarFoodsContainer.appendChild(card);
    });
}

/**
 * Animate results appearance
 */
function animateResultsIn() {
    const mainCard = document.querySelector('.results-main-card');
    const analysisCards = document.querySelectorAll('.analysis-card');

    mainCard?.classList.add('slide-up');

    analysisCards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
}

/**
 * Print results
 */
window.printResults = function () {
    window.print();
};

/**
 * Download as PDF (basic - uses browser print)
 */
window.downloadPDF = function () {
    window.print();
};
