// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// ========== VOICE FUNCTIONALITY ==========

// Voice state
let isRecording = false;
let recognition = null;
let synthesis = window.speechSynthesis;
let currentUtterance = null;

// Check browser support
const supportsVoice = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
const supportsTTS = 'speechSynthesis' in window;

// Initialize Speech Recognition
if (supportsVoice) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = true;  // Changed to continuous
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    let finalTranscript = '';

    recognition.onstart = function () {
        const micBtn = document.getElementById('micBtn');
        const recordingIndicator = document.getElementById('recordingIndicator');
        micBtn.classList.add('recording');
        recordingIndicator.style.display = 'flex';
        isRecording = true;
        finalTranscript = '';
    };

    recognition.onresult = function (event) {
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }

        userInput.value = finalTranscript + interimTranscript;
        userInput.dispatchEvent(new Event('input')); // Trigger auto-resize
    };

    recognition.onerror = function (event) {
        console.error('Speech recognition error:', event.error);
        if (event.error !== 'no-speech' && event.error !== 'aborted') {
            alert('Speech recognition error: ' + event.error);
        }
        stopRecording();
    };

    recognition.onend = function () {
        if (isRecording) {
            // Auto-restart if still recording (unless manually stopped)
            try {
                recognition.start();
            } catch (e) {
                stopRecording();
            }
        }
    };
}

function stopRecording() {
    const micBtn = document.getElementById('micBtn');
    const recordingIndicator = document.getElementById('recordingIndicator');
    micBtn.classList.remove('recording');
    recordingIndicator.style.display = 'none';
    isRecording = false;
    if (recognition) {
        recognition.stop();
    }
}

// DOM Elements
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const messagesContainer = document.getElementById('messagesContainer');
const sendBtn = document.getElementById('sendBtn');
const newChatBtn = document.getElementById('newChatBtn');
const imageInput = document.getElementById('imageInput');
const imageBtn = document.getElementById('imageBtn');

// Image upload state
let currentImage = null;
let imagePreviewDiv = null;

// Image button click - trigger file input
if (imageBtn && imageInput) {
    imageBtn.addEventListener('click', function () {
        imageInput.click();
    });

    // Handle image selection
    imageInput.addEventListener('change', async function (e) {
        const file = e.target.files[0];
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file');
            return;
        }

        // Validate file size (5MB max)
        if (file.size > 5 * 1024 * 1024) {
            alert('Image too large. Maximum size is 5MB');
            return;
        }

        // Store the file
        currentImage = file;

        // Create image preview
        showImagePreview(file);
    });
}

// Show image preview before upload
function showImagePreview(file) {
    // Remove existing preview if any
    if (imagePreviewDiv) {
        imagePreviewDiv.remove();
    }

    const reader = new FileReader();
    reader.onload = function (e) {
        imagePreviewDiv = document.createElement('div');
        imagePreviewDiv.className = 'image-preview-container';
        imagePreviewDiv.innerHTML = `
            <img src="${e.target.result}" class="image-preview" alt="Preview">
            <button class="remove-image-btn" onclick="removeImagePreview()">×</button>
        `;

        // Insert before the form
        chatForm.parentNode.insertBefore(imagePreviewDiv, chatForm);
    };
    reader.readAsDataURL(file);
}

// Remove image preview
window.removeImagePreview = function () {
    if (imagePreviewDiv) {
        imagePreviewDiv.remove();
        imagePreviewDiv = null;
    }
    currentImage = null;
    imageInput.value = '';
};

// Auto-resize textarea
userInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// Handle Enter key (Shift+Enter for newline, Enter to send)
userInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

// Scroll to bottom of messages
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Add message to UI
function addMessage(role, content, imageUrl = null, animate = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🌾';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';

    // Add image if provided
    if (imageUrl) {
        const img = document.createElement('img');
        img.src = imageUrl;
        img.className = 'message-image';
        img.onclick = function () {
            window.open(this.src, '_blank');
        };
        contentDiv.appendChild(img);
    }

    // Render content
    if (role === 'assistant' && animate) {
        // Typewriter effect for assistant
        let i = 0;
        const speed = 10; // ms per char

        function typeWriter() {
            if (i < content.length) {
                // Determine a chunk to add (to speed up rendering of long text)
                const chunk = content.slice(0, i + 3); // Add 3 chars at a time
                if (typeof marked !== 'undefined') {
                    textDiv.classList.remove('raw-text');
                    textDiv.innerHTML = marked.parse(chunk);
                } else {
                    textDiv.classList.add('raw-text');
                    textDiv.textContent = chunk;
                }
                i += 3;
                scrollToBottom();
                setTimeout(typeWriter, speed);
            } else {
                if (typeof marked !== 'undefined') {
                    textDiv.classList.remove('raw-text');
                    textDiv.innerHTML = marked.parse(content); // Final render
                } else {
                    textDiv.classList.add('raw-text');
                    textDiv.textContent = content; // Fallback
                }
                scrollToBottom();

                // Add speaker button after typing is done. Use innerText for clean reading.
                addSpeakerButton(contentDiv, textDiv.innerText);
            }
        }
        typeWriter();
    } else {
        // Instant render for user or history
        // Check if marked is available (it might fail if loaded too late)
        if (typeof marked !== 'undefined') {
            textDiv.innerHTML = marked.parse(content);
        } else {
            textDiv.classList.add('raw-text');
            textDiv.textContent = content;
        }

        if (role === 'assistant') {
            // Use innerText for clean reading
            addSpeakerButton(contentDiv, textDiv.innerText);
        }
    }

    contentDiv.appendChild(textDiv);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function addSpeakerButton(container, text) {
    if (!supportsTTS) return;

    const speakerBtn = document.createElement('button');
    speakerBtn.className = 'speaker-btn';
    speakerBtn.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none">
            <path d="M3 9V15H7L12 20V4L7 9H3Z" fill="currentColor"/>
            <path d="M16.5 12C16.5 10.23 15.48 8.71 14 7.97V16.02C15.48 15.29 16.5 13.77 16.5 12Z" fill="currentColor"/>
            <path d="M14 4.45V6.52C16.89 7.56 19 10.04 19 13C19 15.96 16.89 18.44 14 19.48V21.55C18.01 20.45 21 16.62 21 13C21 9.38 18.01 5.55 14 4.45Z" fill="currentColor"/>
        </svg>
        <span>Listen</span>
    `;
    speakerBtn.onclick = function () {
        speakMessage(text, speakerBtn);
    };
    container.appendChild(speakerBtn);
}

// Show loading indicator
function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant loading-message';
    loadingDiv.id = 'loadingIndicator';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🌾';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const dotsDiv = document.createElement('div');
    dotsDiv.className = 'loading-dots';
    dotsDiv.innerHTML = '<span></span><span></span><span></span>';

    contentDiv.appendChild(dotsDiv);
    loadingDiv.appendChild(avatar);
    loadingDiv.appendChild(contentDiv);

    messagesContainer.appendChild(loadingDiv);
    scrollToBottom();
}

// Remove loading indicator
function removeLoading() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

// Handle form submission
chatForm.addEventListener('submit', async function (e) {
    e.preventDefault();

    const message = userInput.value.trim();

    // Check if we have an image or message
    if (!message && !currentImage) return;

    // Disable send button
    sendBtn.disabled = true;

    try {
        let response;

        if (currentImage) {
            // Handle image upload

            // Create preview URL for immediate display
            const previewUrl = URL.createObjectURL(currentImage);
            addMessage('user', message, previewUrl);
            showLoading(); // Show loading AFTER user message

            const formData = new FormData();
            formData.append('image', currentImage);
            formData.append('message', message);

            // Clear input and image state immediately
            userInput.value = '';
            userInput.style.height = 'auto';
            removeImagePreview(); // This clears currentImage too

            response = await fetch('/chat/upload/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                body: formData
            });
        } else {
            // Handle text-only message
            addMessage('user', message);

            // Clear input
            userInput.value = '';
            userInput.style.height = 'auto';
            showLoading(); // Show loading AFTER user message

            response = await fetch('/chat/send/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ message: message })
            });
        }


        // Check if response is ok first
        if (!response.ok) {
            let errorText = await response.text();

            // Try to parse JSON error from response
            try {
                const jsonError = JSON.parse(errorText);
                errorText = jsonError.error || errorText;
            } catch (e) {
                // If not JSON, use the raw text (truncated if too long)
                if (errorText.length > 200) {
                    // Check for common HTML errors
                    if (errorText.includes('<title>')) {
                        const match = errorText.match(/<title>(.*?)<\/title>/);
                        if (match) errorText = "Server Error: " + match[1];
                        else errorText = "Server Error (HTML response)";
                    } else {
                        errorText = errorText.substring(0, 200) + "...";
                    }
                }
            }
            throw new Error(`Server returned ${response.status}: ${errorText}`);
        }

        const data = await response.json();

        removeLoading();

        if (data.success) {
            // Add AI response to UI with animation
            addMessage('assistant', data.response, null, true);
        } else {
            addMessage('assistant', 'Sorry, I encountered an error: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        removeLoading();
        addMessage('assistant', 'Sorry, there was a connection error: ' + error.message);
        console.error('Error:', error);
    } finally {
        sendBtn.disabled = false;
        userInput.focus();
    }
});

// New chat button
newChatBtn.addEventListener('click', async function () {
    try {
        const response = await fetch('/chat/new/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            }
        });

        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                window.location.href = `/chat/${data.conversation_id}/`;
            } else {
                window.location.reload(); // Fallback
            }
        }
    } catch (error) {
        console.error('Error creating new chat:', error);
    }
});

// ========== VOICE CONTROLS EVENT LISTENERS ==========

// Microphone button - Toggle start/stop recording
const micBtn = document.getElementById('micBtn');
if (micBtn) {
    micBtn.addEventListener('click', function () {
        if (!supportsVoice) {
            alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
            return;
        }

        if (isRecording) {
            // Stop recording
            stopRecording();
        } else {
            // Start recording
            try {
                recognition.start();
            } catch (error) {
                console.error('Error starting recognition:', error);
            }
        }
    });
}

// Text-to-speech function for individual messages
function speakMessage(text, button) {
    if (!supportsTTS) {
        alert('Text-to-speech is not supported in your browser.');
        return;
    }

    // If this button is currently playing, stop it
    if (button.classList.contains('playing')) {
        synthesis.cancel();
        button.classList.remove('playing');
        button.querySelector('span').textContent = 'Listen';
        return;
    }

    // If another message is speaking, stop it first
    if (synthesis.speaking) {
        synthesis.cancel();
        // Remove playing class from all speaker buttons
        document.querySelectorAll('.speaker-btn').forEach(btn => {
            btn.classList.remove('playing');
            btn.querySelector('span').textContent = 'Listen';
        });
    }

    // Mark this button as playing
    button.classList.add('playing');
    button.querySelector('span').textContent = 'Stop';

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;  // Slightly slower for clarity
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    utterance.lang = 'en-US';

    // Get available voices and prefer English voice
    const voices = synthesis.getVoices();
    const englishVoice = voices.find(voice => voice.lang.startsWith('en'));
    if (englishVoice) {
        utterance.voice = englishVoice;
    }

    // Reset button when done
    utterance.onend = function () {
        button.classList.remove('playing');
        button.querySelector('span').textContent = 'Listen';
    };

    utterance.onerror = function () {
        button.classList.remove('playing');
        button.querySelector('span').textContent = 'Listen';
    };

    synthesis.speak(utterance);
}


// Auto-scroll on page load and render Markdown history
window.addEventListener('load', function () {
    // Render Markdown for existing messages
    if (typeof marked !== 'undefined') {
        document.querySelectorAll('.message').forEach(msgDiv => {
            const textDiv = msgDiv.querySelector('.message-text');
            const contentDiv = msgDiv.querySelector('.message-content');

            if (textDiv && !textDiv.dataset.rendered) {
                const rawText = textDiv.textContent.trim();

                // Render Markdown
                textDiv.innerHTML = marked.parse(rawText);
                textDiv.dataset.rendered = 'true';

                // Add speaker button if assistant
                if (msgDiv.classList.contains('assistant') && supportsTTS) {
                    addSpeakerButton(contentDiv, rawText);
                }
            }
        });
    }
    scrollToBottom();
});

// Rename chat
window.renameConversation = async function (id, currentTitle) {
    const newTitle = prompt("Enter new name for this chat:", currentTitle);
    if (newTitle && newTitle.trim() !== "" && newTitle !== currentTitle) {
        try {
            const response = await fetch(`/chat/rename/${id}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ title: newTitle.trim() })
            });

            if (response.ok) {
                window.location.reload();
            } else {
                alert('Error renaming chat');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error renaming chat. Please try again.');
        }
    }
};

// Delete chat
window.deleteConversation = async function (id) {
    if (confirm("Are you sure you want to delete this chat? This cannot be undone.")) {
        try {
            const response = await fetch(`/chat/delete/${id}/`, {
                method: 'POST', // or DELETE
                headers: {
                    'X-CSRFToken': csrftoken
                }
            });

            if (response.ok) {
                // If we are on the deleted chat page, go to index
                // Or just reload which is easiest
                window.location.href = '/chat/';
            } else {
                alert('Error deleting chat');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error deleting chat. Please try again.');
        }
    }
};

// Location Handling
document.addEventListener('DOMContentLoaded', function () {
    const locationBtn = document.getElementById('locationBtn');
    if (locationBtn) {
        locationBtn.addEventListener('click', function () {
            if (!navigator.geolocation) {
                alert('Geolocation is not supported by your browser');
                return;
            }

            this.classList.add('loading');

            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    try {
                        const response = await fetch('/chat/weather/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrftoken
                            },
                            body: JSON.stringify({
                                lat: position.coords.latitude,
                                lon: position.coords.longitude
                            })
                        });

                        const data = await response.json();

                        if (data.success) {
                            // Add system message to UI
                            addMessage('system', `📍 ${data.report}`);
                        } else {
                            alert('Error fetching weather: ' + (data.error || 'Unknown error'));
                        }
                    } catch (err) {
                        console.error('Weather error:', err);
                        alert('Failed to connect to weather service');
                    } finally {
                        this.classList.remove('loading');
                    }
                },
                (error) => {
                    this.classList.remove('loading');
                    let msg = 'Error getting location';
                    switch (error.code) {
                        case error.PERMISSION_DENIED: msg = 'Location permission denied'; break;
                        case error.POSITION_UNAVAILABLE: msg = 'Location unavailable'; break;
                        case error.TIMEOUT: msg = 'Location request timed out'; break;
                    }
                    alert(msg);
                }
            );
        });
    }
});

// Theme Handling
document.addEventListener('DOMContentLoaded', function () {
    const themeToggle = document.getElementById('themeToggle');
    const sunIcon = themeToggle ? themeToggle.querySelector('.sun-icon') : null;
    const moonIcon = themeToggle ? themeToggle.querySelector('.moon-icon') : null;

    // Check local storage
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (sunIcon) sunIcon.style.display = 'block';
        if (moonIcon) moonIcon.style.display = 'none';
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';

            if (isDark) {
                // Switch to Light
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'light');
                if (sunIcon) sunIcon.style.display = 'none';
                if (moonIcon) moonIcon.style.display = 'block';
            } else {
                // Switch to Dark
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                if (sunIcon) sunIcon.style.display = 'block';
                if (moonIcon) moonIcon.style.display = 'none';
            }
        });
    }
});
