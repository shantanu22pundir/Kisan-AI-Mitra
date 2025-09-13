import os
from PIL import Image
import google.generativeai as genai
from django.conf import settings
from .models import UserSubmission  # Import your model


# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

def analyze_with_gemini(image_path=None):
    """
    Fetch the most recent image from the database and send it to Gemini for plant/tree analysis.
    """
    # Get latest submission
    latest_submission = UserSubmission.objects.order_by('-created_at').first()
    if not latest_submission or not latest_submission.image:
        return "No recent image found."

    image_path = latest_submission.image.path

    # Gemini model
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Custom plant/tree analysis prompt
    prompt = (
        "You are a plant and tree identification expert.\n"
        "Analyze the image provided and respond ONLY in the following structured Markdown format:\n\n"
        "## 🌱 Plant Identification Report\n"
        "**📷 Identified Species:** [Plant Name] (*Scientific Name*)\n"
        "**🔍 Identification Details:**\n"
        "- Key leaf/bark/flower traits.\n"
        "- Any special identifying features.\n\n"
        "---\n"
        "### 1️⃣ Best Season to Grow\n"
        "- [Season details]\n\n"
        "### 2️⃣ Optimal Environmental Conditions\n"
        "| Factor | Ideal Range / Requirement |\n"
        "|--------|----------------------------|\n"
        "| **Temperature** | [value] |\n"
        "| **Soil Type** | [value] |\n"
        "| **Humidity** | [value] |\n"
        "| **Sunlight** | [value] |\n\n"
        "### 3️⃣ Disease Check\n"
        "- Current Image Status: [Healthy / Diseased]\n"
        "- Common Diseases List\n\n"
        "### 4️⃣ Recovery & Treatment Methods\n"
        "| Issue | Solution |\n"
        "|-------|----------|\n"
        "| Root Rot | [treatment] |\n"
        "| Leaf Spot | [treatment] |\n"
        "| Powdery Mildew | [treatment] |\n"
        "| Insect Pests | [treatment] |\n\n"
        "**⚠️ Note:**\n"
        "This analysis is based solely on the provided image. For accurate diagnosis, consult a local arborist.\n\n\n\n"
    
        "आप एक पौधों और वृक्षों की पहचान के विशेषज्ञ हैं।\n"
        "दिए गए चित्र का विश्लेषण करें और केवल नीचे दिए गए संरचित Markdown प्रारूप में हिंदी भाषा में उत्तर दें:\n\n"
        "## 🌱 पौधा पहचान रिपोर्ट\n"
        "**📷 पहचानी गई प्रजाति:** [पौधे का नाम] (*वैज्ञानिक नाम*)\n"
        "**🔍 पहचान विवरण:**\n"
        "- पत्तियों/छाल/फूलों की मुख्य विशेषताएं।\n"
        "- कोई विशेष पहचान चिन्ह।\n\n"
        "---\n"
        "### 1️⃣ उगाने का सर्वोत्तम मौसम\n"
        "- [मौसम का विवरण]\n\n"
        "### 2️⃣ आदर्श पर्यावरणीय परिस्थितियां\n"
        "| कारक | आदर्श सीमा / आवश्यकता |\n"
        "|-------|------------------------|\n"
        "| **तापमान** | [मान] |\n"
        "| **मिट्टी का प्रकार** | [मान] |\n"
        "| **नमी** | [मान] |\n"
        "| **धूप** | [मान] |\n\n"
        "### 3️⃣ रोग जांच\n"
        "- वर्तमान चित्र स्थिति: [स्वस्थ / रोगग्रस्त]\n"
        "- सामान्य रोगों की सूची\n\n"
        "### 4️⃣ पुनर्प्राप्ति और उपचार विधियां\n"
        "| समस्या | समाधान |\n"
        "|--------|---------|\n"
        "| जड़ सड़न | [उपचार] |\n"
        "| पत्ती धब्बा | [उपचार] |\n"
        "| पाउडरी फफूंदी | [उपचार] |\n"
        "| कीट संक्रमण | [उपचार] |\n\n"
        "**⚠️ नोट:**\n"
        "यह विश्लेषण केवल दिए गए चित्र पर आधारित है। सटीक निदान के लिए, स्थानीय वृक्ष विशेषज्ञ से परामर्श लें।"
)   

        

    inputs = [
        prompt,
        {
            "mime_type": "image/jpeg",
            "data": open(image_path, "rb").read()
        }
    ]


    # Get AI response
    response = model.generate_content(inputs)
    return response.text


def process_image(file_path):
    """
    Returns basic image info (size).
    """
    img = Image.open(file_path)
    return img.size
