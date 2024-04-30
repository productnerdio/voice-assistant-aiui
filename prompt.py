from gtts import gTTS
import os

# Example text to be spoken
text = "Hello, how are you today?"
language = 'en'  # English

# Passing the text and language to the engine, 
# here we mark slow=False, which tells the module that 
# the converted audio should have a high speed
myobj = gTTS(text=text, lang=language, slow=False)

# Saving the converted audio in a mp3 file named 'welcome.mp3'
myobj.save("welcome.mp3")

# Playing the converted file, using a simple OS command that varies by platform
os.system("start welcome.mp3")  # This command works on Windows
# For macOS, use 'afplay welcome.mp3'
# For Linux, use 'mpg321 welcome.mp3'
