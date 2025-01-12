let videoStream;
let recognizedCharacterDiv = document.getElementById('recognizedCharacter');
let recognizedLabelDiv = document.getElementById('recognizedLabel');
let suggestionsDiv = document.getElementById('suggestions');
let messageInput = document.querySelector('#message__form input[name="message"]');
let recognitionInterval;
let recognizedText = '';
let postNextCount = 0;
const vocabulary = ['HELLO', 'WORLD', 'SIGN', 'LANGUAGE', 'TEST']; // Add your known words here
const suggestions = {
    'A': ['Apple', 'Animal', 'Ask', 'Art', 'Ant'],
    'B': ['Ball', 'Banana', 'Bicycle', 'Bottle', 'Bird'],
    'C': ['Cat', 'Car', 'Camera', 'Cup', 'Clock'],
};

function initializeVideoStream() {
    videoStream = document.querySelector('#streams__container video');
    if (!videoStream) {
        setTimeout(initializeVideoStream, 100); // Retry after 100ms if videoStream is not found
    }
}

initializeVideoStream();

function startRecognition() {
    if (!videoStream) {
        console.error('Video stream not initialized');
        return;
    }
    if (recognitionInterval) {
        clearInterval(recognitionInterval);
    }
    recognitionInterval = setInterval(recognizeSignLanguage, 1000); // Nhận dạng mỗi giây
}

function checkAndAddSpace() {
    const words = messageInput.value.split(' ');
    const lastWord = words[words.length - 1];
    if (vocabulary.includes(lastWord.toUpperCase())) {
        messageInput.value += ' ';
    }
}

function stopRecognition() {
    if (recognitionInterval) {
        clearInterval(recognitionInterval);
        recognitionInterval = null;
    }
}

function updateSuggestions(character) {
    const upperCaseCharacter = character.toUpperCase();
    if (suggestions[upperCaseCharacter]) {
        suggestionsDiv.textContent = `Suggestions: ${suggestions[upperCaseCharacter].join(', ')}`;
    } else {
        suggestionsDiv.textContent = 'Suggestions: ';
    }
}

function recognizeSignLanguage() {
    if (!videoStream) {
        console.error('Video stream not initialized');
        return;
    }
    const canvas = document.createElement('canvas');
    canvas.width = videoStream.videoWidth;
    canvas.height = videoStream.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(videoStream, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(blob => {
        if (blob) {
            const formData = new FormData();
            formData.append('frame', blob, 'frame.png');

            fetch('/recognize/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.character && data.character !== "No hand detected" && data.character !== "Low confidence") {
                    recognizedCharacterDiv.textContent = `Character: ${data.character}`;
                    recognizedLabelDiv.textContent = `Label: ${data.label}`;
                    updateSuggestions(data.character);
                    if (data.character === 'Next') {
                        postNextCount = 0; // Reset the counter when "Next" is recognized
                        recognizedText = '';
                    } else {
                        postNextCount++;
                        if (postNextCount === 3) {
                            messageInput.value += data.character;
                            checkAndAddSpace(); // Check and add space if the last word matches a vocabulary word
                            postNextCount = 0; // Reset the counter after the third character
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error recognizing sign language: ', error);
            });
        } else {
            console.error('Failed to create Blob from canvas');
        }
    }, 'image/png');
}

function speakText(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.pitch = 1.45; // Adjust the pitch (0.0 to 2.0)
    utterance.rate = 1.0;  // Adjust the rate (0.1 to 10.0)
    window.speechSynthesis.speak(utterance);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.getElementById('recognize-btn').addEventListener('click', () => {
    if (recognitionInterval) {
        stopRecognition();
        document.getElementById('recognize-btn').classList.remove('active');
    } else {
        startRecognition();
        document.getElementById('recognize-btn').classList.add('active');
    }
});

document.getElementById('speak-btn').addEventListener('click', () => {
    const text = messageInput.value;
    speakText(text);
});