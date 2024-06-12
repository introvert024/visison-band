import cv2
from gradio_client import Client, handle_file
from gtts import gTTS
import os
import pygame
import face_recognition  # Ensure face_recognition.py is in the same directory or correctly referenced

def capture_and_save_image():
    # Open the default camera (usually 0 for built-in webcams)
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Error: Could not open camera.")
        return False

    # Capture a single frame from the camera
    ret, frame = camera.read()

    if not ret:
        print("Error: Failed to capture image.")
        camera.release()
        return False

    # Save the captured frame as an image file
    cv2.imwrite("image.jpg", frame)

    # Release the camera
    camera.release()

    print("Image captured and saved as 'image.jpg'.")
    return True

def speak(text):
    tts = gTTS(text=text, lang='en')
    save_path = os.path.join(os.getcwd(), "result.mp3")
    
    try:
        # Ensure pygame mixer is properly initialized and stopped
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        
        # Remove the existing file if it exists
        if os.path.exists(save_path):
            os.remove(save_path)
        
        # Save the new TTS output to result.mp3
        tts.save(save_path)
        
        # Initialize pygame mixer and play the new result.mp3
        pygame.mixer.init()
        pygame.mixer.music.load(save_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except PermissionError as e:
        print(f"PermissionError: {e}")

if __name__ == "__main__":
    # Initialize Gradio client only once
    client = Client("krishnv/ImageCaptioning")
    
    while True:
        if capture_and_save_image():
            # Use Gradio client to predict something based on the saved image
            result = client.predict(
                image=handle_file('image.jpg'),
                api_name="/predict"
            )
            print("Prediction result:", result)
            
            # Check for specific keywords in the result
            keywords = ["person", "man", "woman", "young man"]
            if any(keyword in result.lower() for keyword in keywords):
                print("Keyword detected in result.")
                # Recognize faces and print the results
                img, names = face_recognition.recognize_faces()
                print("Recognized names:", names)

                # Replace keywords with recognized names or "KNOWN FACE"
                if "person" in result.lower():
                    result = result.lower().replace("a person", names[0] if names else "a person")
                if "man" in result.lower():
                    result = result.lower().replace("a man", names[0] if names else "a man")
                if "woman" in result.lower():
                    result = result.lower().replace("a woman", names[0] if names else "a woman")
                combined_result = result
                speak("i can see" + combined_result)
            else:
                # Speak the result using gtts
                speak("I can see " + result)
        
        # Optionally, add a delay between iterations to avoid capturing images too rapidly
        cv2.waitKey(1000)  # Wait for 1 second (1000 milliseconds)
