import numpy as np
import mss
from PIL import Image
# import pyautogui as pg
import pydirectinput as pg
from cnocr import CnOcr
from PySide6.QtCore import QTimer, QEventLoop
from python_imagesearch.imagesearch import imagesearcharea as search_area

ocr = CnOcr()

def wait(ms):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()

def screenshot(zones):
    with mss.mss() as sct:
        # 一次性截取全屏
        full_screenshot = sct.grab(sct.monitors[1])
        full_image = Image.frombytes('RGB', full_screenshot.size, full_screenshot.rgb)

        # 裁剪所需区域并保存到列表
        cropped_images = []
        for zone in zones:
            left = zone['left']
            top = zone['top']
            right = left + zone['width']
            bottom = top + zone['height']
            cropped_image = full_image.crop((left, top, right, bottom))
            cropped_image = np.array(cropped_image)
            cropped_images.append(cropped_image)
        return cropped_images
    
chess_zones = [
        {'left': 482, 'top': 1039, 'width': 129, 'height': 31},
        {'left': 686, 'top': 1039, 'width': 129, 'height': 31},
        {'left': 887, 'top': 1039, 'width': 129, 'height': 31},
        {'left': 1088, 'top': 1039, 'width': 129, 'height': 31},
        {'left': 1290, 'top': 1039, 'width': 129, 'height': 31}
    ]

def onscreen(path, region=None, precision=0.8):
    if region:
        x1, y1, width, height = region
        x2 = x1 + width
        y2 = y1 + height
        return search_area(path, x1, y1, x2, y2, precision)[0] != -1
    else:
        screen_width, screen_height = pg.size()
        return search_area(path, 0, 0, screen_width, screen_height, precision)[0] != -1
    
chess_locations = [(573,987), (781, 987), (979, 987), (1180, 987), (1381, 987)]
check_area = [(483, 1037, 32, 36), (685, 1037, 32, 36), (884, 1037, 32, 36), (1087, 1037, 32, 36), (1289, 1037, 32, 36)]

def roll_chess(d_n, interval, need_chess_dict, window):
    pg.click(960, 540)
    for d in range(d_n):
        if window.roll_status:
            images = screenshot(chess_zones)
            out = ocr.ocr_for_single_lines(images)
            for i, chess in enumerate(out):
                chess = chess['text']
                if chess in need_chess_dict and need_chess_dict[chess][0] < need_chess_dict[chess][1]:
                    n = 0
                    while n < 3:
                        # pg.click(chess_locations[i][0], chess_locations[i][1], duration=0.5)
                        pg.mouseDown(chess_locations[i][0], chess_locations[i][1])
                        # wait(50)
                        pg.mouseUp(chess_locations[i][0], chess_locations[i][1])
                     
                        # wait(100)
                        if onscreen('img/check.png', check_area[i]):
                            need_chess_dict[chess][0] += 1
                            break
                        n += 1
            all_get = True
            for chess in need_chess_dict.values():
                all_get = False if chess[0] < chess[1] else all_get
            if all_get:
                break

            wait(interval/2)
            pg.press('d')
            wait(interval/2)
        else:
            break

ybzone = [{'left': 620, 'top': 931, 'width': 256, 'height': 30}]

def roll_anomalie(d_n, interval, need_anomalie_list, window):
    pg.click(960, 540)
    for d in range(d_n):
        if window.roll_status:
            image = screenshot(ybzone)
            out = ocr.ocr_for_single_lines(image)
            anomalie = out[0]['text'].split('（')[0]
            if anomalie in need_anomalie_list:
                break
            wait(interval/2)
            pg.press('d')
            wait(interval/2)
        else:
            break

