import os
os.environ['YOLO_OFFLINE']='true'
os.environ['YOLO_AUTOINSTALL']='false'
os.environ['OMP_NUM_THREADS']='3'
os.environ['OPENBLAS_NUM_THREADS']='1'
import json,time,statistics
from pathlib import Path
import cv2
from ultralytics import YOLO
cv2.setNumThreads(1)
root=Path('/home/bioiot/agave_benchmark_20260921')
summary={}
for name,weights in [('pytorch',root/'best.pt'),('ncnn',root/'best_ncnn_model')]:
    model=YOLO(str(weights),task='detect')
    records=[]
    paths=sorted((root/'images').glob('*.jpg'))
    for i,path in enumerate([paths[0]]+paths):
        im=cv2.imread(str(path)); im=cv2.resize(im,(640,360))
        t=time.perf_counter()
        r=model.predict(im,imgsz=320,conf=.2,iou=.4,device='cpu',verbose=False)[0]
        seconds=time.perf_counter()-t
        if i:
            records.append({'image':path.name,'seconds':seconds,'boxes':r.boxes.data.tolist()})
        print(name,path.name,round(seconds,3),len(r.boxes),flush=True)
    summary[name]={'mean_seconds':statistics.mean(x['seconds'] for x in records),'records':records}
    del model
(root/'backend_comparison.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({k:v['mean_seconds'] for k,v in summary.items()}),flush=True)
