from PIL import Image
import os

# 원본 이미지 경로
input_path = r'C:\Users\sadpig70\.gemini\antigravity\brain\4f683ed2-bc4c-4e7c-8ecd-dd3f11cf4970\mde_app_logo_1776515109462.png'
output_path = 'mde.ico'

def convert_to_ico(input_img, output_ico):
    if not os.path.exists(input_img):
        print(f"Error: No image found at {input_img}")
        return

    img = Image.open(input_img)
    # 표준 윈도우 아이콘 해상도 세트
    icon_sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
    img.save(output_ico, sizes=icon_sizes)
    print(f"Success: {output_ico} created.")

if __name__ == "__main__":
    convert_to_ico(input_path, output_path)
