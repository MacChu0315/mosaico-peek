#!/usr/bin/env python3
"""Build editable raster-layer sources from packaged PNG assets (Pillow + ImageMagick)."""
from pathlib import Path
import io, json, subprocess, tempfile, zipfile
from xml.etree import ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'assets/processed'
S=ROOT/'source'
def png(im):
    b=io.BytesIO();im.save(b,format='PNG');return b.getvalue()

def main():
    surface=Image.open(A/'eye_surface.png').convert('RGBA')
    mount=Image.open(A/'frame.png').convert('RGBA')
    frames=[Image.open(A/f'shutter/shutter_{i:02}.png').convert('RGBA') for i in range(9)]
    shutter_full=Image.new('RGBA',(480,480));shutter_full.alpha_composite(frames[0],(120,125))
    merged=Image.alpha_composite(Image.alpha_composite(surface,shutter_full),mount)
    with tempfile.TemporaryDirectory(prefix='mechanical-c-psd-') as td:
        td=Path(td);merged.save(td/'merged.png');shutter_full.save(td/'shutter-full.png')
        cmd=['convert','(',str(td/'merged.png'),'-set','label','Merged preview',')',
             '(',str(A/'frame.png'),'-set','label','Fixed mount',')',
             '(',str(td/'shutter-full.png'),'-set','label','Shutter 00 - open',')',
             '(',str(A/'eye_surface.png'),'-set','label','Moving eye surface',')',
             '-depth','8','-compress','RLE',str(S/'mechanical_c.psd')]
        subprocess.run(cmd,check=True)
    image=ET.Element('image',{'version':'0.0.3','w':'480','h':'480','name':'Mechanical C - optical shutter'})
    stack=ET.SubElement(image,'stack')
    ET.SubElement(stack,'layer',{'name':'Fixed mount','src':'data/frame.png','x':'0','y':'0',
        'opacity':'1.0','visibility':'visible','composite-op':'svg:src-over'})
    for i in range(8,-1,-1):
        ET.SubElement(stack,'layer',{'name':f'Shutter {i:02} - closure {i/8:.3f}',
            'src':f'data/shutter_{i:02}.png','x':'120','y':'125','opacity':'1.0',
            'visibility':'visible' if i==0 else 'hidden','composite-op':'svg:src-over'})
    ET.SubElement(stack,'layer',{'name':'Moving eye surface','src':'data/eye_surface.png','x':'0','y':'0',
        'opacity':'1.0','visibility':'visible','composite-op':'svg:src-over'})
    with zipfile.ZipFile(S/'mechanical_c.ora','w') as z:
        z.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED)
        z.writestr('stack.xml',ET.tostring(image,encoding='utf-8',xml_declaration=True),compress_type=zipfile.ZIP_DEFLATED)
        z.writestr('mergedimage.png',png(merged),compress_type=zipfile.ZIP_DEFLATED)
        thumb=merged.copy();thumb.thumbnail((256,256));z.writestr('Thumbnails/thumbnail.png',png(thumb),compress_type=zipfile.ZIP_DEFLATED)
        for path in [A/'eye_surface.png',A/'frame.png',*[A/f'shutter/shutter_{i:02}.png' for i in range(9)]]:
            z.writestr('data/'+path.name,path.read_bytes(),compress_type=zipfile.ZIP_DEFLATED)
    (S/'editable-source-notes.json').write_text(json.dumps({
        'PSD':{'size':[480,480],'editable_layers_top_to_bottom':['Fixed mount','Shutter 00 - open','Moving eye surface'],
               'other_shutter_frames':'See processed PNGs and ORA; Photoshop GUI roundtrip untested'},
        'ORA':{'layers':11,'visible':['Fixed mount','Shutter 00','Moving eye surface'],
               'hidden':['Shutter '+str(i).zfill(2) for i in range(1,9)],'Krita_GIMP_GUI_roundtrip_verified':False},
        'SVG':'shutter/shutter-rig.svg: six clipped raster blade regions in contracted pose, not vector paint or a rigid mechanical CAD rig'
    },ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'PSD_bytes':(S/'mechanical_c.psd').stat().st_size,'ORA_bytes':(S/'mechanical_c.ora').stat().st_size}))

if __name__=='__main__':main()
