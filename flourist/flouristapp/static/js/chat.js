 function endMessage(event) {

    if (event) {
        event.preventDefault();
    }

    let message = document.getElementById("msg").value;

    if (message.trim() == "") {
        return;
    }

    fetch("/ai-chat/", {

        method: "POST",

        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },

        body: JSON.stringify({
            message: message
        })

    })

    .then(response => response.json())

    .then(data => {

        let chatBox = document.getElementById("chat-box");

        // User Message
        chatBox.innerHTML += `
        <div class="user-msg">
            <b>👤 You</b><br>
            ${message}
        </div>`;

        // AI Reply
        let html = `
        <div class="ai-msg">
            <b>🤖 AI Assistant</b><br><br>
             ${(data.reply || "").replace(/\n/g,"<br>")}
        </div>`;

         // Product Cards
if (data.products && data.products.length > 0) {

    data.products.forEach(product => {

        html += `
        <div class="product-card">

            <img src="${product.image}" class="product-img">

            <h4>${product.name}</h4>

            <p>₹${product.price}</p>

             <a href="/add-to-cart/${product.category}/${product.id}/"
   class="cart-btn">
    🛒 Add to Cart
</a>

<a href="/wishlist/add/${product.id}/${product.category}/"
   class="wish-btn">
    ❤️ Wishlist
</a>

        </div>`;
    });

}

        chatBox.innerHTML += html;

        document.getElementById("msg").value = "";

        chatBox.scrollTop = chatBox.scrollHeight;

        // Speak AI Reply
        let speech = new SpeechSynthesisUtterance(data.reply || ""); 

        speech.lang = "en-US";
        speech.rate = 1;
        speech.pitch = 1;

        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(speech);

    })

    .catch(error => {
        console.log("Error:", error);
    });

}


// =======================
// CSRF TOKEN
// =======================

function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {

            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + "=")) {

                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;
            }
        }
    }

    return cookieValue;
}


// =======================
// VOICE INPUT
// =======================

function startVoice() {

    if (!('webkitSpeechRecognition' in window)) {
        alert("Speech Recognition is not supported.");
        return;
    }

    const recognition = new webkitSpeechRecognition();

    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = function () {
        console.log("Listening...");
    };

    recognition.onresult = function(event){

        let text = event.results[0][0].transcript;

        document.getElementById("msg").value = text;

        endMessage();
    };

    recognition.onerror = function(event){
        console.log(event.error);
    };

    recognition.onend = function(){
        console.log("Voice Ended");
    };

    recognition.start();

}


