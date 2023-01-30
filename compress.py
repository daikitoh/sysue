from PIL import Image
import io

def compress(image):
    img = Image.open(image)
    width = 60
    height = 40
    resized = img.resize((width, height))
    output = io.BytesIO()
    resized.save(output, format="JPEG")
    thumb = output.getvalue()
    return thumb