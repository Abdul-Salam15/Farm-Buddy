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

// ========== LANGUAGE SUPPORT ==========
const translations = {
    'en': {
        'subtitle': 'Type or speak your questions • Phase 3: Voice-Enabled',
        'placeholder': 'Type, speak, or upload an image...',
        'newChat': '+ New Chat',
        'listening': 'Listening... (click mic to stop)',
        'welcome': 'Welcome to FarmBuddy! 🌾',
        'intro': "I'm your AI agricultural advisor for Nigerian smallholder farmers.",
        'topics': 'Ask me anything about:',
        'topic1': '🌱 Crop planting and management',
        'topic2': '🐛 Pest control',
        'topic3': '💧 Irrigation and soil health',
        'topic4': '📊 Farming best practices'
    },
    'ha': {
        'subtitle': 'Rubuta ko kayi magana • Mataki na 3: Voice-Enabled',
        'placeholder': 'Rubuta, yi magana, ko ɗauki hoto...',
        'newChat': '+ Sabuwar Tattaunawa',
        'listening': 'Ina sauraro... (danna mic don tsayawa)',
        'welcome': 'Barka da zuwa FarmBuddy! 🌾',
        'intro': 'Ni ne mai ba ku shawara kan harkar noma don manoman Najeriya.',
        'topics': 'Tambaye ni komai game da:',
        'topic1': '🌱 Shuka da kula da amfanin gona',
        'topic2': '🐛 Kula da kwari',
        'topic3': '💧 Ban ruwa da lafiyar kasa',
        'topic4': '📊 Mafi kyawun hanyoyin noma'
    },
    'ig': {
        'subtitle': 'Dee ma ọ bụ kwuo okwu • Agba nke 3: Voice-Enabled',
        'placeholder': 'Dee, kwuo, ma ọ bụ tinye foto...',
        'newChat': '+ Nkata Ọhụrụ',
        'listening': 'Ana m ege ntị... (pịa mic ka ị kwụsị)',
        'welcome': 'Nnọọ na FarmBuddy! 🌾',
        'intro': 'Abụ m onye ndụmọdụ ọrụ ugbo gị maka ndị ọrụ ugbo na Naijiria.',
        'topics': 'Jụọ m ihe ọ bụla gbasara:',
        'topic1': '🌱 Ịkụ ihe ọkụkụ na njikwa',
        'topic2': '🐛 Nchịkwa ụmụ ahụhụ',
        'topic3': '💧 Ịgbara mmiri na ahụike ala',
        'topic4': '📊 Ụzọ kachasị mma maka ọrụ ugbo'
    },
    'yo': {
        'subtitle': 'Tẹ tabi sọrọ • Ipele 3: Voice-Enabled',
        'placeholder': 'Tẹ, sọrọ, tabi gbe aworan si...',
        'newChat': '+ Ifọrọwerọ Titun',
        'listening': 'Mo n tẹtisi... (tẹ mic lati da duro)',
        'welcome': 'Kaabo si FarmBuddy! 🌾',
        'intro': 'Emi ni olugbamoran iṣẹ-ogbin AI rẹ fun awọn agbe kekere ni Nigeria.',
        'topics': 'Beere ohunkohun nipa:',
        'topic1': '🌱 Gbingbin ati itọju irugbin',
        'topic2': '🐛 Iṣakoso kokoro',
        'topic3': '💧 Imudani omi ati ilera ile',
        'topic4': '📊 Awọn iṣe ti o dara julọ ninu iṣẹ-ogbin'
    }
};

let currentLanguage = localStorage.getItem('language') || 'en';

function updateLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('language', lang);

    // Update Dropdown
    const langSelect = document.getElementById('languageSelect');
    if (langSelect) langSelect.value = lang;

    const t = translations[lang];
    if (!t) return;

    // Update static elements
    const subtitle = document.querySelector('.subtitle');
    if (subtitle) subtitle.textContent = t.subtitle;

    const userInput = document.getElementById('userInput');
    if (userInput) userInput.placeholder = t.placeholder;

    const newChatBtn = document.getElementById('newChatBtn');
    if (newChatBtn) newChatBtn.textContent = t.newChat;

    const recordingText = document.querySelector('#recordingIndicator span');
    if (recordingText) recordingText.textContent = t.listening;

    // Update welcome message if present
    const welcomeTitle = document.querySelector('.welcome-message h2');
    if (welcomeTitle) welcomeTitle.textContent = t.welcome;

    const welcomeIntro = document.querySelector('.welcome-message p:nth-of-type(1)');
    if (welcomeIntro) welcomeIntro.textContent = t.intro;

    const welcomeTopics = document.querySelector('.welcome-message p:nth-of-type(2)');
    if (welcomeTopics) welcomeTopics.textContent = t.topics;

    const listing = document.querySelectorAll('.welcome-message li');
    if (listing.length >= 4) {
        listing[0].textContent = t.topic1;
        listing[1].textContent = t.topic2;
        listing[2].textContent = t.topic3;
        listing[3].textContent = t.topic4;
    }
}

// ========== MAIN INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', function () {
    console.log("FarmBuddy Chat Initializing...");

    // 1. Language Init
    updateLanguage(currentLanguage);
    const langSelect = document.getElementById('languageSelect');
    if (langSelect) {
        langSelect.addEventListener('change', function () {
            updateLanguage(this.value);
        });
    }

    // 2. DOM Elements
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const messagesContainer = document.getElementById('messagesContainer');
    const sendBtn = document.getElementById('sendBtn');
    const newChatBtn = document.getElementById('newChatBtn');
    const imageInput = document.getElementById('imageInput');
    const imageBtn = document.getElementById('imageBtn');
    const locationBtn = document.getElementById('locationBtn');
    const themeToggle = document.getElementById('themeToggle');
    const sunIcon = themeToggle ? themeToggle.querySelector('.sun-icon') : null;
    const moonIcon = themeToggle ? themeToggle.querySelector('.moon-icon') : null;

    // 3. Location Handling
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
                        const response = await fetch('/chat/api/weather/', {
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

    // 4. Theme Handling 
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
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'light');
                if (sunIcon) sunIcon.style.display = 'none';
                if (moonIcon) moonIcon.style.display = 'block';
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                if (sunIcon) sunIcon.style.display = 'block';
                if (moonIcon) moonIcon.style.display = 'none';
            }
        });
    }

    // 5. Image Handling
    let currentImage = null;
    let imagePreviewDiv = null;

    if (imageBtn && imageInput) {
        imageBtn.addEventListener('click', function () {
            imageInput.click();
        });

        imageInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (!file) return;

            if (!file.type.startsWith('image/')) {
                alert('Please select an image file');
                return;
            }

            if (file.size > 5 * 1024 * 1024) {
                alert('Image too large. Maximum size is 5MB');
                return;
            }

            currentImage = file;
            showImagePreview(file);
        });
    }

    function showImagePreview(file) {
        if (imagePreviewDiv) {
            imagePreviewDiv.remove();
        }

        const reader = new FileReader();
        reader.onload = function (e) {
            imagePreviewDiv = document.createElement('div');
            imagePreviewDiv.className = 'image-preview-container';
            imagePreviewDiv.innerHTML = `
                <img src="${e.target.result}" class="image-preview" alt="Preview">
                <button class="remove-image-btn" id="removeImageBtn">×</button>
            `;

            chatForm.parentNode.insertBefore(imagePreviewDiv, chatForm);

            // Add event listener to the dynamic button
            document.getElementById('removeImageBtn').addEventListener('click', function (e) {
                e.preventDefault(); // Prevent form submission
                removeImagePreview();
            });
        };
        reader.readAsDataURL(file);
    }

    window.removeImagePreview = function () {
        if (imagePreviewDiv) {
            imagePreviewDiv.remove();
            imagePreviewDiv = null;
        }
        currentImage = null;
        if (imageInput) imageInput.value = '';
    };

    // 6. Auto-resize textarea
    if (userInput) {
        userInput.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });

        userInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }

    // 7. Form Submission
    if (chatForm) {
        chatForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            console.log("Form submitted");

            const message = userInput.value.trim();

            if (!message && !currentImage) return;

            sendBtn.disabled = true;

            try {
                let response;

                if (currentImage) {
                    const previewUrl = URL.createObjectURL(currentImage);
                    addMessage('user', message, previewUrl);
                    showLoading();

                    const formData = new FormData();
                    formData.append('image', currentImage);
                    formData.append('message', message);

                    userInput.value = '';
                    userInput.style.height = 'auto';
                    removeImagePreview();

                    response = await fetch('/chat/upload/', {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrftoken
                        },
                        body: formData
                    });
                } else {
                    addMessage('user', message);
                    userInput.value = '';
                    userInput.style.height = 'auto';
                    showLoading();

                    response = await fetch('/chat/send/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken
                        },
                        body: JSON.stringify({
                            message: message,
                            language: currentLanguage
                        })
                    });

                    // Streaming Logic
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();

                    addMessage('assistant', '', null, false);
                    const lastMessageDiv = messagesContainer.lastElementChild;
                    const textDiv = lastMessageDiv.querySelector('.message-text');
                    const contentDiv = lastMessageDiv.querySelector('.message-content');

                    let fullText = "";
                    let buffer = "";

                    removeLoading();

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;

                        buffer += decoder.decode(value, { stream: true });
                        const lines = buffer.split('\n');
                        buffer = lines.pop() || "";

                        for (const line of lines) {
                            if (!line.trim()) continue;
                            try {
                                const data = JSON.parse(line);
                                if (data.chunk) {
                                    fullText += data.chunk;
                                    if (typeof marked !== 'undefined') {
                                        textDiv.innerHTML = marked.parse(fullText);
                                    } else {
                                        textDiv.textContent = fullText;
                                    }
                                    scrollToBottom();
                                } else if (data.error) {
                                    textDiv.textContent += "\n[Error: " + data.error + "]";
                                } else if (data.full_text) {
                                    fullText = data.full_text;
                                }
                            } catch (e) {
                                console.error("Error parsing stream chunk:", e);
                            }
                        }
                    }
                    addSpeakerButton(contentDiv, fullText);
                }

                if (response && !response.ok && !response.body) {
                    // Handle non-streaming errors if any
                    const errData = await response.json();
                    throw new Error(errData.error || 'Request failed');
                }

            } catch (error) {
                removeLoading();
                addMessage('assistant', 'Sorry, there was a connection error: ' + error.message);
                console.error('Error:', error);
            } finally {
                sendBtn.disabled = false;
                if (userInput) userInput.focus();
            }
        });
    }

    // 8. New Chat
    if (newChatBtn) {
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
                        window.location.reload();
                    }
                }
            } catch (error) {
                console.error('Error creating new chat:', error);
            }
        });
    }

    // 9. Voice Controls
    const micBtn = document.getElementById('micBtn');
    if (micBtn) {
        micBtn.addEventListener('click', function () {
            if (!supportsVoice) {
                alert('Speech recognition is not supported in your browser.');
                return;
            }

            if (isRecording) {
                stopRecording();
            } else {
                try {
                    if (recognition) {
                        recognition.start();
                    } else {
                        console.error("Recognition not initialized");
                    }
                } catch (error) {
                    console.error('Error starting recognition:', error);
                }
            }
        });
    }

    // 10. Initial Render
    if (typeof marked !== 'undefined') {
        document.querySelectorAll('.message').forEach(msgDiv => {
            const textDiv = msgDiv.querySelector('.message-text');
            const contentDiv = msgDiv.querySelector('.message-content');

            if (textDiv && !textDiv.dataset.rendered) {
                const rawText = textDiv.textContent.trim();
                textDiv.innerHTML = marked.parse(rawText);
                textDiv.dataset.rendered = 'true';

                if (msgDiv.classList.contains('assistant') && supportsTTS) {
                    addSpeakerButton(contentDiv, rawText);
                }
            }
        });
    }
    scrollToBottom();

}); // End DOMContentLoaded


// ========== HELPER FUNCTIONS (Outside Init) ==========

// Voice state
let isRecording = false;
let recognition = null;
const supportsVoice = 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window;
const supportsTTS = 'speechSynthesis' in window;

if (supportsVoice) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    let finalTranscript = '';

    recognition.onstart = function () {
        const micBtn = document.getElementById('micBtn');
        const recordingIndicator = document.getElementById('recordingIndicator');
        if (micBtn) micBtn.classList.add('recording');
        if (recordingIndicator) recordingIndicator.style.display = 'flex';
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
        const userInput = document.getElementById('userInput');
        if (userInput) {
            userInput.value = finalTranscript + interimTranscript;
            userInput.dispatchEvent(new Event('input'));
        }
    };

    recognition.onerror = function (event) {
        console.error('Speech recognition error:', event.error);
        stopRecording();
    };

    recognition.onend = function () {
        if (isRecording) {
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
    if (micBtn) micBtn.classList.remove('recording');
    if (recordingIndicator) recordingIndicator.style.display = 'none';
    isRecording = false;
    if (recognition) {
        recognition.stop();
    }
}

function scrollToBottom() {
    const messagesContainer = document.getElementById('messagesContainer');
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

function addMessage(role, content, imageUrl = null, animate = false) {
    const messagesContainer = document.getElementById('messagesContainer');
    if (!messagesContainer) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🌾';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';

    if (imageUrl) {
        const img = document.createElement('img');
        img.src = imageUrl;
        img.className = 'message-image';
        img.onclick = function () {
            window.open(this.src, '_blank');
        };
        contentDiv.appendChild(img);
    }

    if (role === 'assistant' && animate) {
        let i = 0;
        const speed = 10;

        function typeWriter() {
            if (i < content.length) {
                const chunk = content.slice(0, i + 3);
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
                    textDiv.innerHTML = marked.parse(content);
                } else {
                    textDiv.classList.add('raw-text');
                    textDiv.textContent = content;
                }
                scrollToBottom();
                addSpeakerButton(contentDiv, textDiv.innerText);
            }
        }
        typeWriter();
    } else {
        if (typeof marked !== 'undefined') {
            textDiv.innerHTML = marked.parse(content);
        } else {
            textDiv.classList.add('raw-text');
            textDiv.textContent = content;
        }

        if (role === 'assistant') {
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

function showLoading() {
    const messagesContainer = document.getElementById('messagesContainer');
    if (!messagesContainer) return;

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

function removeLoading() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

function speakMessage(text, button) {
    if (!supportsTTS) {
        alert('Text-to-speech is not supported in your browser.');
        return;
    }

    if (button.classList.contains('playing')) {
        speechSynthesis.cancel();
        button.classList.remove('playing');
        button.querySelector('span').textContent = 'Listen';
        return;
    }

    if (speechSynthesis.speaking) {
        speechSynthesis.cancel();
        document.querySelectorAll('.speaker-btn').forEach(btn => {
            btn.classList.remove('playing');
            btn.querySelector('span').textContent = 'Listen';
        });
    }

    button.classList.add('playing');
    button.querySelector('span').textContent = 'Stop';

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    utterance.lang = 'en-US';

    const voices = speechSynthesis.getVoices();
    const englishVoice = voices.find(voice => voice.lang.startsWith('en'));
    if (englishVoice) {
        utterance.voice = englishVoice;
    }

    utterance.onend = function () {
        button.classList.remove('playing');
        button.querySelector('span').textContent = 'Listen';
    };

    utterance.onerror = function () {
        button.classList.remove('playing');
        button.querySelector('span').textContent = 'Listen';
    };

    speechSynthesis.speak(utterance);
}

// Rename chat
window.renameConversation = async function (id, currentTitle) {
    const newTitle = prompt("Enter new name for this chat:", currentTitle);
    if (newTitle && newTitle.trim() !== "" && newTitle !== currentTitle) {
        try {
            const response = await fetch(`/chat/api/rename/${id}/`, {
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
            const response = await fetch(`/chat/api/delete/${id}/`, {
                method: 'POST', // or DELETE
                headers: {
                    'X-CSRFToken': csrftoken
                }
            });

            if (response.ok) {
                window.location.reload();
            } else {
                alert('Error deleting chat');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error deleting chat. Please try again.');
        }
    }
};


