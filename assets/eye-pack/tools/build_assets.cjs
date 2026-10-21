#!/usr/bin/env node
'use strict';
/**
 * Deterministic bitmap export for the handoff. No drawing of a new character.
 * Approved original pixels are resized once, then separated using documented
 * masks. AI-generated closed-eye references provide only the lid material.
 * Requires @napi-rs/canvas for BUILD only. No runtime dependencies in preview.
 */
const fs=require('fs'), path=require('path'), crypto=require('crypto');
const runtime=process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
let Canvas;
try { Canvas=require('@napi-rs/canvas'); }
catch(e) { if(!runtime) throw e; Canvas=require(runtime+'/@napi-rs/canvas'); }
const {createCanvas,loadImage,Path2D}=Canvas;
const fontFile=process.env.EYE_HANDOFF_FONT||'/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';
const fontName=fs.existsSync(fontFile)&&Canvas.GlobalFonts.registerFromPath(fontFile,'Handoff Sans')?'Handoff Sans':'sans-serif';
const ROOT=path.resolve(__dirname,'..');
const size=480;
const configs=[
 {id:'night_owl',name:'夜枭眼',maxGazeX:18,maxGazeY:12,seamY:262,seamCurve:7,
  palette:{surround:'#2b1d15',iris:'#d87919',pupil:'#030303'},
  aperture:'M 20 247 C 44 205 94 168 157 147 C 242 128 348 151 432 207 C 444 215 451 223 454 230 C 435 280 396 319 341 341 C 254 375 151 353 86 316 C 51 294 28 271 20 247 Z'},
 {id:'deep_sea',name:'深海眼',maxGazeX:20,maxGazeY:12,seamY:264,seamCurve:3,
  palette:{surround:'#111e37',iris:'#318c9e',pupil:'#01080c'},
  aperture:'M 17 255 C 61 201 124 168 191 155 C 289 143 382 177 465 244 C 430 309 373 343 310 355 C 206 379 94 341 39 291 C 27 279 20 267 17 255 Z'},
 {id:'mechanical',name:'机械眼',maxGazeX:10,maxGazeY:8,seamY:247,seamCurve:5,
  palette:{surround:'#242324',iris:'#b8791c',pupil:'#090908'},
  aperture:'M 19 236 C 57 184 113 151 181 135 C 279 113 378 141 457 215 C 466 225 469 233 467 241 C 438 291 376 337 313 354 C 214 378 112 343 53 289 C 36 272 25 254 19 236 Z'}
];
function rgba(c){return c.getContext('2d').getImageData(0,0,c.width,c.height);}
function put(w,h,data){const c=createCanvas(w,h),x=c.getContext('2d');const d=x.createImageData(w,h);d.data.set(data);x.putImageData(d,0,0);return c;}
function write(c,p){fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,c.toBuffer('image/png'));}
function hashFile(p){return crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');}
function crop(c,b){const o=createCanvas(b.w,b.h);o.getContext('2d').drawImage(c,-b.x,-b.y);return o;}
function clamp(v){return Math.max(0,Math.min(1,v));}
function dataURI(p){return 'data:image/png;base64,'+fs.readFileSync(p).toString('base64');}
function entry(p,usage,origin=[0,0]){
 const file=path.relative(ROOT,p).split(path.sep).join('/');
 return {file,usage,origin,bytes:fs.statSync(p).size,sha256:hashFile(p)};
}
(async()=>{
 const manifest={format_version:1,package_version:'1.0.0',built_at:'2026-10-21',
  screen:{width:size,height:size,origin:'top-left',x_positive:'right',y_positive:'down'},
  status:'DESIGN_AND_CANVAS_REFERENCE_ONLY_NOT_C_GSP_VALIDATED',
  alpha:'straight/unassociated PNG RGBA; converter must verify native premultiplied-alpha expectations',
  compositing:['opaque near-black fill','translated eye.png','lid_00..08.png in place','stationary frame.png'],
  source_of_truth:'The main project AGENTS.md, README and docs/HANDOFF.md were not available.',
  themes:[],build_checks:[]};
 const bundle={screen:[480,480],status:manifest.status,themes:{}};
 const contact=createCanvas(1440,520),cx=contact.getContext('2d');
 cx.fillStyle='#ecebe8';cx.fillRect(0,0,1440,520);
 for(const [themeIndex,cfg] of configs.entries()){
  const out=path.join(ROOT,'assets/processed',cfg.id);fs.mkdirSync(out,{recursive:true});
  const originalFile=path.join(ROOT,'assets/originals',cfg.id+'.png');
  const closedFile=path.join(ROOT,'assets/design-reference',cfg.id+'_closed_generated.png');
  const original=await loadImage(originalFile),closed=await loadImage(closedFile);
  const neutral=createCanvas(size,size);neutral.getContext('2d').drawImage(original,0,0,size,size);
  const closedC=createCanvas(size,size);closedC.getContext('2d').drawImage(closed,0,0,size,size);
  const src=rgba(neutral).data,cl=rgba(closedC).data;
  const mask=createCanvas(size,size),mx=mask.getContext('2d'),p=new Path2D(cfg.aperture);
  mx.fillStyle='#fff';mx.fill(p);
  const a=rgba(mask).data;
  // Guard covers the maximum diagonal translation, not only antialiasing.
  // Extend source edge pixels outside the screen so the eye stays opaque at
  // either extreme. The stationary frame still preserves the exact original.
  const guard=Math.ceil(Math.hypot(cfg.maxGazeX,cfg.maxGazeY))+3;
  const pad=guard+4,extSize=size+2*pad;
  const expanded=createCanvas(extSize,extSize),ex=expanded.getContext('2d');
  ex.translate(pad,pad);
  ex.fillStyle='#fff';ex.strokeStyle='#fff';ex.lineWidth=2*guard;ex.lineJoin='round';ex.fill(p);ex.stroke(p);
  const b=rgba(expanded).data;
  let minX=480,minY=480,maxX=0,maxY=0;
  const frame=new Uint8ClampedArray(src),eye=new Uint8ClampedArray(extSize*extSize*4);
  const top=new Array(480).fill(480),bottom=new Array(480).fill(-1);
  for(let y=0;y<size;y++)for(let x=0;x<size;x++){
   const i=(y*size+x)*4;
   frame[i+3]=255-a[i+3];
   if(a[i+3]>0){top[x]=Math.min(top[x],y);bottom[x]=Math.max(bottom[x],y);}
  }
  for(let ey=0;ey<extSize;ey++)for(let ex=0;ex<extSize;ex++){
   const x=ex-pad,y=ey-pad,i=(ey*extSize+ex)*4;
   const si=(Math.max(0,Math.min(479,y))*480+Math.max(0,Math.min(479,x)))*4;
   eye[i]=src[si];eye[i+1]=src[si+1];eye[i+2]=src[si+2];eye[i+3]=b[i+3];
   if(b[i+3]){minX=Math.min(minX,x);minY=Math.min(minY,y);maxX=Math.max(maxX,x);maxY=Math.max(maxY,y);}
  }
  const bbox={x:minX-2,y:minY-2,w:maxX-minX+5,h:maxY-minY+5};
  const frameC=put(size,size,frame),eyeC=crop(put(extSize,extSize,eye),{...bbox,x:bbox.x+pad,y:bbox.y+pad});
  write(frameC,path.join(out,'frame.png'));
  write(eyeC,path.join(out,'eye.png'));
  write(neutral,path.join(out,'neutral.png'));
  write(mask,path.join(out,'aperture_mask.png'));
  const levels=[];
  for(let level=0;level<=8;level++){
   const q=level/8, pixels=new Uint8ClampedArray(cl);
   for(let y=0;y<size;y++)for(let x=0;x<size;x++){
    const i=(y*size+x)*4;
    if(level===0||a[i+3]===0){pixels[i+3]=0;continue;}
    if(level===8){pixels[i+3]=a[i+3];continue;}
    const seam=cfg.seamY+cfg.seamCurve*(1-Math.pow((x-240)/225,2));
    const upper=top[x]+q*(seam-top[x]);
    const lower=bottom[x]-q*(bottom[x]-seam);
    const cover=Math.max(clamp(upper-y+0.5),clamp(y-lower+0.5));
    pixels[i+3]=Math.round(a[i+3]*cover);
   }
   const file=path.join(out,'lid_'+String(level).padStart(2,'0')+'.png');
   write(crop(put(size,size,pixels),bbox),file);
   levels.push({closure:q,...entry(file,'precomposed lid cover; zero=fully open, one=fully closed',[bbox.x,bbox.y])});
  }
  // Verify that the layered neutral reproduces the chosen source after one resize.
  const rec=createCanvas(size,size),rx=rec.getContext('2d');
  rx.fillStyle='#07090c';rx.fillRect(0,0,size,size);
  rx.drawImage(eyeC,bbox.x,bbox.y);rx.drawImage(frameC,0,0);
  const got=rgba(rec).data;let maxDiff=0,sum=0,different=0;
  for(let i=0;i<src.length;i+=4){let changed=false;for(let c=0;c<3;c++){const d=Math.abs(src[i+c]-got[i+c]);maxDiff=Math.max(maxDiff,d);sum+=d;if(d>1)changed=true;}if(changed)different++;}
  const check={theme:cfg.id,neutral_max_channel_delta:maxDiff,neutral_mean_abs_channel_delta:sum/(480*480*3),pixels_with_delta_gt_1:different,passed:maxDiff<=3};
  const coverage=[];
  for(const gx of [-1,0,1])for(const gy of [-1,0,1]){
   const cc=createCanvas(size,size),xx=cc.getContext('2d');
   xx.drawImage(eyeC,bbox.x+gx*cfg.maxGazeX,bbox.y+gy*cfg.maxGazeY);xx.drawImage(frameC,0,0);
   const pixels=rgba(cc).data;let uncovered=0,minAlpha=255;
   for(let k=3;k<pixels.length;k+=4){minAlpha=Math.min(minAlpha,pixels[k]);if(pixels[k]<254)uncovered++;}
   coverage.push({gaze:[gx,gy],pixels_alpha_below_254:uncovered,min_alpha:minAlpha});
  }
  check.translation_coverage=coverage;
  check.passed=check.passed&&coverage.every(v=>v.pixels_alpha_below_254===0);
  manifest.build_checks.push(check);
  const rgbaFrameBytes=480*480*4,rgbaEyeBytes=bbox.w*bbox.h*4;
  const files=[
   {...entry(originalFile,'AI-generated approved original; preserved bytes'),width:original.width,height:original.height,kind:'raw-original'},
   {...entry(closedFile,'AI edited closed-eye material reference; not an actual runtime screenshot'),width:closed.width,height:closed.height,kind:'design-reference'},
   {...entry(path.join(out,'neutral.png'),'480x480 neutral reference; not needed at runtime'),width:480,height:480,kind:'processed-reference'},
   {...entry(path.join(out,'frame.png'),'stationary foreground; eye hole has alpha'),width:480,height:480,kind:'processed-runtime'},
   {...entry(path.join(out,'eye.png'),'movable original eye pixels; expanded guard and source-edge extrusion',[bbox.x,bbox.y]),width:bbox.w,height:bbox.h,kind:'processed-runtime'},
   {...entry(path.join(out,'aperture_mask.png'),'build/check mask; not required at runtime'),width:480,height:480,kind:'processed-build'}
  ];
  const theme={id:cfg.id,name:cfg.name,coordinate_space:[480,480],eye_origin:[bbox.x,bbox.y],lid_origin:[bbox.x,bbox.y],layer_bbox:bbox,
   eye_center:[240,cfg.id==='mechanical'?245:250],max_gaze_translation_px:[cfg.maxGazeX,cfg.maxGazeY],
   eye_path:cfg.aperture,seam_y:cfg.seamY,seam_curve:cfg.seamCurve,guard_overlap_px:guard,edge_extension:'clamped source edge pixels outside 480x480; only eye guard, never the foreground',palette:cfg.palette,
   runtime_estimates:{rgba8888_frame_bytes:rgbaFrameBytes,rgba8888_eye_bytes:rgbaEyeBytes,rgba8888_one_lid_bytes:rgbaEyeBytes,
    minimal_resident_texture_bytes:rgbaFrameBytes+2*rgbaEyeBytes,blended_resident_texture_bytes:rgbaFrameBytes+3*rgbaEyeBytes,
    all_nine_lid_resident_texture_bytes:rgbaFrameBytes+10*rgbaEyeBytes,
    rgba8888_framebuffer_bytes:480*480*4,rgb565_framebuffer_bytes:480*480*2,note:'calculated tightly packed pixel memory, not measured; excludes allocator, decoder, conversion, alignment, staging and queues'},
   files,lid_frames:levels};
  manifest.themes.push(theme);
  bundle.themes[cfg.id]={name:cfg.name,eye:dataURI(path.join(out,'eye.png')),frame:dataURI(path.join(out,'frame.png')),
   lids:levels.map(l=>dataURI(path.join(ROOT,l.file))),eyeOrigin:[bbox.x,bbox.y],lidOrigin:[bbox.x,bbox.y],
   maxGazeX:cfg.maxGazeX,maxGazeY:cfg.maxGazeY};
  cx.drawImage(rec,themeIndex*480,0);cx.fillStyle='#202020';cx.font='18px "'+fontName+'"';cx.fillText(cfg.id,themeIndex*480+12,510);
  console.log(JSON.stringify({theme:cfg.id,bbox,check,resident_bytes:theme.runtime_estimates.blended_resident_texture_bytes}));
 }
 fs.writeFileSync(path.join(ROOT,'assets/manifest.json'),JSON.stringify(manifest,null,2)+'\n');
 fs.writeFileSync(path.join(ROOT,'preview/assets-data.js'),'/* Generated local-only bitmap bundle. Sources and hashes: assets/manifest.json. */\nwindow.EYE_ASSETS = '+JSON.stringify(bundle)+';\n');
 write(contact,path.join(ROOT,'evidence/neutral-comparison.png'));
 if(manifest.build_checks.some(c=>!c.passed))process.exitCode=1;
})();

