from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import shutil
import tempfile
import os
import uvicorn

from image import get_caption_and_hashtags  # Import your function without changes

app = FastAPI()

@app.post("/generate-caption/")
async def generate_caption(image: UploadFile = File(...)):
    # Save uploaded file temporarily to call get_caption_and_hashtags(image_path)
    try:
        suffix = os.path.splitext(image.filename)[1]  # file extension e.g. '.png'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(image.file, tmp)
            temp_file_path = tmp.name

        # Call the original function from image.py
        result = get_caption_and_hashtags(temp_file_path)

        # Clean up temp file
        os.remove(temp_file_path)

        return JSONResponse(content={"result": result})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run("imageapi:app", host="0.0.0.0", port=8000, reload=True)
