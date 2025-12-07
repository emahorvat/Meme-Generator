import os
from flask import Flask, render_template, request, send_from_directory, url_for
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'static/generated'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GENERATED_FOLDER'] = GENERATED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def dovoljeni_formati(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_font(size=40):
    font_paths = [
        'C:/Windows/Fonts/impact.ttf',
        'C:/Windows/Fonts/Arial.ttf',
    ]
    
    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size)
        except:
            continue
    
    return ImageFont.load_default()

def wrap_text(text, font, max_width, draw):
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def add_text(draw, text, position, font, fill_color='white', outline_color='black', outline_width=2):
    x, y = position
    
   # outline
    for adj_x in range(-outline_width, outline_width + 1):
        for adj_y in range(-outline_width, outline_width + 1):
            draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline_color)
    
    # glavni text
    draw.text(position, text, font=font, fill=fill_color)

def generiraj_meme(image_path, top_text, bottom_text):
    try:
        img = Image.open(image_path)
        
        max_size = (800, 800)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        draw = ImageDraw.Draw(img)
        
        font_size = max(20, int(img.width / 12))
        font = get_font(font_size)
        
        img_width, img_height = img.size
        
        max_text_width = img_width * 0.92
        
        if top_text:
            top_lines = wrap_text(top_text.upper(), font, max_text_width, draw)
            
            total_height = 0
            for line in top_lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                total_height += bbox[3] - bbox[1] + 3 
            
            current_y = img_height * 0.03
            
            for line in top_lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (img_width - text_width) / 2
                add_text(draw, line, (x, current_y), font)
                current_y += bbox[3] - bbox[1] + 3 
        
        if bottom_text:
            bottom_lines = wrap_text(bottom_text.upper(), font, max_text_width, draw)
            
            total_height = 0
            line_heights = []
            for line in bottom_lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_height = bbox[3] - bbox[1]
                line_heights.append(line_height)
                total_height += line_height + 3 
            
            current_y = img_height * 0.95 - total_height
            
            for i, line in enumerate(bottom_lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (img_width - text_width) / 2
                add_text(draw, line, (x, current_y), font)
                current_y += line_heights[i] + 3
        
        # shrani sliko
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'meme_{timestamp}.png'
        output_path = os.path.join(app.config['GENERATED_FOLDER'], output_filename)
        
        img.save(output_path, 'PNG')
        
        return output_filename
    
    except Exception as e:
        print(f"Napaka pri generiranju meme-a: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if 'image' not in request.files:
        return render_template('index.html', error='ni izbrane slike')
    
    file = request.files['image']
    
    if file.filename == '':
        return render_template('index.html', error='ni izbrane slike')
    
    if not dovoljeni_formati(file.filename):
        return render_template('index.html', error='Napačen format slike. Dovoljeni formati: png, jpg, jpeg, gif')
    
    top_text = request.form.get('top_text', '').strip()
    bottom_text = request.form.get('bottom_text', '').strip()
    
    if not top_text and not bottom_text:
        return render_template('index.html', error='vnesi vsaj en tekst')
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_filename = f'upload_{timestamp}_{file.filename}'
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        file.save(upload_path)
        
        meme_filename = generiraj_meme(upload_path, top_text, bottom_text)
        
        if meme_filename:
            try:
                os.remove(upload_path)
            except:
                pass
            
            return render_template('index.html', 
                                 meme_image=meme_filename,
                                 success='Meme uspešno generiran!!!')
        else:
            return render_template('index.html', error='Napaka pri generiranju mema.')
    
    except Exception as e:
        return render_template('index.html', error=f'Napaka: {str(e)}')

@app.route('/generated/<filename>')
def generated_file(filename):
    return send_from_directory(app.config['GENERATED_FOLDER'], filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)