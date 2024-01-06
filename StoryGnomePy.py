from flask import Flask, render_template, request
import speech_recognition as sr
import openai
import pyttsx3
import concurrent.futures

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = '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'

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def generate_text_with_openai(prompt, result_dict, enable_audio=True):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=1500
    )
    generated_text = response['choices'][0]['text']
    
    result_dict['generated_text'] = generated_text
    
    if enable_audio:
        text_to_speech(generated_text)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_audio', methods=['POST'])
def process_audio_route():
    if request.method == 'POST':
        audio_text = real_time_speech_to_text()
        enable_audio = request.form.get('audio_enabled', 'false') == 'true'
        
        if audio_text:
            openai_prompt = f"'{audio_text}'"
            
            # Using a dictionary to store the result of the OpenAI generation
            result_dict = {}
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Submit OpenAI API call for text generation and audio for generated text
                future_openai = executor.submit(generate_text_with_openai, openai_prompt, result_dict, enable_audio)
                
                # Wait for the OpenAI API call to complete
                future_openai.result()

            # Display the generated text on the results page
            return render_template('result.html', input_prompt=audio_text, generated_text=result_dict.get('generated_text', ''))

def real_time_speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")

        try:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            print('Prompt:', text)
            return text

        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Error with the request to Google Web Speech API; {e}")

if __name__ == '__main__':
    app.run(debug=True)
