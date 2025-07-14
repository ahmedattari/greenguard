document.getElementById('send-button').addEventListener('click', function () {
  sendMessage();
});

document.getElementById('user-message').addEventListener('keypress', function (e) {
  if (e.key === 'Enter') {
    e.preventDefault(); // Prevent newline
    sendMessage();
  }
});

document.getElementById('voice-note-button').addEventListener('click', function () {
  startVoiceRecognition();
});

function sendMessage() {
  let message = document.getElementById('user-message').value.trim();
  if (message !== '') {
    appendUserMessage(message);
    document.getElementById('user-message').value = '';

    // Show typing placeholder
    const typingElement = appendTypingIndicator();

    $.ajax({
      url: '/get_response',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ message: message }),
      success: function (data) {
        removeTypingIndicator(typingElement);
        appendBotMessage(data.response);
      },
      error: function () {
        removeTypingIndicator(typingElement);
        appendBotMessage("Sorry, something went wrong.");
      }
    });
  }
}

function appendUserMessage(message) {
  let messagesContainer = document.querySelector('.messages-container');
  let messageElement = document.createElement('div');
  messageElement.classList.add('message', 'user-message');
  messageElement.textContent = message;
  messagesContainer.appendChild(messageElement);
  scrollToBottom(messagesContainer);
}

function appendBotMessage(message) {
  let messagesContainer = document.querySelector('.messages-container');
  let messageElement = document.createElement('div');
  messageElement.classList.add('message', 'bot-message');
  messageElement.textContent = message;

  let ttsButton = document.createElement('button');
  ttsButton.classList.add('tts-button');
  ttsButton.innerHTML = '<i class="fas fa-volume-up"></i>';
  ttsButton.addEventListener('click', function () {
    speakText(message);
  });

  messageElement.appendChild(ttsButton);
  messagesContainer.appendChild(messageElement);
  scrollToBottom(messagesContainer);
}

function appendTypingIndicator() {
  let messagesContainer = document.querySelector('.messages-container');
  let typingElement = document.createElement('div');
  typingElement.classList.add('message', 'bot-message');
  typingElement.textContent = 'Typing...';
  messagesContainer.appendChild(typingElement);
  scrollToBottom(messagesContainer);
  return typingElement;
}

function removeTypingIndicator(element) {
  if (element && element.parentNode) {
    element.parentNode.removeChild(element);
  }
}

function scrollToBottom(container) {
  container.scrollTop = container.scrollHeight;
}

function startVoiceRecognition() {
  if (!('webkitSpeechRecognition' in window)) {
    alert('Your browser does not support speech recognition.');
    return;
  }

  const recognition = new webkitSpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onresult = function (event) {
    const speechResult = event.results[0][0].transcript;
    document.getElementById('user-message').value = speechResult;
    sendMessage();
  };

  recognition.onerror = function (event) {
    console.error('Speech recognition error:', event.error);
  };

  recognition.onend = function () {
    console.log('Speech recognition service disconnected');
  };

  recognition.start();
}

function speakText(text) {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    speechSynthesis.speak(utterance);
  } else {
    alert('Your browser does not support text-to-speech.');
  }
}
