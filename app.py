import streamlit as st
from transformers import DetrImageProcessor, DetrForObjectDetection
from PIL import Image, ImageDraw, ImageFont
import torch

# --- CONFIGURATION ---
st.set_page_config(page_title="AI Object Detector", page_icon="🔍")

# --- 1. LOAD MODEL (Cloud Cache) ---
# This downloads the model to Hugging Face's RAM, not yours.
@st.cache_resource
def load_model():
    # We use Facebook's DETR (End-to-End Object Detection)
    processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
    model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")
    return processor, model

processor, model = load_model()

# --- 2. THE DETECTION FUNCTION ---
def detect_objects(image):
    # Prepare image for the AI
    inputs = processor(images=image, return_tensors="pt")
    
    # Forward pass (The AI "Thinking")
    outputs = model(**inputs)

    # Convert outputs to bounding boxes (only keep high confidence > 0.9)
    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]
    
    return results

# --- 3. UI LAYOUT ---
st.title("🔍 AI Object Detector")
st.markdown("Upload an image. The AI will draw boxes around what it sees.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    
    # Create a draw object to draw boxes on the image
    draw = ImageDraw.Draw(image)
    
    with st.spinner("🤖 Scanning image..."):
        # Run detection
        results = detect_objects(image)
        
        # Draw boxes
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            box = [round(i, 2) for i in box.tolist()]
            
            # The AI gives us coordinates: [xmin, ymin, xmax, ymax]
            # We draw the rectangle
            draw.rectangle(box, outline="red", width=3)
            
            # Label the object (e.g., "cat: 0.99")
            label_text = f"{model.config.id2label[label.item()]}: {round(score.item(), 2)}"
            draw.text((box[0], box[1]), label_text, fill="red")

    # Show the final image
    st.image(image, caption="Processed Image", use_container_width=True)
    
    # Print list of found objects
    st.success(f"Found {len(results['scores'])} objects!")
