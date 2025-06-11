import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch
from reportlab.lib.utils import ImageReader # Import ImageReader

# Constants
TEMPLATE_PATH = "ute_id_template.png"
CSV_PATH = "employees.csv"
OUTPUT_PDF = "output/employee_ids.pdf"
PHOTO_DIR = "photos/"
FONT_PATH = "arial.ttf"  
FONT_SIZE_NAME = 20
FONT_SIZE_TITLE = 16

# PHOTO_BOX: (left, top, right, bottom) for the large orange square
PHOTO_BOX = (220, 10, 390, 180)

# TEXT_NAME_POS: (x, y) for the employee's name
TEXT_NAME_POS = (270, 185)

# TEXT_TITLE_POS: (x, y) for the employee's title
TEXT_TITLE_POS = (270, 205)

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

# Load template image
template_img = Image.open(TEMPLATE_PATH)
ID_WIDTH, ID_HEIGHT = template_img.size

# Load employee data
df = pd.read_csv(CSV_PATH)

# Create a PDF
# The pagesize in reportlab needs to be in points (1 inch = 72 points).
# PIL image size is in pixels. Assuming 72 DPI for conversion.
ID_WIDTH_PTS = ID_WIDTH * (1/72.0) * inch
ID_HEIGHT_PTS = ID_HEIGHT * (1/72.0) * inch

c = canvas.Canvas(OUTPUT_PDF, pagesize=(ID_WIDTH_PTS, ID_HEIGHT_PTS))

for _, row in df.iterrows():
    # Copy template for each ID card
    id_img = template_img.copy()
    draw = ImageDraw.Draw(id_img)

    # Resolve full photo path
    photo_filename = row['photo'].replace("photos/", "")
    photo_path = os.path.join(PHOTO_DIR, photo_filename)

    # Load and paste employee photo
    try:
        photo_width = PHOTO_BOX[2] - PHOTO_BOX[0]
        photo_height = PHOTO_BOX[3] - PHOTO_BOX[1]
        photo = Image.open(photo_path).resize(
            (photo_width, photo_height), Image.Resampling.LANCZOS
        )
        id_img.paste(photo, (PHOTO_BOX[0], PHOTO_BOX[1]))
    except FileNotFoundError:
        print(f"Photo not found: {photo_path}")
        continue

    # Load fonts
    try:
        font_name = ImageFont.truetype(FONT_PATH, FONT_SIZE_NAME)
        font_title = ImageFont.truetype(FONT_PATH, FONT_SIZE_TITLE)
    except OSError:
        print(" Font not found. Please ensure 'arial.ttf' exists in the directory.")
        continue

    # Draw text: Name and Title
    name_text_width = draw.textlength(row['name'], font=font_name)
    title_text_width = draw.textlength(row['title'], font=font_title)

    block_center_x = (PHOTO_BOX[0] + PHOTO_BOX[2]) / 2

    name_x_pos = block_center_x - (name_text_width / 2)
    title_x_pos = block_center_x - (title_text_width / 2)

    draw.text((name_x_pos, TEXT_NAME_POS[1]), row['name'], font=font_name, fill="black")
    draw.text((title_x_pos, TEXT_TITLE_POS[1]), row['title'], font=font_title, fill="black")

    # Convert the PIL Image to a format ReportLab can read directly (ImageReader)
    # ReportLab's drawImage can take a PIL Image object wrapped by ImageReader
    reportlab_image = ImageReader(id_img)

    # Draw the entire ID card image onto the PDF
    # The drawImage arguments are (image_reader_object, x, y, width, height) in points
    c.drawImage(reportlab_image, 0, 0, width=ID_WIDTH_PTS, height=ID_HEIGHT_PTS)
    c.showPage() # Start a new page for the next ID card

c.save()
print(f" PDF saved: {OUTPUT_PDF}")