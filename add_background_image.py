"""
Helper script to convert your background image to base64 for use in Streamlit
"""
import base64
from pathlib import Path

def image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def get_background_css(image_path):
    """Generate CSS for background image"""
    img_base64 = image_to_base64(image_path)
    file_ext = Path(image_path).suffix.lower()
    mime_type = "image/jpeg" if file_ext in [".jpg", ".jpeg"] else "image/png"
    
    css = f"""
    <style>
    .main {{
        background-image: url("data:{mime_type};base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    .block-container {{
        background: rgba(255, 255, 255, 0.90);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem auto;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        backdrop-filter: blur(10px);
    }}
    </style>
    """
    return css

if __name__ == "__main__":
    # Example usage
    image_path = "static/images/skills-background.png"
    
    if Path(image_path).exists():
        print("Background CSS generated successfully!")
        print("\nCopy the CSS below into your app.py:")
        print("="*60)
        print(get_background_css(image_path))
    else:
        print(f"Image not found: {image_path}")
        print("\nPlease save your background image as:")
        print("  static/images/skills-background.png")
        print("  OR")
        print("  static/images/skills-background.jpg")
