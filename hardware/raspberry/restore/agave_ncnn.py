"""Local-only NCNN runner for the exported, single-class agave detector."""
from pathlib import Path
import cv2
import numpy as np
import ncnn
import yaml


class AgaveNCNN:
    def __init__(self, directory, threads=2):
        directory=Path(directory)
        metadata=yaml.safe_load((directory/'metadata.yaml').read_text())
        self.names=metadata['names']
        if isinstance(self.names,list): self.names=dict(enumerate(self.names))
        self.names={int(k):v for k,v in self.names.items()}
        if len(self.names)!=1:
            raise ValueError('This runner requires a single-class agave model')
        self.height,self.width=metadata['imgsz']
        self.net=ncnn.Net()
        self.net.opt.num_threads=threads
        self.net.opt.use_vulkan_compute=False
        if self.net.load_param(str(directory/'model.ncnn.param'))!=0:
            raise RuntimeError('Cannot load NCNN parameters')
        if self.net.load_model(str(directory/'model.ncnn.bin'))!=0:
            raise RuntimeError('Cannot load NCNN weights')

    def predict(self, image, conf=.2, iou=.4):
        h,w=image.shape[:2]
        ratio=min(self.width/w,self.height/h)
        nw,nh=round(w*ratio),round(h*ratio)
        left=round((self.width-nw)/2-.1); top=round((self.height-nh)/2-.1)
        resized=cv2.resize(image,(nw,nh),interpolation=cv2.INTER_LINEAR)
        padded=cv2.copyMakeBorder(resized,top,self.height-nh-top,left,self.width-nw-left,
                                 cv2.BORDER_CONSTANT,value=(114,114,114))
        mat=ncnn.Mat.from_pixels(padded,ncnn.Mat.PixelType.PIXEL_BGR2RGB,self.width,self.height)
        mat.substract_mean_normalize([], [1/255.0]*3)
        with self.net.create_extractor() as ex:
            ex.input(self.net.input_names()[0],mat)
            rc,output=ex.extract(self.net.output_names()[0])
            if rc!=0: raise RuntimeError('NCNN inference failed')
            pred=np.array(output).T.copy()
        if pred.ndim!=2 or pred.shape[1]!=5:
            raise ValueError(f'Unexpected exported output {pred.shape}')
        pred=pred[pred[:,4]>conf]
        if not len(pred): return []
        xywh=pred[:,:4].copy()
        xywh[:,:2]-=xywh[:,2:]/2
        keep=cv2.dnn.NMSBoxes(xywh.tolist(),pred[:,4].tolist(),conf,iou)
        parsed=[]
        for idx in np.asarray(keep).reshape(-1)[:300]:
            x,y,bw,bh=xywh[idx]
            box=[max(0,min(w,(float(x)-left)/ratio)),max(0,min(h,(float(y)-top)/ratio)),
                 max(0,min(w,(float(x+bw)-left)/ratio)),max(0,min(h,(float(y+bh)-top)/ratio))]
            parsed.append((box,0,float(pred[idx,4])))
        return parsed
