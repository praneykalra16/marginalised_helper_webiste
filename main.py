import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import os
import speech_recognition as sr
from googletrans import Translator, LANGUAGES
from gtts import gTTS
import io
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import tempfile

# Set up the directory containing the sign language images
IMAGE_DIR = 'path - to sign language data folder'

# Function to load an image given a letter
def load_image(letter):
    image_path = os.path.join(IMAGE_DIR, f'{letter.upper()}_test.jpg')
    return Image.open(image_path)

# Function to take audio command
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        st.write("Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        return query

    except Exception as e:
        st.write("Error:", e)
        return "Please try again"

# Function to translate text
def translate_text(text, target_language):
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    return translation.text

# Function to extract audio from video
def extract_audio_from_video(video_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        video = VideoFileClip(video_file)
        video.audio.write_audiofile(temp_audio_file.name)
        temp_audio_file_path = temp_audio_file.name
    return temp_audio_file_path

# Function to convert audio to text
def audio_to_text(audio_file):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_wav(audio_file)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
        audio.export(temp_wav_file.name, format="wav")
        temp_wav_file_path = temp_wav_file.name
    with sr.AudioFile(temp_wav_file_path) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
    return text

# Main application
def main():
    st.sidebar.title("Navigation")
    selected = option_menu(
        menu_title=None,
        options=["Sign Language Translator", "Audio to Text Converter", "Text Translation", "Text to Speech Converter", "Video to Text Extractor"],
        icons=["sign-language", "mic", "translate", "volume-up", "video"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
    )

    if selected == "Sign Language Translator":
        st.title("Sign Language Translator")

        # User input
        user_input = st.text_input("Enter a word:")

        if user_input:
            st.write(f"Translating '{user_input}' into sign language:")

            # Display images for each letter in the user input
            for letter in user_input:
                if letter.isalpha():  # Ensure the character is a letter
                    try:
                        image = load_image(letter)
                        st.image(image, caption=f"Letter: {letter.upper()}")
                    except FileNotFoundError:
                        st.write(f"No image found for letter: {letter.upper()}")

    elif selected == "Audio to Text Converter":
        st.title("Audio to Text Converter")

        if st.button("Start Recording"):
            with st.spinner("Recording..."):
                text = take_command()
                st.write("Transcribed Text:")
                st.write(text)

    elif selected == "Text Translation":
        st.title("Text Translation App")

        st.write("Enter text to be translated:")
        text = st.text_area("Text", "")

        st.write("Select target language:")
        language_options = list(LANGUAGES.values())
        target_language = st.selectbox("Language", language_options)

        if st.button("Translate"):
            if text and target_language:
                # Find the language code for the selected language
                language_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(target_language)]

                translated_text = translate_text(text, language_code)
                st.subheader("Translated Text")
                st.write(translated_text)
            else:
                st.error("Please enter text and select a language.")

    elif selected == "Text to Speech Converter":
        st.title("Text to Speech Converter")

        # Text input
        text = st.text_area("Enter text here:")

        if st.button("Speak"):
            if text:
                # Convert text to speech
                tts = gTTS(text=text, lang='en')
                audio_file = io.BytesIO()
                tts.write_to_fp(audio_file)
                audio_file.seek(0)

                # Play audio
                st.audio(audio_file, format="audio/mp3")
            else:
                st.warning("Please enter some text.")

    elif selected == "Video to Text Extractor":
        st.title("Video to Text Extractor")

        uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "avi", "mov", "mkv"])

        if uploaded_file:
            st.video(uploaded_file)

            # Temporary file to save the uploaded video
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
                temp_video_file.write(uploaded_file.read())
                temp_video_file_path = temp_video_file.name

            st.write("Extracting audio and converting to text...")

            # Extract audio from the uploaded video
            audio_file = extract_audio_from_video(temp_video_file_path)
            # Convert audio to text
            text = audio_to_text(audio_file)

            st.subheader("Extracted Text")
            st.write(text)

            # Clean up temporary files
            os.remove(temp_video_file_path)
            os.remove(audio_file)

if __name__ == "__main__":
    main()
