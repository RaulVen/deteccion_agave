"""Scale the camera texture on the GPU instead of resizing Full HD frames on CPU."""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
os.environ.setdefault('SDL_VIDEODRIVER','wayland')
import cv2
import pygame
from pygame._sdl2 import Window, Renderer, Texture


class AgaveScreen:
    def __init__(self,title,width,height,fullscreen):
        pygame.display.init()
        self.window=Window(title,size=(width,height),fullscreen_desktop=fullscreen)
        self.renderer=Renderer(self.window,accelerated=1,vsync=False)
        self.texture=None
        self.shape=None

    def show(self,frame):
        h,w=frame.shape[:2]
        rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        surface=pygame.image.frombuffer(rgb,(w,h),'RGB')
        if self.shape!=(w,h):
            self.texture=Texture.from_surface(self.renderer,surface)
            self.shape=(w,h)
        else:
            self.texture.update(surface)
        sw,sh=self.window.size
        scale=min(sw/w,sh/h)
        ow,oh=round(w*scale),round(h*scale)
        left,top=(sw-ow)//2,(sh-oh)//2
        self.renderer.draw_color=(0,0,0,255)
        self.renderer.clear()
        self.texture.draw(dstrect=(left,top,ow,oh))
        self.renderer.present()
        return {'left':left,'top':top,'width':ow,'height':oh}

    def poll(self,callback):
        key=-1
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                key=27
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE: key=27
                elif event.unicode: key=ord(event.unicode[0])
            elif event.type in (pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP):
                kind=None
                if event.button==1:
                    kind=cv2.EVENT_LBUTTONDOWN if event.type==pygame.MOUSEBUTTONDOWN else cv2.EVENT_LBUTTONUP
                elif event.button==3 and event.type==pygame.MOUSEBUTTONDOWN:
                    kind=cv2.EVENT_RBUTTONDOWN
                if kind is not None: callback(kind,*event.pos,0,None)
            elif event.type==pygame.MOUSEMOTION:
                callback(cv2.EVENT_MOUSEMOVE,*event.pos,0,None)
            elif event.type==pygame.MOUSEWHEEL:
                callback(cv2.EVENT_MOUSEWHEEL,*pygame.mouse.get_pos(),1 if event.y>0 else -1,None)
        return key

    def close(self):
        self.texture=None
        self.renderer=None
        self.window.destroy()
        pygame.display.quit()
