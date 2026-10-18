import io
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from PIL import Image
from ultralytics import YOLO

app = FastAPI(
    title="RoadGuard AI - Pothole Detection API",
    description="Inference API for YOLO Pothole Detection model deployed on Render.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load lightweight pretrained model on startup
# Replace 'yolo11n.pt' with path to your 'best.pt' if uploaded to repository
MODEL_PATH = os.getenv("MODEL_PATH", "yolo11n.pt")
try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    model = None
    print(f"Error loading model {MODEL_PATH}: {e}")

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "RoadGuard AI Pothole Detector",
        "model_loaded": model is not None
    }

@app.post("/predict")
async def predict_pothole(file: UploadFile = File(...), conf_threshold: float = 0.25):
    if not model:
        raise HTTPException(status_code=500, detail="YOLO Model is not loaded on server.")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Run YOLO inference on CPU
        results = model.predict(source=image, conf=conf_threshold, device="cpu")
        result = results[0]

        detections = []
        for box in result.boxes:
            coords = box.xyxy[0].tolist()  # [xmin, ymin, xmax, ymax]
            confidence = float(box.conf[0])
            cls_id = int(box.cls[0])
            class_name = result.names[cls_id]

            detections.append({
                "bbox": [round(c, 2) for c in coords],
                "confidence": round(confidence, 4),
                "class": class_name
            })

        return JSONResponse(content={
            "filename": file.filename,
            "detected_potholes_count": len(detections),
            "detections": detections
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

@app.post("/predict-image")
async def predict_and_annotate(file: UploadFile = File(...), conf_threshold: float = 0.25):
    if not model:
        raise HTTPException(status_code=500, detail="YOLO Model is not loaded on server.")

    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    
    results = model.predict(source=image, conf=conf_threshold, device="cpu")
    annotated_array = results[0].plot()  # Returns BGR numpy array
    
    annotated_image = Image.fromarray(annotated_array[..., ::-1])  # Convert BGR to RGB
    
    img_byte_arr = io.BytesIO()
    annotated_image.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)

    return StreamingResponse(img_byte_arr, media_type="image/jpeg")