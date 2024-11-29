document.addEventListener('DOMContentLoaded', function() {
    console.log("Document is ready!" );

    var socket = io.connect(window.location.protocol + '//' + window.location.hostname + ':' + window.location.port);
    console.log("SocketIO connection initialized!" );

    var ngrok_url;

    socket.on('get_ngrok', function(data) {
        ngrok_url = data.url;
        console.log("ngrok url: " + String(ngrok_url))
    });




    $('#inputForm').submit(function(event) {
        event.preventDefault(); 
        var textInput = $('#textInput').val();
        var actionType = $(this).find("button[type=submit]:focus").val();
        console.log("Text input: " + textInput);
        

        socket.emit('submit_message', {text : String(actionType) + ":" + String(textInput)});
        $('#textInput').val('');
    });
    
    document.getElementById("gen_rate_button").addEventListener("click", function() {
        const genRateValue = document.getElementById("gen_rate_input").value;
        
        socket.emit('submit_gen_rate', {text : String(genRateValue)});
        document.getElementById("input1").value = String(genRateValue) + ' Messages / Gen';
    });

    document.getElementById("blocklist_button").addEventListener("click", function() {
        const blocklistValue = document.getElementById("blocklist_input").value;
        
        socket.emit('submit_blocklist', {text : String(blocklistValue)});
    });

     document.getElementById("char_threshold_button").addEventListener("click", function() {
        const charThresholdValue = document.getElementById("char_threshold_input").value;
        
        socket.emit('submit_char_threshold', {text : String(charThresholdValue)});
    });

    document.getElementById("cache_button").addEventListener("click", function() {
        console.log("Message queue cleared!");

    });





    socket.on('update_command_content', function(data) {
        // appendCommandMessage(data.text)
        // fetch('http://127.0.0.1:5000/submit_admin', {
        fetch(nrgok_url + '/submit_admin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data.text)
        })
        .then(response => response.json())
        .catch(error => console.error('Error:', error));
        updateHistory(); 
    });

    // function appendCommandMessage(text) {
    //     var messageContainer = $('#command_content');
    //     var newMessage = $('<p>').text(text); 

    //     messageContainer.append(newMessage);

    //     messageContainer.scrollTop(messageContainer[0].scrollHeight);
    // }

    socket.on('update_message_content', function(data) {
        // appendChatMessage(data.text)
        // fetch('http://127.0.0.1:5000/submit_chat', {
        fetch(ngrok_url + '/submit_chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data.text)
        })
        .then(response => response.json())
        .catch(error => console.error('Error:', error));
        updateHistory(); 
    });

    
//     function appendChatMessage(text) {
//         var messageContainer = $('#message_content');
//         var newMessage = $('<p>').text(text); 

//         messageContainer.append(newMessage);


//         messageContainer.scrollTop(messageContainer[0].scrollHeight);

//     }

var oldChatHistory = [];
var oldAdminHistory = [];
function updateChatHistory() {
    const messageContainer = document.getElementById('message_container')
    // fetch('http://127.0.0.1:5000/chat_history')
    fetch(ngrok_url + '/chat_history')
    .then(response => response.json())
    .then(history => {
        if (JSON.stringify(history.history) === JSON.stringify(oldChatHistory)) {
            return;
        }
        oldChatHistory = history.history;
        messageContainer.innerHTML = '';
        history.history.forEach(item => {
            const newElement = $('<p>').text(text);
            messageContainer.appendChild(newElement);
        });
        scroller.scrollTop = scroller.scrollHeight;
    })
    .catch(error => console.error('Error fetching history:', error));
}

function updateAdminHistory() {
    const messageContainer = document.getElementById('command_container')
    // fetch('http://127.0.0.1:5000/admin_history')
    fetch(ngrok_url + '/admin_history')
    .then(response => response.json())
    .then(history => {
        if (JSON.stringify(history.history) === JSON.stringify(oldAdminHistory)) {
            return;
        }
        oldAdminHistory = history.history;
        messageContainer.innerHTML = '';
        history.history.forEach(item => {
            const newElement = $('<p>').text(text);
            messageContainer.appendChild(newElement);
        });
        scroller.scrollTop = scroller.scrollHeight;
    })
    .catch(error => console.error('Error fetching history:', error));
}

updateChatHistory();
updateAdminHistory();
setInterval(updateChatHistory, 1000);
setInterval(updateAdminHistory, 1000);


});
