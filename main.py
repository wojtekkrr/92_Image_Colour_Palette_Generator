from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
import cv2
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SECRET_KEY'] = 'Flask_Key'


@app.route("/")
def home():
    images = [os.path.join(app.config['UPLOAD_FOLDER'], filename) for filename in
              os.listdir(app.config['UPLOAD_FOLDER'])]
    return render_template("index.html", images=images, file ="")


@app.route('/upload', methods=['POST'])
def upload():
    data = request.files
    if 'file' not in data:
        flash("No file to upload.")
        return redirect(url_for('home'))
    file = data['file']
    if file.filename == '':
        flash("File not chosen.")
        return redirect(url_for('home'))
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        image = cv2.imread(f'static/uploads/{file.filename}')
        # Przekształć obraz do formatu RGB (jeśli jest w innym formacie, na przykład BGR)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mpx = image_rgb.shape[0] * image_rgb.shape[1]
        # Splaszcz obraz do jednego wymiaru
        flattened_image = image_rgb.reshape(-1, 3)
        # Znajdź unikalne kolory i ich częstość
        unique_colors, counts = np.unique(flattened_image, axis=0, return_counts=True)
        # Posortuj kolory według częstości w odwrotnej kolejności
        sorted_indices = np.argsort(-counts)
        sorted_colors = unique_colors[sorted_indices]
        sorted_counts = counts[sorted_indices]
        # Wyświetl najczęściej występujące kolory i ich częstość
        most_popular_colors = sorted_colors[:10]

        most_popular_color_perc = []
        for count in sorted_counts[:10]:
            most_popular_color_perc.append(round(count / mpx * 100, 2))
        colors = zip(most_popular_colors, most_popular_color_perc)

        folder_path = os.getcwd() + "/static/uploads"
        files_to_delete = os.listdir(folder_path)
        for file in files_to_delete:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

        return render_template("index.html", file=file.filename, colors=colors)
        # return send_file(os.path.join(app.config['UPLOAD_FOLDER'], file.filename), as_attachment=True)



if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, port=5007)