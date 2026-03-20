import os
import uuid
from deepface import DeepFace

UPLOAD_DIR = "uploads/faces"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def verify_face(known_image_path: str, incoming_image_bytes: bytes) -> bool:
    import base64
    
    known_path_to_use = known_image_path
    temp_known_path = None
    
    if known_image_path and known_image_path.startswith("data:image"):
        header, encoded = known_image_path.split(",", 1)
        known_bytes = base64.b64decode(encoded)
        temp_known_path = f"temp_known_{uuid.uuid4().hex}.jpg"
        with open(temp_known_path, "wb") as f:
            f.write(known_bytes)
        known_path_to_use = temp_known_path
    elif not os.path.exists(known_image_path):
        return False
    
    # Save incoming image temporarily with a unique name
    temp_path = f"temp_{uuid.uuid4().hex}.jpg"
    with open(temp_path, "wb") as f:
        f.write(incoming_image_bytes)
        
    try:
        result = DeepFace.verify(
            img1_path=known_path_to_use, 
            img2_path=temp_path, 
            model_name="VGG-Face",
            enforce_detection=True,
            align=True
        )
        return result.get("verified", False)
    except ValueError as ve:
        if "Face could not be detected" in str(ve):
            raise Exception("Yuzingiz aniqlanmadi! Iltimos, yorug'roq joyda rasmga tushing.")
        raise Exception(f"Yuz xatoligi: {str(ve)}")
    except Exception as e:
        print(f"Face verification error: {e}")
        raise Exception(f"Yuzni aniqlashda xatolik: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        if temp_known_path and os.path.exists(temp_known_path):
            try:
                os.remove(temp_known_path)
            except:
                pass
