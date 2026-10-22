#!/usr/bin/env python3
"""Read-only asset audit; writes only evidence/verification.json and manifest.json."""
from pathlib import Path
import hashlib,json,math,platform,subprocess,sys
import numpy as np
import PIL
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'preview'))
from reference_render import Renderer,projection,timeline_sample

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    a=ROOT/'assets/processed';records=[]
    for p in sorted(a.rglob('*.png')):
        with Image.open(p) as im:im.verify()
        im=Image.open(p);arr=np.asarray(im)
        expected=(240,240) if p.name.startswith('shutter_') else (480,480)
        assert im.mode=='RGBA' and im.size==expected,(p,im.mode,im.size)
        transparent=arr[...,3]==0
        assert not np.any(arr[transparent,:3]),'Transparent RGB must be zero'
        records.append({'path':str(p.relative_to(ROOT)),'dimensions':list(im.size),'format':'RGBA8 straight alpha',
            'bytes':p.stat().st_size,'sha256':sha(p),'alpha_min':int(arr[...,3].min()),'alpha_max':int(arr[...,3].max()),
            'origin':[120,125] if p.name.startswith('shutter_') else [0,0],
            'space':'screen' if p.name=='frame.png' else 'texture'})
    eye=np.asarray(Image.open(a/'eye_surface.png'))
    assert np.all(eye[...,3]==255)
    original=np.asarray(Image.open(ROOT/'source/registered_states/concept-open-480.png'))
    y,x=np.mgrid[:480,:480];rad=np.hypot(x-240,y-245)
    protected=rad<=184
    assert np.array_equal(eye[protected],original[protected])
    renderer=Renderer()
    composed=[]
    for i in range(9):
        im=Image.fromarray(eye.copy());im.alpha_composite(Image.open(a/f'shutter/shutter_{i:02}.png'),(120,125));composed.append(np.asarray(im))
    assert np.array_equal(composed[0],eye),'Open state must preserve base pixels'
    assert all(np.array_equal(im[rad>111],eye[rad>111]) for im in composed),'Outside shutter changed'
    rig=json.loads((ROOT/'source/shutter/shutter-rig.json').read_text())
    holes=[f['hole_area_model_px2'] for f in rig['frames']]
    assert all(b<a for a,b in zip(holes,holes[1:])) and holes[-1]==0
    frame=np.asarray(Image.open(a/'frame.png'))
    visible=frame[...,3]<255
    invalid_samples=0
    for gx in np.linspace(-.78,.78,17):
        for gy in np.linspace(-.58,.58,17):
            u,v=projection(gx,gy)
            invalid_samples+=int(np.sum(visible&((u<0)|(v<0)|(u>=479)|(v>=479))))
    assert invalid_samples==0,'Visible bilinear footprint leaves texture'
    timeline=json.loads((ROOT/'preview/timeline.json').read_text())
    checks={str(t):timeline_sample(timeline,t) for t in (0,1000,16000,17175,18600,20400,21800,23500,28000)}
    assert checks['16000']['candidate'] and not checks['16000']['confirmed'] and checks['16000']['shutter']==1
    assert checks['17175']['state']=='waking' and checks['17175']['shutter']==.5
    assert not checks['18600']['active'] and checks['20400']['active']
    assert not checks['21800']['valid'] and checks['21800']['gaze_x']==.55
    assert checks['23500']['gaze_x']==0
    videos=[]
    for p in sorted((ROOT/'evidence').glob('*.mp4')):
        j=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries',
            'stream=width,height,nb_frames,r_frame_rate:format=duration,size','-of','json',str(p)]))
        videos.append({'path':str(p.relative_to(ROOT)),**j})
    png_count=0
    for p in ROOT.rglob('*.png'):
        with Image.open(p) as im:im.verify()
        png_count+=1
    manifest={'schema':'mechanical-c-art-assets-v1','not_a_C_API':True,'canvas':[480,480],
        'center':[240,245],'sphere_radius':233,'gaze_limits':{'x':[-.78,.78],'y':[-.58,.58]},
        'pure_axis_center_excursion':[120,80],'shutter_roi':[120,125,240,240],
        'shutter_selection':'floor(clamp(closure,0,1)*8+0.5)',
        'composition_order':['eye_surface + selected shutter in texture coordinates','sphere projection','fixed frame in screen coordinates'],
        'assets':records,'measured_png_total_bytes':sum(r['bytes'] for r in records),
        'estimated_all_RGBA_resident_bytes':480*480*4*2+240*240*4*9,
        'estimated_single_shutter_resident_bytes':480*480*4*2+240*240*4,
        'estimated_extra_RGBA_work_buffer_bytes':480*480*4,
        'estimate_excludes':'decoder/temp allocator, screen buffers, alignment, DMA and GSP internal caches; no device measurement'}
    (ROOT/'assets/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    report={'validation_date':'2026-10-22','asset_dimensions_alpha':'passed','processed_asset_count':len(records),
        'all_packaged_PNG_CRCs_verified':png_count,'protected_C_concept_pixels':int(protected.sum()),'protected_changed_pixels':0,
        'open_composite_identical_to_eye_surface':True,'outside_radius_111_unchanged_across_shutter_frames':True,
        'shutter_model_hole_areas':holes,'visible_bilinear_footprints_outside_texture_17x17_gazes':invalid_samples,
        'timeline_checks':checks,'video_probes':videos,
        'editable_sources':json.loads((ROOT/'source/editable-source-checks.json').read_text()),
        'shutter_rebuild':json.loads((ROOT/'evidence/shutter-rebuild-check.json').read_text()),
        'python_js_comparison':json.loads((ROOT/'evidence/python-js-comparison.json').read_text()),
        'node_render_checks':json.loads((ROOT/'preview/node-render-checks.json').read_text()),
        'environment':{'python':platform.python_version(),'Pillow':PIL.__version__,'numpy':np.__version__,
            'ImageMagick':subprocess.check_output(['convert','-version'],text=True).splitlines()[0],
            'FFmpeg':subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0]},
        'visual_approved':False,'native_C_GSP_verified':False,'hardware_verified':False,'browser_UI_verified':False,
        'known_limits':['Nine discrete visually morphed shutter frames, not physical rigid iris kinematics.',
            'Peripheral texture stretches at extreme gaze under the inherited front-projection sphere mapping.',
            'No real browser executable available; Node execution does not verify layout or browser interaction.',
            'Photoshop/Krita/GIMP GUI roundtrip not verified.','Main project newest AGENTS/README/HANDOFF not provided.']}
    (ROOT/'evidence/verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['processed_asset_count','all_packaged_PNG_CRCs_verified','protected_C_concept_pixels','protected_changed_pixels','open_composite_identical_to_eye_surface','visible_bilinear_footprints_outside_texture_17x17_gazes']},indent=2))
    print('processed PNG bytes',manifest['measured_png_total_bytes'])

if __name__=='__main__':main()
