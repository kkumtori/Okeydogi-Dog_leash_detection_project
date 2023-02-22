import torch
from PIL import Image

yolo_model = torch.hub.load('WongKinYiu/yolov7','custom','/home/lab16/pt/0213_yolov7_epochs55.pt')
#yolo_model = torch.hub.load('ultralytics/yolov5', 'custom', path='/home/lab16/pt/0208_best_sgd_yolov5_epoch50_jiye.pt', force_reload=True)
yolo_model.conf=0.6 # thresghold
yolo_model.classes=27
yolo_model.iou=0.6

def crop_image(image_path,image_name,new_image_path,margin=20):
    # 이미지 열기
    img = Image.open(image_path+image_name).convert('RGB')

    # predict 결과
    results = yolo_model(img, size=416)
    pos_lists = results.pandas().xyxy
    pos_df = pos_lists[0]

    for idx, pos in pos_df.iterrows():
        cropped_image = img.crop((max(pos['xmin']-margin, 0), max(pos['ymin']-margin, 0), min(pos['xmax']+margin, img.width), min(pos['ymax']+margin, img.height)))
        cropped_image.save(f'{new_image_path}crop_{image_name}')