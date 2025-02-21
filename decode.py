import wave
import os
from xor_cipher import KEY, xor_decrypt  # Import the fixed key and XOR functions

def extract_document_from_audio(stego_audio, output_folder):
    """Extracts and decrypts a document from a stego audio file."""
    try:
        # Open the stego audio and read its frames
        with wave.open(stego_audio, "rb") as audio:
            frames = bytearray(audio.readframes(audio.getnframes()))

        # Extract the encrypted data by reading the LSB of the frames
        extracted_data = bytearray()
        for i in range(0, len(frames), 8):
            byte = 0
            for j in range(8):
                byte |= (frames[i + j] & 1) << j
            extracted_data.append(byte)

        # Decrypt the extracted data using the fixed key
        decrypted_data = xor_decrypt(extracted_data, KEY)

        # Separate the file extension from the document content
        separator = b"|||"
        if separator in decrypted_data:
            extension_bytes, document_data = decrypted_data.split(separator, 1)
            file_extension = extension_bytes.decode(errors="ignore").strip()
            print(f"Extracted file extension: {file_extension}")  # Debugging
        else:
            return "Error: No file extension found in decoded data.", None

        # Ensure a valid extension
        if not file_extension.startswith("."):
            return "Error: Invalid file extension extracted.", None

        # Generate a clean extracted filename with the correct extension
        extracted_filename = f"extracted_document{file_extension}"
        extracted_doc_path = os.path.join(output_folder, extracted_filename)

        # Save the extracted document
        with open(extracted_doc_path, "wb") as extracted_file:
            extracted_file.write(document_data)

        return f"Success: Document extracted as {extracted_filename}", extracted_doc_path

    except Exception as e:
        return f"Error: {e}", None
