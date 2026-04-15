import wx
from PIL import Image, ImageOps, ImageDraw, ImageFilter , ImageEnhance# ImageDraw ve ImageFilter   eklendi

MAX_SIZE = (720, 480)
current_pil_image = None   # Üzerinde çalıştığımız, sürekli değişen CANLI resim
canvas_size = (1920, 1080)
layers = []  # İleride katmanlar için kullanacağız, şimdilik boş kalsın
original_pil_image = None  # Reset atmak için sakladığımız İLK resim
current_brush_color = (255, 0, 0)  # Varsayılan renk: Kırmızı (RGB formatında)
current_brush_size = 5             # Varsayılan fırça kalınlığı
current_eraser_size = 20  # YENİ EKLENDİ: Silginin bağımsız kalınlığı
is_drawing= False
is_eraser_active = False
last_mouse_x = 0
last_mouse_y = 0
draw_mode_active = False
clean_canvas_image = None  # Silgiyle ortaya çıkaracağımız temiz fotoğraf yedeği


#update canvas kaldı bir tek

ID_RESET = wx.NewIdRef()
history = []




class Layers:
    def __init__(self, pil_image, name="Layer"):
        self.original_image = pil_image.convert("RGBA") 
        self.current_image = self.original_image.copy()
        self.name = name

        self.x = 0
        self.y = 0
        self.visible = True
        self.angle = 0
        self.scale = 1.0


    def update_transform(self):
        """Bu fonksiyon sadece bu katmana ait döndürme ve ölçeklemeyi hesaplar."""
        # 1. Ölçekleme (Büyütme/Küçültme)
        w, h = self.original_image.size
        new_w, new_h = int(w * self.scale), int(h * self.scale)
        # Resim çok küçülürse hata vermemesi için güvenlik önlemi:
        if new_w < 1 or new_h < 1: return 
        
        temp_img = self.original_image.resize((new_w, new_h), Image.LANCZOS)
        
        # 2. Döndürme (expand=True, döndürünce resmin köşelerinin kesilmesini önler)
        self.current_image = temp_img.rotate(self.angle, expand=True)




def choose_eraser_size(event):
    global current_eraser_size
    # wxPython'un hazır sayı alma penceresi
    val = wx.GetNumberFromUser("Silgi kalınlığını seçin (1-100):", "Kalınlık:", 
                               "Silgi Boyutu", current_eraser_size, 1, 100, frame)
    if val != -1: # Kullanıcı iptale basmadıysa
        current_eraser_size = val
        print(f"Yeni Silgi Kalınlığı: {current_eraser_size}")

def choose_brush_color(event):
    global current_brush_color
    # wxPython'un hazır renk seçme penceresi
    color_data = wx.ColourData()
    dlg = wx.ColourDialog(frame, color_data)
    
    if dlg.ShowModal() == wx.ID_OK:
        # Seçilen rengi al ve PILLOW'un anlayacağı RGB (Kırmızı, Yeşil, Mavi) formatına çevir
        color = dlg.GetColourData().GetColour()
        current_brush_color = (color.Red(), color.Green(), color.Blue())
        print(f"Yeni Fırça Rengi: {current_brush_color}")
        
    dlg.Destroy()

def choose_brush_size(event):
    global current_brush_size
    # wxPython'un hazır sayı alma penceresi (Başlık, Mesaj, Varsayılan değer, Min, Max)
    val = wx.GetNumberFromUser("Fırça kalınlığını seçin (1-100):", "Kalınlık:", 
                               "Fırça Boyutu", current_brush_size, 1, 100, frame)
    if val != -1: # Kullanıcı Cancel'a basmadıysa
        current_brush_size = val
        print(f"Yeni Fırça Kalınlığı: {current_brush_size}")

# --- ETKİLEŞİMLİ ÇİZİM FONKSİYONLARI ---

def toggle_draw_mode(event=None): # event=None yaptık ki başka yerden de çağırabilelim
    global draw_mode_active, clean_canvas_image, current_pil_image
    draw_mode_active = not draw_mode_active
    
    if draw_mode_active:
        print("Çizim Modu: AÇIK")
        # SİLGİ İÇİN KRİTİK NOKTA: Çizime başlarken resmin temiz halini BİR KERE yedekliyoruz
        if current_pil_image is not None:
            clean_canvas_image = current_pil_image.copy()
        
        image_viewer.SetCursor(wx.Cursor(wx.CURSOR_PENCIL))
    else:
        print("Çizim Modu: KAPALI")
        image_viewer.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

def toggle_eraser_mode(event):
    global is_eraser_active, draw_mode_active
    is_eraser_active = not is_eraser_active
    
    if is_eraser_active:
        # Eğer çizim modu kapalıyken silgiye basıldıysa, çizim modunu da aç
        if not draw_mode_active:
            toggle_draw_mode()
            
        # SİLGİ İMLECİ: Hassas silme işlemi için farenin ucunu Artı (+) işareti yapar
        image_viewer.SetCursor(wx.Cursor(wx.CURSOR_CROSS)) 
        print("Silgi Modu: AKTİF")
        
    else:
        # SİLGİDEN ÇIKILINCA: Fareyi tekrar Kalem imlecine döndürür
        image_viewer.SetCursor(wx.Cursor(wx.CURSOR_PENCIL)) 
        print("Silgi Modu: KAPALI")
        
def on_mouse_down(event):
    global is_drawing, last_mouse_x, last_mouse_y, current_pil_image
    
    # Çizim modu kapalıysa veya resim yoksa hiçbir şey yapma
    if not draw_mode_active or current_pil_image is None: 
        event.Skip()
        return

    is_drawing = True
    save_state() # Çizimi geri alabilmek (Undo) için işlemi kaydet
    
    # Koordinat Ölçeklendirme Matematiği (Ekrandaki x,y -> Gerçek x,y)
    display_img = current_pil_image.copy()
    display_img.thumbnail(MAX_SIZE)
    ratio_x = current_pil_image.width / display_img.width
    ratio_y = current_pil_image.height / display_img.height
    
    last_mouse_x = event.GetX() * ratio_x
    last_mouse_y = event.GetY() * ratio_y

def on_mouse_up(event):
    global is_drawing
    is_drawing = False # Tıklamayı bırakınca çizimi durdur
    event.Skip()

def on_mouse_move(event):
    global is_drawing, last_mouse_x, last_mouse_y, current_pil_image
    
    if is_drawing and draw_mode_active and current_pil_image is not None:
        display_img = current_pil_image.copy()
        display_img.thumbnail(MAX_SIZE)
        ratio_x = current_pil_image.width / display_img.width
        ratio_y = current_pil_image.height / display_img.height
        
        curr_x = event.GetX() * ratio_x
        curr_y = event.GetY() * ratio_y
        
        if not is_eraser_active:
            # 1. NORMAL ÇİZİM (Fırça)
            draw = ImageDraw.Draw(current_pil_image)
            draw.line([(last_mouse_x, last_mouse_y), (curr_x, curr_y)], 
                      fill=current_brush_color, width=current_brush_size, joint="curve")
        else:
            # 2. GERÇEK SİLGİ (Temiz resmi ortaya çıkarma işlemi)
            # A. Siyah bir maske (şablon) oluştur
        
            # 2. GERÇEK SİLGİ (Temiz resmi ortaya çıkarma işlemi)
            mask = Image.new("L", current_pil_image.size, 0)
            mask_draw = ImageDraw.Draw(mask)
            
            # DİKKAT: Artık current_brush_size değil, current_eraser_size kullanıyoruz!
            mask_draw.line([(last_mouse_x, last_mouse_y), (curr_x, curr_y)], 
                           fill=255, width=current_eraser_size, joint="curve")
            
            current_pil_image = Image.composite(clean_canvas_image, current_pil_image, mask)
        
        last_mouse_x, last_mouse_y = curr_x, curr_y
        update_canvas(current_pil_image)
        
    event.Skip()


def save_state():
    """Mevcut resmin bir kopyasını geçmişe (history) kaydeder."""
    global current_pil_image, history
    if current_pil_image is not None:
        # RAM dolmasın diye sadece son 10 işlemi hafızada tutalım
        if len(history) >= 10:
            history.pop(0) # En eski olanı sil
        
        # O anki resmin BİR KOPYASINI listeye ekle
        history.append(current_pil_image.copy())




def apply_brightness_slider(event):
    def brightness_logic(img, val):
        factor = val / 100.0 
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(factor)
    apply_adjustable_filter("Brightness (Parlaklık) Şiddeti", 0, 200, 100, brightness_logic)
        

def on_undo(event):
    global current_pil_image, history
    
    # Eğer geçmiş listesi boşsa (hiçbir işlem yapılmadıysa) hiçbir şey yapma
    if len(history) == 0:
        return
        
    # Listeden en son eklenen resmi al (.pop() hem alır hem de listeden siler)
    current_pil_image = history.pop()
    update_canvas(current_pil_image)
    print("Geri alındı!")        


def update_canvas(pil_img):
    """Verilen PILLOW resmini ekrana basar. Her yerde bunu kullanacağız."""
    display_img = pil_img.copy()
    display_img.thumbnail(MAX_SIZE)
    
    if display_img.mode != 'RGB':
        display_img = display_img.convert('RGB')
        
    width, height = display_img.size
    wx_img = wx.Image(width, height, display_img.tobytes())
    image_viewer.SetBitmap(wx_img.ConvertToBitmap())
    panel.Layout()



def on_exit(event):
    frame.Close()

def on_open(event):
    wildcard_format = "Image Files (*.jpg;*.png;*.bmp)|*.jpg;*.png;*.bmp"
    with wx.FileDialog(frame, "Open file", wildcard=wildcard_format, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as file_dialog:
        if file_dialog.ShowModal() == wx.ID_CANCEL:
            return
        
        global current_pil_image, original_pil_image, current_image_path
        current_image_path = file_dialog.GetPath()
        
        # Resmi hafızaya alıyoruz
        opened_img = Image.open(current_image_path)
        original_pil_image = opened_img.copy() # Yedeği sakla
        current_pil_image = opened_img.copy()  # Üstünde çalışacağımız kopya
        
        update_canvas(current_pil_image) # İşçiyi çağır, ekrana bassın

def on_reset(event):
    global current_pil_image, original_pil_image
    if original_pil_image is None: return
        
    # Canlı resmi orijinal yedeğe geri döndür
    current_pil_image = original_pil_image.copy()
    update_canvas(current_pil_image)
    print("Resim orijinal haline döndürüldü.")

def save_image(event):
    global current_pil_image # Artık doğrudan hafızadaki resmi kaydedeceğiz
    if current_pil_image is None: return
    
    wildcard_format = "PNG files (*.png)|*.png|JPEG files (*.jpg)|*.jpg"
    with wx.FileDialog(frame, "Save file", wildcard=wildcard_format, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as file_dialog:
        if file_dialog.ShowModal() == wx.ID_CANCEL: return
        
        # Geçici dosyalarla uğraşmaya gerek kalmadı! Direkt kaydediyoruz:
        save_path = file_dialog.GetPath()
        current_pil_image.save(save_path)
        print(f"Image saved to {save_path}")

# --- FİLTRELER BÖLÜMÜ ---




def apply_adjustable_filter(title, min_val, max_val, default_val, logic_function):
    """Tüm slider pencerelerini yöneten ortak ana fonksiyon (Motor)"""
    global current_pil_image, history
    if current_pil_image is None: return

    save_state()
    base_image = current_pil_image.copy()
    if base_image.mode != 'RGB': base_image = base_image.convert('RGB')

    # 1. Ortak Pencere Tasarımı
    dlg = wx.Dialog(frame, title=title, size=(300, 150))
    vbox = wx.BoxSizer(wx.VERTICAL)
    slider = wx.Slider(dlg, value=default_val, minValue=min_val, maxValue=max_val, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
    vbox.Add(slider, 1, wx.EXPAND | wx.ALL, 15)
    
    btn_sizer = dlg.CreateButtonSizer(wx.OK | wx.CANCEL)
    vbox.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)
    dlg.SetSizer(vbox)

    # 2. Ortak Scroll (Kaydırma) Olayı
    def on_scroll(e):
        global current_pil_image
        # İŞTE BURASI! Hangi filtre geldiyse o formülü çalıştır ve değeri gönder:
        current_pil_image = logic_function(base_image, slider.GetValue())
        update_canvas(current_pil_image)

    slider.Bind(wx.EVT_SLIDER, on_scroll)
    on_scroll(None) # İlk açılışta efekti uygula

    # 3. Ortak Karar (Tamam mı İptal mi?)
    result = dlg.ShowModal()
    if result == wx.ID_CANCEL:
        current_pil_image = base_image
        update_canvas(current_pil_image)
        history.pop() 
        print(f"{title} iptal edildi.")
    else:
        print(f"{title} uygulandı!")

        dlg.Destroy()   

def apply_grayscale(event):
    def grayscale_logic(img, val):
        alpha = val / 100.0 
        bw_image = ImageOps.grayscale(img)
        return Image.blend(img, bw_image.convert('RGB'), alpha)
    apply_adjustable_filter("Grayscale (Sarımsaklama) Şiddeti", 0, 100, 100, grayscale_logic)


def apply_blur(event):
    def blur_logic(img, val):
        radius = (val / 100.0) * 10 
        return img.filter(ImageFilter.GaussianBlur(radius=radius))
    apply_adjustable_filter("Blur (Bulanıklık) Şiddeti", 0, 100, 0, blur_logic)


   

def apply_sharpen(event):
    global current_pil_image
    if current_pil_image is None: return
    save_state()
    base_image = current_pil_image.copy()
    if base_image.mode != 'RGB': base_image = base_image.convert('RGB')

    dlg = wx.Dialog(frame, title="Sharpen (Efekt Şiddeti)", size=(300, 150))
    vbox = wx.BoxSizer(wx.VERTICAL)
    slider = wx.Slider(dlg, value=100, minValue=0, maxValue=200, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
    vbox.Add(slider, 1, wx.EXPAND | wx.ALL, 15)
    btn_sizer = dlg.CreateButtonSizer(wx.OK | wx.CANCEL)
    vbox.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)
    dlg.SetSizer(vbox)
    def on_scroll(e):
        global current_pil_image
        factor = slider.GetValue() / 100.0 
        enhancer = ImageEnhance.Sharpness(base_image)
        current_pil_image = enhancer.enhance(factor)
        update_canvas(current_pil_image)
    slider.Bind(wx.EVT_SLIDER, on_scroll)
    on_scroll(None) # Pencere açılır açılmaz efekti %100 haliyle göstersin diye bir kere manuel çağırıyoruz
    result = dlg.ShowModal()
    if result == wx.ID_CANCEL:
        current_pil_image = base_image
        update_canvas(current_pil_image)
        history.pop() # İptal ettiği için geçmişteki o gereksiz "save_state" kaydını sil
        print("Sharpen iptal edildi.")
    else:
        print("Sharpen başarıyla uygulandı!")



    
 

def negative_filter(event):
    global current_pil_image
    if current_pil_image is None: return
    save_state()
    if current_pil_image.mode != 'RGB': current_pil_image = current_pil_image.convert('RGB')




    base_image = current_pil_image.copy()
    if base_image.mode != 'RGB': base_image = base_image.convert('RGB')
   
    dlg = wx.Dialog(frame, title="Polarize (Efekt Şiddeti)", size=(300, 150))
    vbox = wx.BoxSizer(wx.VERTICAL)

    # Slider 0 ile 100 arası (%0 efekt - %100 efekt)
    slider = wx.Slider(dlg, value=100, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
    vbox.Add(slider, 1, wx.EXPAND | wx.ALL, 15)

    btn_sizer = dlg.CreateButtonSizer(wx.OK | wx.CANCEL)
    vbox.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)
    dlg.SetSizer(vbox)

    # --- SLIDER KAYDIRILDIKÇA ÇALIŞACAK SİHİRLİ KISIM ---
    def on_scroll(e):
        global current_pil_image
      
        alpha = int((slider.GetValue() / 100.0) * 255)
          
        negatives = ImageOps.invert(base_image) # Negative filtresi için PILLOW'un hazır fonksiyonunu kullanıyoruz, slider'la efekt şiddetini değiştirmek istersek o zaman kendi algoritmamızı yazmamız gerekecek
        current_pil_image = Image.blend(base_image, negatives, slider.GetValue() / 100.0) # Slider'dan gelen değere göre orijinal resim ile negatif resmi harmanlıyoruz
        update_canvas(current_pil_image)
       
    # Slider'ı dinle
    slider.Bind(wx.EVT_SLIDER, on_scroll)
    
    # Pencere açılır açılmaz efekti %100 haliyle göstersin diye bir kere manuel çağırıyoruz
    on_scroll(None)

    # --- KULLANICININ KARARI ---
    result = dlg.ShowModal()

    if result == wx.ID_CANCEL:
        current_pil_image = base_image # İptal derse alt katmana (temiz hale) geri dön
        update_canvas(current_pil_image)
        history.pop() # İşlem iptal olduğu için geçmişteki o gereksiz kaydı sil
        print("Negative iptal edildi.")
    else:
        print("Negative başarıyla uygulandı!")

    dlg.Destroy()


    
def apply_posterize(event):
    def posterize_logic(img, val):
        bits_degeri = 8 - int((val / 100.0) * 7)
        return ImageOps.posterize(img, bits=bits_degeri)
        
    apply_adjustable_filter("Posterize Şiddeti", 0, 100, 100, posterize_logic)



def apply_solarize(event):
    def solarize_logic(img, val):
        alpha = 255 - int((val / 100.0) * 255)
        return ImageOps.solarize(img, threshold=alpha)
        
    apply_adjustable_filter("Solarize Şiddeti", 0, 100, 100, solarize_logic)



def apply_sepia(event):
    
    def sepia_logic(img, val):
        # 1. Fotoğrafçılıkta kullanılan standart Sepia renk matrisi
        sepia_matrix = (0.393, 0.769, 0.189, 0, 
                        0.349, 0.686, 0.168, 0, 
                        0.272, 0.534, 0.131, 0)
        
        # 2. Resmin %100 tam sepia halini (üst katmanı) oluştur
        tam_sepia = img.convert("RGB", sepia_matrix)
        
        # 3. Slider'dan gelen 0-100 arası değeri 0.0-1.0 arasına çevir
        alpha = val / 100.0
        
        # 4. Orijinal resim ile tam sepia resmi slider oranında harmanla
        return Image.blend(img, tam_sepia, alpha)

    # Master motoru çağırıyoruz: 
    # Başlık: Sepia Şiddeti, Min: 0, Max: 100, Başlangıç: 100
    apply_adjustable_filter("Sepia Şiddeti", 0, 100, 100, sepia_logic)


def apply_contrast(event):
    def contrast_logic(img, val):
        factor = val / 100.0 
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(factor)
        
    apply_adjustable_filter("Contrast (Kontrast) Şiddeti", 0, 200, 100, contrast_logic)

def apply_saturation(event):
    def saturation_logic(img, val):
        factor = val / 100.0 
        enhancer = ImageEnhance.Color(img)
        return enhancer.enhance(factor)
        
    apply_adjustable_filter("Saturation (Doygunluk) Şiddeti", 0, 200, 100, saturation_logic)

def on_draw_square(event):
    global current_pil_image
    if current_pil_image is None: return
    save_state()
    draw = ImageDraw.Draw(current_pil_image)
    draw.rectangle([50, 50, 150, 150], outline="red", width=5)
    update_canvas(current_pil_image)


app = wx.App()
wx.InitAllImageHandlers()

frame = wx.Frame(None, title="My Pro Graphic Editor", size=(800, 600))
panel = wx.Panel(frame)
image_viewer = wx.StaticBitmap(panel, bitmap=wx.Bitmap(1, 1))

# --- YENİ MENÜ DÜZENİ ---
menu_bar = wx.MenuBar()

# 1. Dosya Menüsü
file_menu = wx.Menu()

open_item = file_menu.Append(wx.ID_OPEN, "&Open\tCtrl+O")
# Dosya menüsünün (file_menu) içine ekle
undo_item = file_menu.Append(wx.ID_UNDO, "&Undo\tCtrl+Z", "Geri Al")
save_item = file_menu.Append(wx.ID_SAVE, "&Save\tCtrl+S") # Save seçeneği eklendi
exit_item = file_menu.Append(wx.ID_EXIT, "&Exit\tAlt+F4")

# 2. Filtreler Menüsü
filter_menu = wx.Menu()

filter_item = filter_menu.Append(wx.ID_ANY, "&Black & White")
filter_menu.Append(ID_RESET, "&Reset")
sepia_item = filter_menu.Append(wx.ID_ANY, "&Sepia") # Sepia filtresi eklendi
negative_filter_item = filter_menu.Append(wx.ID_ANY, "&Negative") # Negative filtresi eklendi
posterize_item = filter_menu.Append(wx.ID_ANY, "&Posterize") # Posterize filtresi eklendi
solarize_item = filter_menu.Append(wx.ID_ANY, "&Solarize") # Solarize filtresi eklendi



effect_menu = wx.Menu()

blur_item = effect_menu.Append(wx.ID_ANY, "&Blur") # Blur filtresi eklendi
sharpen_item = effect_menu.Append(wx.ID_ANY, "&Sharpen") # Sharpen filtresi eklendi
# effect_menu içine blur ve sharpen'ın yanına ekle:
brightness_item = effect_menu.Append(wx.ID_ANY, "Adjust &Brightness (Slider)")
contrast_item = effect_menu.Append(wx.ID_ANY, "Adjust &Contrast (Slider)")
saturation_item = effect_menu.Append(wx.ID_ANY, "Adjust &Saturation (Slider)") # Saturation filtresi eklendi
effect_menu.Append(ID_RESET, "&Reset")

# 3. Çizim Menüsü
# 3. Çizim Menüsü (Eski draw_square kodunu silebilirsin)
draw_menu = wx.Menu()
draw_toggle_item = draw_menu.Append(wx.ID_ANY, "Toggle Free Draw\tCtrl+D", "Serbest çizim modunu açar/kapatır")
draw_item = draw_menu.Append(wx.ID_ANY, "Draw &Square\tCtrl+Shift+D") # Çizim seçeneği eklendi, Ctrl+D kısayolu verildi
draw_menu.AppendSeparator() # Araya şık bir çizgi çeker
brush_color_item = draw_menu.Append(wx.ID_ANY, "Brush Color (Renk Seç)")
brush_size_item = draw_menu.Append(wx.ID_ANY, "Brush Size (Kalınlık Seç)")
draw_menu.AppendSeparator()
eraser_item = draw_menu.Append(wx.ID_ANY, "Toggle Eraser (Silgi)\tCtrl+E", "Gerçek silgi modunu açar")
eraser_size_item = draw_menu.Append(wx.ID_ANY, "Eraser Size (Silgi Kalınlığı Seç)") # YENİ EKLENDİ
draw_menu.AppendSeparator()

# Menüleri Bar'a ekle
menu_bar.Append(file_menu, "&File")
menu_bar.Append(filter_menu, "&Filters")
menu_bar.Append(effect_menu, "&Effects")
menu_bar.Append(draw_menu, "&Draw")

frame.SetMenuBar(menu_bar)

# --- BAĞLANTILAR ---
frame.Bind(wx.EVT_MENU, on_open, open_item)
frame.Bind(wx.EVT_MENU, save_image, save_item) # Save fonksiyonu tanımlanmadı ama menüye eklendi, ileride eklenebilir
frame.Bind(wx.EVT_MENU, apply_grayscale, filter_item)
frame.Bind(wx.EVT_MENU, on_draw_square, draw_item) # Çizim bağlandı
frame.Bind(wx.EVT_MENU, on_exit, exit_item)
frame.Bind(wx.EVT_MENU, apply_blur, blur_item)
frame.Bind(wx.EVT_MENU, apply_sharpen, sharpen_item)
frame.Bind(wx.EVT_MENU, on_reset, id=ID_RESET)
frame.Bind(wx.EVT_MENU, apply_sepia, sepia_item) # Sepia filtresi bağlandı
frame.Bind(wx.EVT_MENU, negative_filter, negative_filter_item) # Negative filtresi bağlandı
frame.Bind(wx.EVT_MENU, apply_posterize, posterize_item) # Reset seçeneği açma işlemiyle aynı işlevi görecek şekilde bağlandı
frame.Bind(wx.EVT_MENU, apply_solarize, solarize_item) # Reset seçeneği açma işlemiyle aynı işlevi görecek şekilde bağlandı
frame.Bind(wx.EVT_MENU, on_undo, undo_item)
frame.Bind(wx.EVT_MENU, apply_brightness_slider, brightness_item)
frame.Bind(wx.EVT_MENU, apply_contrast, contrast_item)
frame.Bind(wx.EVT_MENU, apply_saturation, saturation_item) # Saturation filtresi bağlandı
frame.Bind(wx.EVT_MENU, toggle_draw_mode, draw_toggle_item)
# Yeni çizim ayarı bağlantıları
frame.Bind(wx.EVT_MENU, choose_brush_color, brush_color_item)
frame.Bind(wx.EVT_MENU, choose_brush_size, brush_size_item)
frame.Bind(wx.EVT_MENU, toggle_eraser_mode, eraser_item)
frame.Bind(wx.EVT_MENU, choose_eraser_size, eraser_size_item) # YENİ EKLENDİ
# Farenin hareketlerini image_viewer'a (resmin gösterildiği alan) bağlama
image_viewer.Bind(wx.EVT_LEFT_DOWN, on_mouse_down)
image_viewer.Bind(wx.EVT_LEFT_UP, on_mouse_up)
image_viewer.Bind(wx.EVT_MOTION, on_mouse_move)


frame.Show()
app.MainLoop()