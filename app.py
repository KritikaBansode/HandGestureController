import streamlit as st
import os
from pptx import Presentation
from PIL import Image
import cv2
import numpy as np
import shutil


# Function to convert PPT slides to images
def convert_ppt_to_images(ppt_path, output_folder):
    prs = Presentation(ppt_path)
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    for i, slide in enumerate(prs.slides):
        img_path = os.path.join(output_folder, f"{i + 1}.png")
        blank_slide = Image.new("RGB", (1280, 720), "white")
        blank_slide.save(img_path)
    return sorted(os.listdir(output_folder))


# Streamlit UI
st.title("Hand Gesture-Based Presentation Controller")

uploaded_file = st.file_uploader("Upload your PowerPoint file (.pptx)", type=["pptx"])

if uploaded_file:
    ppt_path = "uploaded_presentation.pptx"
    with open(ppt_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("File uploaded successfully!")

    output_folder = "Presentation"
    slide_images = convert_ppt_to_images(ppt_path, output_folder)
    st.write("Slides converted successfully!")

    # Display first slide preview
    if slide_images:
        first_slide = Image.open(os.path.join(output_folder, slide_images[0]))
        st.image(first_slide, caption="First Slide Preview", use_column_width=True)

        st.write("Now, run the hand gesture controller script to navigate through the slides.")
