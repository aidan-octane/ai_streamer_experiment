This is the dashboard that I built for my AI Streamer project:
https://www.youtube.com/watch?v=u4_QYREBac8&lc=UgwC60xFSosMtjimA7B4AaABAg

This project was much bigger than just these files. I also:
    - Created a dataset sufficiently large enough to train an AI model, fully by hand 
    - Trained the AI model using Unsloth in a Google Colab notebook
    - Hosted the model on Huggingface at https://huggingface.co/tachophobicat/tachophobicai_v4.0
    - Created a Python library, 'ChatGET', to easily allow programs to grab Twitch chat - https://github.com/aidan-octane/chatGET

The end product is a teleprompter-like dashboard that, during a live stream, automatically feeds me AI-generated responses to chat messages and more. The goal of the project was to determine if AI can replace me as a live streamer. If you want to see if it can, watch the YouTube video about it. The dashboard itself, however, worked flawlessly. It's hard to set something up to work flawlessly during a live stream without impacting the viewer experience, so a TON of testing, quality control, and effort went into this to ensure it went well. And it did! 

Features include:
    - Automatic chat grabbing & AI responses
    - Dynamically updating filtration system to respond to the right amount of chat messages without becoming overwhelming
    - Dynamically updating blocklist in case of any rogue chatters (did not have to use, but functioned properly)
    - Communication with the model itself to send requests for monologues, commands, and direct chat message response
    - Various buttons and whistles to interact with the dashboard itself to modify anything during the stream if at all needed
    - Globally updating, so anybody could connect to the dashboard, see the same thing, and update it for everyone - it wasn't purely local!

# TODO - Push saved final .html file from laptop to this repo!