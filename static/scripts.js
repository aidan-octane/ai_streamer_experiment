$(document).ready(function() {
    console.log("Document is ready!" );

    var socket = io.connect(window.location.protocol + '//' + window.location.hostname + ':' + window.location.port);
    console.log("SocketIO connection initialized!" );

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
        appendCommandMessage(data.text)
    });

    function appendCommandMessage(text) {
        var messageContainer = $('#command_content');
        var newMessage = $('<p>').text(text); 

        messageContainer.append(newMessage);

        messageContainer.scrollTop(messageContainer[0].scrollHeight);
    }

    socket.on('update_message_content', function(data) {
        appendChatMessage(data.text)
    });

    
    function appendChatMessage(text) {
        var messageContainer = $('#message_content');
        var newMessage = $('<p>').text(text); 

        messageContainer.append(newMessage);


        messageContainer.scrollTop(messageContainer[0].scrollHeight);

    }
});
