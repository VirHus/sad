import wave
import os
from xor_cipher import KEY, xor_encrypt  # Import the fixed key and XOR functions

def hide_document_in_audio(audio_path, doc_path, output_audio):
    """Hides a document inside an audio file using LSB and XOR encryption."""
    try:
        # Extract file extension (e.g., ".docx", ".xlsx")
        file_extension = os.path.splitext(doc_path)[1]
        if not file_extension:
            return "Error: No file extension found."

        print(f"Encoding file with extension: {file_extension}")  # Debugging

        # Read the document in binary
        with open(doc_path, "rb") as file:
            doc_data = file.read()

        # Convert extension to bytes and prepend it
        extension_bytes = (file_extension + "|||").encode()
        full_data = extension_bytes + doc_data

        # Encrypt the data using the fixed key
        encrypted_data = xor_encrypt(full_data, KEY)

        # Open the audio file and read its frames
        with wave.open(audio_path, "rb") as audio:
            params = audio.getparams()
            frames = bytearray(audio.readframes(audio.getnframes()))

        # Check if the audio file is large enough
        if len(encrypted_data) * 8 > len(frames):
            return "Error: Audio file too small to hide document."

        # Embed the encrypted data into the audio's LSB
        for i in range(len(encrypted_data)):
            byte = encrypted_data[i]
            for j in range(8):
                frames[i * 8 + j] = (frames[i * 8 + j] & 0xFE) | ((byte >> j) & 1)

        # Write the stego audio file
        with wave.open(output_audio, "wb") as new_audio:
            new_audio.setparams(params)
            new_audio.writeframes(frames)

        return "Success: Document hidden in audio."

    except Exception as e:
        return f"Error: {e}"
