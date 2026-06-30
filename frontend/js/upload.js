// ========================================
// NutriFy - Upload Page JavaScript
// Handles drag-drop, file preview, upload
// ========================================

document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    const previewContainer = document.getElementById('previewContainer');
    const previewImage = document.getElementById('previewImage');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const removeBtn = document.getElementById('removeBtn');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const errorDialog = document.getElementById('errorDialog');
    const errorTitle = document.getElementById('errorTitle');
    const errorMessage = document.getElementById('errorMessage');
    const errorCloseBtn = document.getElementById('errorCloseBtn');

    let selectedFile = null;

    // ==================== EVENT LISTENERS ====================

    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => imageInput.click());

    // File input change
    imageInput.addEventListener('change', handleFileSelect);

    // Remove button
    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetUpload();
    });

    // Analyze button
    analyzeBtn.addEventListener('click', handleAnalyze);

    // Error dialog close
    errorCloseBtn.addEventListener('click', closeErrorDialog);

    // ==================== DRAG & DROP HANDLERS ====================

    function handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.style.opacity = '0.8';
        uploadArea.style.transform = 'scale(1.02)';
    }

    function handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.style.opacity = '1';
        uploadArea.style.transform = 'scale(1)';
    }

    function handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.style.opacity = '1';
        uploadArea.style.transform = 'scale(1)';

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            imageInput.files = files;
            handleFileSelect({ currentTarget: imageInput });
        }
    }

    // ==================== FILE HANDLERS ====================

    function handleFileSelect(e) {
        const file = e.currentTarget.files[0];

        if (!file) {
            return;
        }

        // Validate file type
        const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
        if (!validTypes.includes(file.type)) {
            showError('Invalid File Type', 'Please upload a valid image (JPG, PNG, GIF, BMP)');
            return;
        }

        // Validate file size (10MB)
        if (file.size > 10 * 1024 * 1024) {
            showError('File Too Large', 'Image size should be less than 10MB');
            return;
        }

        selectedFile = file;
        displayPreview(file);
    }

    function displayPreview(file) {
        const reader = new FileReader();

        reader.onload = (e) => {
            previewImage.src = e.target.result;
            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);

            // Show preview container
            uploadArea.style.display = 'none';
            previewContainer.classList.remove('hidden');
        };

        reader.readAsDataURL(file);
    }

    function resetUpload() {
        selectedFile = null;
        imageInput.value = '';
        previewContainer.classList.add('hidden');
        uploadArea.style.display = 'block';
        uploadArea.style.opacity = '1';
        uploadArea.style.transform = 'scale(1)';
    }

    // ==================== ANALYZE HANDLER ====================

    async function handleAnalyze() {
        if (!selectedFile) {
            showError('No Image Selected', 'Please select an image first');
            return;
        }

        showLoading(true);

        try {
            // Upload file
            const result = await window.NutriFy.uploadFile(selectedFile);

            // Simulate processing time
            await new Promise(resolve => setTimeout(resolve, 1500));

            // Store result in session storage
           // Store result in session storage
            sessionStorage.setItem('mealResult', JSON.stringify({
                food_items: result.food_items,
                detailed_foods: result.detailed_foods, // <--- ADD THIS LINE!
                total_calories: result.total_calories,
                recommendation: result.recommendation,
                filename: result.filename
            }));

            // Redirect to results page
            window.location.href = '/results';
        } catch (error) {
            console.error('Analysis error:', error);
            showLoading(false);
            showError(
                'Analysis Failed',
                'Could not process your image. Please try again or upload a different image.'
            );
        }
    }

    // ==================== UI HELPERS ====================

    function showLoading(show) {
        if (show) {
            loadingOverlay.classList.remove('hidden');
            // Animate progress bar
            const progressFill = loadingOverlay.querySelector('.progress-fill');
            progressFill.style.animation = 'none';
            setTimeout(() => {
                progressFill.style.animation = 'shimmer 2s infinite';
            }, 10);
        } else {
            loadingOverlay.classList.add('hidden');
        }
    }

    function showError(title, message) {
        errorTitle.textContent = title;
        errorMessage.textContent = message;
        errorDialog.classList.remove('hidden');
    }

    function closeErrorDialog() {
        errorDialog.classList.add('hidden');
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    }
});
