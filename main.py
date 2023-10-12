from flask import Flask, render_template, request, flash, redirect, url_for
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
    return render_template("index.html", images=images, file="")


@app.route('/upload', methods=['POST'])
def upload():
    data = request.files
    # Komunikaty przy błędach powstałych podczas wczytywania plików
    if 'file' not in data:
        flash("No file to upload.")
        return redirect(url_for('home'))
    file = data['file']
    if file.filename == '':
        flash("File not chosen.")
        return redirect(url_for('home'))
    if file:
        # Zapisanie obrazu
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        image = cv2.imread(f'static/uploads/{file.filename}')
        # Przekształcenie obraz do formatu RGB (jeśli jest w innym formacie, na przykład BGR)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # Liczba pikseli
        mpx = image_rgb.shape[0] * image_rgb.shape[1]
        # Splaszczenie obrazu do jednego wymiaru
        flattened_image = image_rgb.reshape(-1, 3)
        # Znajdź unikalne kolory i ich częstość
        unique_colors, counts = np.unique(flattened_image, axis=0, return_counts=True)
        # Posortuj kolory według częstości w odwrotnej kolejności
        sorted_indices = np.argsort(-counts)
        sorted_colors = unique_colors[sorted_indices]
        sorted_counts = counts[sorted_indices]
        # Wyświetl najczęściej występujące kolory i ich częstość
        most_popular_colors = sorted_colors[:10]

        # Przygotowanie danych do przesłania do pliku HTML
        most_popular_color_perc = []
        for count in sorted_counts[:10]:
            most_popular_color_perc.append(round(count / mpx * 100, 2))
        colors = zip(most_popular_colors, most_popular_color_perc)
        return render_template("index.html", file=file.filename, colors=colors)


if __name__ == "__main__":
    # Utworzenie folderu, w którym będzie przechowywane zdjęcie
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, port=5007)
