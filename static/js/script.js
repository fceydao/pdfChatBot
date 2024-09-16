/*function sendMessage(event) {
    if (event.key === 'Enter') {
        const userInput = document.getElementById('user-input').value;
        const message = userInput.value;
        if (message.trim()) {
            // Send message to the server
            fetch('/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `user_question=${userInput}`
                //body: `user_question=${encodeURIComponent(message)}`
            })
            .then(response => response.json())
            .then(data => { 
                if (data.status === 'success') {
                    updateChatBox(data.chat_history);
                }
            });
            userInput.value = '';
        }
    }
}
*/

function checkEnter(event) {
    if (event.keyCode === 13) {
        event.preventDefault();  // Enter tuşuna basıldığında formun normal gönderimini engelle
        sendMessage();
    }
}

function sendMessage() {
    const userQuestion = document.getElementById('user-input').value.trim();
    if (userQuestion) {
        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'user_question': userQuestion
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateChatBox(data.chat_history);
                document.getElementById('user-input').value = '';  // Input alanını temizle
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

/*function updateChatBox(chatHistory) {
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = ''; // Clear the chat box
    chatHistory.forEach(entry => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', entry.sender);
        messageDiv.innerHTML = `
            <div class="avatar">
                <img src="/static/images/${entry.sender}.png" style="max-height: 78px; max-width: 78px; border-radius: 0; object-fit: cover;">
            </div>
            <div class="message">${entry.message}</div>
        `;
        chatBox.appendChild(messageDiv);
    });
    chatBox.scrollTop = chatBox.scrollHeight;
}
*/

function updateChatBox(chatHistory) {
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = ''; // Clear the chat box
    for (let i = chatHistory.length - 1; i >= 0; i--) {
        const entry = chatHistory[i];
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', entry.sender);
        messageDiv.innerHTML = `
            <div class="avatar">
                <img src="/static/images/${entry.sender}.png" style="max-height: 78px; max-width: 78px; border-radius: 0; object-fit: cover;">
            </div>
            <div class="message">${entry.message}</div>
        `;
        chatBox.appendChild(messageDiv);
    }
    chatBox.scrollTop = 0;
}

function handleUploadResponse(response) {
    if (response.status === 'success') {
        alert(response.message);
        window.location.reload();
    } else {
        alert(response.message);
    }
}

function uploadFiles(event) {
    event.preventDefault();
    let formData = new FormData(document.getElementById('upload-form'));
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => handleUploadResponse(data))
    .catch(error => alert('An error occurred: ' + error));
}
