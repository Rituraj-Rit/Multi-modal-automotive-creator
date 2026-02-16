// Global state
let generationInProgress = false;

/**
 * Generate automotive visualization
 */
async function generateVisualization() {
    const designPrompt = document.getElementById('designPrompt').value.trim();
    const context = document.getElementById('contextInput').value.trim();
    const enhanceImage = document.getElementById('enhanceImage').checked;

    // Validation
    if (!designPrompt) {
        alert('Please enter a design concept description');
        return;
    }

    // Prevent multiple submissions
    if (generationInProgress) {
        return;
    }

    generationInProgress = true;
    toggleLoadingState(true);
    hideResults();

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                design_prompt: designPrompt,
                context: context || undefined,
                enhance_image: enhanceImage
            })
        });

        const data = await response.json();

        if (!data.success) {
            showError(data.error || 'Failed to generate visualization');
            return;
        }

        // Display results
        displayResults(data);

    } catch (error) {
        console.error('Error:', error);
        showError(`Network error: ${error.message}`);
    } finally {
        generationInProgress = false;
        toggleLoadingState(false);
    }
}

/**
 * Display generation results
 */
function displayResults(data) {
    // Display narrative
    const narrativeContent = document.getElementById('narrativeContent');
    narrativeContent.textContent = data.narrative;

    // Display metadata
    const tokens = data.metadata.llm_tokens || 0;
    document.getElementById('narrativeMetadata').innerHTML =
        `<strong>Tokens used:</strong> ${tokens}`;

    // Display generated image
    if (data.image_data) {
        const img = document.getElementById('generatedImage');
        img.src = `data:image/png;base64,${data.image_data}`;
    }

    // Display image prompt
    const imagePromptContent = document.getElementById('imagePromptContent');
    imagePromptContent.value = data.image_prompt || '';

    // Show results section
    showResults();
}

/**
 * Show error message
 */
function showError(message) {
    const errorPanel = document.getElementById('errorPanel');
    const errorContent = document.getElementById('errorContent');
    errorContent.textContent = message;
    errorPanel.classList.remove('hidden');
    document.getElementById('results').classList.remove('hidden');
}

/**
 * Toggle loading spinner visibility
 */
function toggleLoadingState(isLoading) {
    const spinner = document.getElementById('loadingSpinner');
    const generateBtn = document.getElementById('generateBtn');

    if (isLoading) {
        spinner.classList.remove('hidden');
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';
    } else {
        spinner.classList.add('hidden');
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate Visualization';
    }
}

/**
 * Show results section
 */
function showResults() {
    const resultsSection = document.getElementById('results');
    resultsSection.classList.remove('hidden');
    
    // Hide error panel if showing results
    const errorPanel = document.getElementById('errorPanel');
    errorPanel.classList.add('hidden');
    
    // Scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

/**
 * Hide results section
 */
function hideResults() {
    const resultsSection = document.getElementById('results');
    resultsSection.classList.add('hidden');
}

/**
 * Clear the form
 */
function clearForm() {
    document.getElementById('designPrompt').value = '';
    document.getElementById('contextInput').value = '';
    document.getElementById('enhanceImage').checked = false;
    hideResults();
}

/**
 * Download generated image
 */
function downloadImage() {
    const img = document.getElementById('generatedImage');
    const link = document.createElement('a');
    link.href = img.src;
    link.download = `automotive-design-${Date.now()}.png`;
    link.click();
}

/**
 * Copy image prompt to clipboard
 */
function copyImagePrompt() {
    const textarea = document.getElementById('imagePromptContent');
    textarea.select();
    document.execCommand('copy');
    
    // Show feedback
    const btn = event.target;
    const originalText = btn.textContent;
    btn.textContent = 'Copied!';
    setTimeout(() => {
        btn.textContent = originalText;
    }, 2000);
}

/**
 * Handle Enter key in textarea
 */
document.addEventListener('DOMContentLoaded', function() {
    const designPromptField = document.getElementById('designPrompt');
    
    // Allow Ctrl+Enter to submit
    designPromptField.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            generateVisualization();
        }
    });

    // Check API configuration on load
    checkApiConfiguration();
});

/**
 * Check if APIs are properly configured
 */
async function checkApiConfiguration() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (!data.configuration.all_configured) {
            console.warn('Warning: Not all APIs are configured', data.configuration);
            // You could show a warning banner here
        }
    } catch (error) {
        console.error('Failed to check API configuration:', error);
    }
}
