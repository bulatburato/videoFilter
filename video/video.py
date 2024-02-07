import cv2
import numpy as np
import moviepy.editor as mp
import PySimpleGUI as sg

# Erstellen der grafischen Oberfläche
effects = ["Schwarz-Weiß", "Spiegel", "Negativ", "Sepia", "Kacheln", "Glow", "Film Grain", "Noise", "Vignette", "Distortion"]
resolutions = ["VGA: 640×480", "XGA: 1024×768", "HD-ready: 1280×720", "Full-HD: 1920×1080", "UHD-4k: 3840×2160"]
layout = [
    [sg.Text("Wähle ein Video aus:")],
    [sg.Input(key="video_path"), sg.FileBrowse()],
    [sg.Text("Wähle einen CGI-Effekt aus:")],
    [sg.Listbox(effects, size=(15, 4), key="effect")],
    [sg.Text("Wähle eine Auflösung aus:")],
    [sg.Listbox(resolutions, size=(15, 4), key="resolution")],
    [sg.Text("Eingabe der Geschwindigkeit (langsamer mit - davor und schneller ohne - davor. Werte zwischen -10 und +10):")],
    [sg.Input(key="speed")],
    [sg.Text("Eingabe der Farbwerte für Kachel-Effekt 0.1 0.6 0.2 (falls ausgewählt):")],
    [sg.Input(key="kacheln_values")],
    [sg.Button("Anwenden"), sg.Button("Abbrechen")]
]

window = sg.Window("Video-Editor by Ralf Krümmel", layout)
def glow_effect(img):
           blur = cv2.GaussianBlur(255 - img, (0, 0), 1, 1)
           img_glow = cv2.addWeighted(img, 2.5, blur, -0.5, 2)
           return img_glow

def film_grain_effect(img):
    grain = np.random.normal(0, 3.6, img.shape)
    img_grain = np.clip(img + grain, 0, 255)
    return img_grain.astype(np.uint8)

def noise_effect(img):
    noise = np.random.normal(0, 2.05, img.shape)
    img_noise = np.clip(img + noise, 0, 255)
    return img_noise.astype(np.uint8)

def vignette_effect(img):
    rows, cols = img.shape[:2]
    kernel_x = cv2.getGaussianKernel(cols, 200)
    kernel_y = cv2.getGaussianKernel(rows, 200)
    kernel = kernel_y * kernel_x.T
    mask = kernel / np.linalg.norm(kernel)
    img_vignette = img * mask
    return img_vignette.astype(np.uint8)

def distortion(img):
    height, width = img.shape[:2]
    map_x, map_y = np.indices((height, width), dtype=np.float32)
    map_x = 2*map_x/(width-1) - 1
    map_y = 2*map_y/(height-1) - 1
    r, theta = cv2.cartToPolar(map_x, map_y)
    r[r < 1] = r[r < 1]**1.5
    map_x, map_y = cv2.polarToCart(r, theta)
    map_x = ((map_x + 1)*width - 1)/2
    map_y = ((map_y + 1)*height - 1)/2
    distorted_img = cv2.remap(img, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return distorted_img
# Erstellen einer Funktion, die den ausgewählten Effekt auf das Video anwendet
def apply_effect(video, effect, resolution, speed, kacheln_values=None):
    # Öffnen des Videos mit MoviePy
    clip = mp.VideoFileClip(video)
    # Überprüfen, welcher Effekt ausgewählt wurde
    if effect == "Schwarz-Weiß":
        # Konvertieren des Videos in Graustufen
        clip = clip.fx(mp.vfx.blackwhite)
    elif effect == "Spiegel":
        # Spiegeln des Videos horizontal
        clip = clip.fx(mp.vfx.mirror_x)
    elif effect == "Negativ":
        # Invertieren der Farben des Videos
        clip = clip.fx(mp.vfx.invert_colors)
    elif effect == "Sepia":
        # Anwenden des Sepia-Effekts auf das Video
        clip = clip.fl_image(sepia)
    elif effect == "Kacheln":
        # Anwenden des kacheln-Effekts auf das Video
        clip = clip.fl_image(lambda image: kacheln(image, kacheln_values))
    elif effect == "Glow":
    # Anwenden des Glow-Effekts auf das Video
        clip = clip.fl_image(lambda image: glow_effect(image))
    elif effect == "Film Grain":
    # Anwenden des Film Grain-Effekts auf das Video
        clip = clip.fl_image(lambda image: film_grain_effect(image))
    elif effect == "Noise":
    # Anwenden des Noise-Effekts auf das Video
        clip = clip.fl_image(lambda image: noise_effect(image))
    elif effect == "Vignette":
    # Anwenden des Vignette-Effekts auf das Video
        clip = clip.fl_image(lambda image: vignette_effect(image))
    elif effect == "Distortion":
    # Anwenden des Distortion-Effekts auf das Video
        clip = clip.fl_image(lambda image: distortion(image))
    # Hier können Sie weitere Effekte hinzufügen
    # elif effect == "Lens Flare":
        # Fügen Sie hier den Code für den Lens Flare-Effekt ein
    # elif effect == "Bloom":
        # Fügen Sie hier den Code für den Bloom-Effekt ein
    # Ändern der Geschwindigkeit des Videos
    if speed:
        speed = float(speed)
        if speed < 0:
            clip = clip.fx(mp.vfx.speedx, 1 - abs(speed)/10)
        else:
            clip = clip.fx(mp.vfx.speedx, 1 + speed/10)
    # Ändern der Auflösung des Videos
    resolution = resolution.split(": ")[1].split("×")
    clip = clip.resize(height=int(resolution[1]), width=int(resolution[0]))
    # Rückgabe des bearbeiteten Videos
    return clip

# Erstellen einer Funktion für den Sepia-Effekt
def sepia(image):
    sepia_image = np.dot(image[...,:3], [[0.769, 0.189, 0.0],
                                         [0.686, 0.189, 0.0],
                                         [0.272, 0.543, 0.131]])
    sepia_image = np.clip(sepia_image, 0, 255).astype(np.uint8)
    return sepia_image

# Erstellen einer Funktion für den kacheln-Effekt
def kacheln(image, values):
    kacheln_values = np.array(values.split(' '), dtype=float)
    kacheln_image = np.dot(image[...,:3], kacheln_values)
    kacheln_image = np.clip(kacheln_image, 0, 255 ).astype(np.uint8)
    return kacheln_image

# Erstellen einer Hauptschleife, die auf Benutzereingaben reagiert
while True:
    event, values = window.read()
    # Beenden der Schleife, wenn der Benutzer auf Abbrechen klickt oder das Fenster schließt
    if event in (sg.WIN_CLOSED, "Abbrechen"):
        break
    # Überprüfen, ob der Benutzer auf Anwenden klickt
    if event == "Anwenden":
        # Überprüfen, ob der Benutzer ein Video und einen Effekt ausgewählt hat
        if values["video_path"] and values["effect"] and values["resolution"]:
            # Anwenden des ausgewählten Effekts auf das ausgewählte Video
            new_clip = apply_effect(values["video_path"], values["effect"][0], values["resolution"][0], values["speed"], values["kacheln_values"])
            # Erstellen eines Dateinamens für das neue Video
            new_video = values["video_path"].split(".")[0] + "_" + values["effect"][0] + ".mp4"
            # Speichern des neuen Videos
            new_clip.write_videofile(new_video)
            # Anzeigen einer Nachricht, dass das neue Video erstellt wurde
            sg.popup("Das neue Video wurde gespeichert als " + new_video)
        else:
            # Anzeigen einer Fehlermeldung, wenn der Benutzer kein Video oder keinen Effekt ausgewählt hat
            sg.popup("Bitte wählen Sie ein Video, einen Effekt und eine Auflösung aus.")
