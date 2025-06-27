import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def get_model_path():
    """Model dosyası için güvenli path döndür"""
    model_file = "yolov12.pt"
    
    # Önce executable yanında ara
    if getattr(sys, 'frozen', False):
        # PyInstaller ile build edilmiş
        app_dir = os.path.dirname(sys.executable)
        model_path = os.path.join(app_dir, "models", model_file)
        if os.path.exists(model_path):
            return model_path
    
    # Geliştirme ortamında veya resource_path ile
    paths_to_try = [
        resource_path(os.path.join("models", model_file)),
        os.path.join("models", model_file),
        model_file
    ]
    
    for path in paths_to_try:
        if os.path.exists(path):
            return path
    
    raise FileNotFoundError(f"Model dosyası bulunamadı: {model_file}")

def get_alarm_path():
    """Alarm dosyası için güvenli path döndür"""
    alarm_file = "alarm.wav"
    
    # Önce executable yanında ara
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
        alarm_path = os.path.join(app_dir, "assets", alarm_file)
        if os.path.exists(alarm_path):
            return alarm_path
    
    # Geliştirme ortamında veya resource_path ile
    paths_to_try = [
        resource_path(os.path.join("assets", alarm_file)),
        os.path.join("assets", alarm_file),
        alarm_file
    ]
    
    for path in paths_to_try:
        if os.path.exists(path):
            return path
    
    # Eğer alarm dosyası yoksa None döndür (sessiz mod)
    return None

def get_icon_path():
    """Icon dosyası için güvenli path döndür"""
    icon_file = "icon.png"
    
    # Önce executable yanında ara
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
        icon_path = os.path.join(app_dir, "assets", icon_file)
        if os.path.exists(icon_path):
            return icon_path
    
    # Geliştirme ortamında veya resource_path ile
    paths_to_try = [
        resource_path(os.path.join("assets", icon_file)),
        os.path.join("assets", icon_file),
        icon_file
    ]
    
    for path in paths_to_try:
        if os.path.exists(path):
            return path
    
    # Eğer icon dosyası yoksa None döndür
    return None