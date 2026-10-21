#!/usr/bin/env node
'use strict';
/**
 * Reference evidence exporter. Uses the EXACT model/timeline/renderer shipped
 * in preview/. Offscreen @napi-rs/canvas output; never a C/GSP/device capture.
 * node tools/render_evidence.cjs [--stills-only]
 * Build-only prerequisites: Node, @napi-rs/canvas, ffmpeg, ffprobe.
 */
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto');
const {spawn,spawnSync}=require('child_process');
const {once}=require('events');
let Canvas;
try{Canvas=require('@napi-rs/canvas');}catch(e){
 if(!process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES)throw e;
 Canvas=require(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES+'/@napi-rs/canvas');
}
const {createCanvas,loadImage}=Canvas;
const fontFile=process.env.EYE_HANDOFF_FONT||'/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';
const fontName=fs.existsSync(fontFile)&&Canvas.GlobalFonts.registerFromPath(fontFile,'Handoff Sans')?'Handoff Sans':'sans-serif';
const ROOT=path.resolve(__dirname,'..'),EVIDENCE=path.join(ROOT,'evidence');
const SHA=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT,p))).digest('hex');
const digest=buffer=>crypto.createHash('sha256').update(buffer).digest('hex');
const context={console};context.globalThis=context;vm.createContext(context);
for(const file of ['timeline.js','model.js','renderer.js'])
 vm.runInContext(fs.readFileSync(path.join(ROOT,'preview',file),'utf8'),context,{filename:file});
const Model=context.PreviewModel,Timeline=context.PreviewTimeline,Renderer=context.PreviewRenderer;
const manifest=JSON.parse(fs.readFileSync(path.join(ROOT,'assets/manifest.json')));
const fps=20,duration=48000,W=1440,H=620;
const states=[
 ['IDLE',1800],['NOTICE',6100],['TRACKING',10200],['HOLD',13700],
 ['LEAVE',14800],['sleeping',20000],['waking',22725]
];
const scenes=[
 ['UNCONFIRMED CANDIDATE / stays IDLE',4100,'full'],
 ['FOLLOW LEFT',8500,'full'],['FOLLOW RIGHT',10200,'full'],
 ['FOLLOW DOWN',11300,'full'],['FOLLOW UP',12200,'full'],
 ['UNCONFIRMED CANDIDATE / stays asleep',21000,'full'],
 ['SWITCHED OUT / no character drawn',27150,'full'],
 ['REENTER / current confirmed target',28400,'full'],
 ['INVALID DATA / easing to center',30950,'full'],
 ['INVALID DATA / neutral',31400,'full'],
 ['DATA RESTORED',31900,'full'],
 ['REENTER / current empty state',34200,'full'],
 ['REENTER / already sleeping',38200,'full'],
 ['NaN COORDINATE / safe fallback',42850,'full'],
 ['ENTER WITH TARGET',0,'enter_target'],
 ['ENTER WITHOUT TARGET',0,'enter_empty'],
 ['ENTER WHILE ASLEEP',0,'enter_asleep']
];
function sourceHashes(){return Object.fromEntries(['preview/model.js','preview/timeline.js','preview/renderer.js','assets/manifest.json','tools/render_evidence.cjs'].map(p=>[p,SHA(p)]));}
function serializeSample(sample){
 const output={},special=[];
 for(const [key,value]of Object.entries(sample)){
  if(typeof value==='number'&&!Number.isFinite(value)){output[key]=null;special.push({field:key,value:String(value)});}
  else output[key]=value;
 }
 delete output.theme;
 return {input:output,non_finite_numbers:special};
}
function text(ctx,str,x,y,size=18,color='#dce1e7'){ctx.fillStyle=color;ctx.font=size+'px "'+fontName+'"';ctx.fillText(str,x,y);}
function pngFile(c,file){fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,c.toBuffer('image/png'));}
function jpegFile(c,file){fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,c.toBuffer('image/jpeg',92));}
(async()=>{
 fs.mkdirSync(path.join(EVIDENCE,'screenshots'),{recursive:true});
 const loaded=[];
 for(const t of manifest.themes){
  const base=path.join(ROOT,'assets/processed',t.id);
  const assets={eye:await loadImage(path.join(base,'eye.png')),frame:await loadImage(path.join(base,'frame.png')),
   lids:await Promise.all(Array.from({length:9},(_,i)=>loadImage(path.join(base,'lid_0'+i+'.png')))),
   eyeOrigin:t.eye_origin,lidOrigin:t.lid_origin,maxGazeX:t.max_gaze_translation_px[0],maxGazeY:t.max_gaze_translation_px[1]};
  loaded.push({id:t.id,assets,painter:Renderer.createRenderer(createCanvas),canvas:createCanvas(480,480),cursor:null});
 }
 function renderAt(t,ms,scenario='full',incremental=false,lowMode=false){
  const result=incremental?Model.advanceTo(t.cursor,ms,scenario,t.id):Model.simulateAt(ms,scenario,t.id);
  if(incremental)t.cursor=result.cursor;
  const rendered=t.painter.render(t.canvas.getContext('2d'),t.assets,result.pose,{lowMode});
  return {result,rendered};
 }
 const record={status:'OFFSCREEN_CANVAS_REFERENCE_ONLY_NOT_C_GSP',simulated_input:true,source_hashes:sourceHashes(),
  environment:{node:process.version,canvas:'@napi-rs/canvas',font:fontName==='Handoff Sans'?'DejaVu Sans (system font, registered alias Handoff Sans)':'system sans-serif fallback',font_sha256:fs.existsSync(fontFile)?digest(fs.readFileSync(fontFile)):null},
  screenshot_format:'480x480 PNG; character-only; all labels in filenames/metadata',
  key_states:[],direct_entry:[],repeatability:[],alpha_coverage:manifest.build_checks.map(c=>({theme:c.theme,results:c.translation_coverage})),
  not_verified:['real browser controls and presentation','native shared C/GSP','real detector','BSP gestures/buttons','device memory or frame time','hardware']};
 for(const t of loaded)for(const [name,ms]of states){
  const {result}=renderAt(t,ms),file='screenshots/'+t.id+'_'+name+'.png';
  pngFile(t.canvas,path.join(EVIDENCE,file));
  const raw=Buffer.from(t.canvas.getContext('2d').getImageData(0,0,480,480).data);
  const h=digest(raw);
  renderAt(t,ms);
  const h2=digest(Buffer.from(t.canvas.getContext('2d').getImageData(0,0,480,480).data));
  if(h!==h2)throw Error('Non-deterministic render '+file);
  record.key_states.push({theme:t.id,state:name,scenario:'full',time_ms:ms,file,pose:result.pose,raw_rgba_sha256:h,png_sha256:SHA('evidence/'+file)});
  record.repeatability.push({file,identical:true});
 }
 // Compact external-captioned contact sheet; the individual screens are still
 // full 480x480 before scaling to 240 in this review-only contact sheet.
 const cw=720,rh=280,ch=40+rh*scenes.length;
 const sheet=createCanvas(cw,ch),sc=sheet.getContext('2d');
 sc.fillStyle='#101318';sc.fillRect(0,0,cw,ch);
 text(sc,'SIMULATED INPUT / OFFSCREEN CANVAS REFERENCE',14,26,17);
 for(let row=0;row<scenes.length;row++){
  const [label,ms,scenario]=scenes[row],y=40+row*rh;
  for(let col=0;col<loaded.length;col++){const t=loaded[col];const result=renderAt(t,ms,scenario).result;sc.drawImage(t.canvas,col*240,y,240,240);
   if(scenario!=='full')record.direct_entry.push({theme:t.id,scenario,time_ms:ms,pose:result.pose});}
  text(sc,label+'  /  '+(ms/1000).toFixed(3)+' s',10,y+263,15);
 }
 jpegFile(sheet,path.join(EVIDENCE,'scene-contact-sheet.jpg'));
 // Extreme-position and closure diagnostic; not a detector-driven scenario.
 const geom=createCanvas(1440,1560),gc=geom.getContext('2d');
 gc.fillStyle='#101318';gc.fillRect(0,0,geom.width,geom.height);
 const geometryPoses=[
  {gazeX:-1,gazeY:-1,lid:0},{gazeX:1,gazeY:1,lid:0},{gazeX:0,gazeY:0,lid:1}
 ];
 for(let row=0;row<loaded.length;row++)for(let col=0;col<3;col++){
  const t=loaded[row];t.painter.render(t.canvas.getContext('2d'),t.assets,geometryPoses[col]);
  gc.drawImage(t.canvas,col*480,row*520);
  text(gc,t.id+' / '+['EXTREME TOP LEFT','EXTREME BOTTOM RIGHT','FULLY CLOSED'][col],col*480+10,row*520+508,17);
 }
 jpegFile(geom,path.join(EVIDENCE,'geometry-contact-sheet.jpg'));
 fs.writeFileSync(path.join(EVIDENCE,'render-record.json'),JSON.stringify(record,null,2)+'\n');
 if(process.argv.includes('--stills-only')){console.log('Stills and render-record.json exported.');return;}
 const videoFile=path.join(EVIDENCE,'reference-demo.mp4');
 const ff=spawn(process.env.FFMPEG_BIN||'ffmpeg',['-y','-hide_banner','-loglevel','error',
  '-f','rawvideo','-pixel_format','rgba','-video_size',W+'x'+H,'-framerate',String(fps),'-i','pipe:0',
  '-an','-c:v','libx264','-preset','medium','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart',videoFile],{stdio:['pipe','ignore','pipe']});
 let ffError='';ff.stderr.on('data',d=>ffError+=d);ff.stdin.on('error',()=>{});
 const done=new Promise((resolve,reject)=>{ff.on('error',reject);ff.on('close',code=>code===0?resolve():reject(new Error('ffmpeg '+code+' '+ffError)));});
 const movie=createCanvas(W,H),mx=movie.getContext('2d');
 const frameInputs=[];
 const frames=duration/1000*fps;
 for(let i=0;i<frames;i++){
  const ms=i*1000/fps;
  mx.fillStyle='#0d1117';mx.fillRect(0,0,W,H);
  text(mx,'SIMULATED INPUT  /  CANVAS REFERENCE  /  NOT C-GSP OR DEVICE FOOTAGE',18,24,18,'#c6a367');
  const poses={};let sample;
  for(let col=0;col<3;col++){
   const t=loaded[col],{result}=renderAt(t,ms,'full',true);sample=result.sample;poses[t.id]=result.pose;
   text(mx,t.id,col*480+18,52,20);mx.drawImage(t.canvas,col*480,64);
  }
  const p=poses.night_owl,xy=Number.isFinite(sample.target_y)?sample.target_x.toFixed(2)+', '+sample.target_y.toFixed(2):'INVALID';
  text(mx,'t '+(ms/1000).toFixed(2)+'s   '+sample.role_state+'   confirmed '+sample.target_confirmed+'   valid '+sample.data_valid+'   candidate '+sample.candidate_present+'   visible '+sample.ui_visible,18,572,19);
  text(mx,'target ['+xy+']    fallback '+p.fallbackMode+'    export 20 fps (not measured device performance)',18,603,18,'#8e9ba8');
  frameInputs.push({frame_index:i,time_ms:ms,...serializeSample(sample),poses});
  const bytes=Buffer.from(mx.getImageData(0,0,W,H).data);
  if(!ff.stdin.write(bytes))await once(ff.stdin,'drain');
  if(i%200===0)console.log('Reference export '+i+'/'+frames+' frames');
 }
 ff.stdin.end();await done;
 const probe=spawnSync(process.env.FFPROBE_BIN||'ffprobe',['-v','error','-count_frames','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_read_frames,duration:format=duration,size','-of','json',videoFile],{encoding:'utf8'});
 if(probe.status!==0)throw Error('ffprobe failed: '+probe.stderr);
 const metadata=JSON.parse(probe.stdout),vs=metadata.streams[0];
 if(Number(vs.nb_read_frames)!==frames||Number(vs.width)!==W||Number(vs.height)!==H)throw Error('Video frame validation failed');
 record.video={file:'reference-demo.mp4',export_fps:fps,duration_ms:duration,frame_count:frames,width:W,height:H,
  device_rectangles:[{x:0,y:64,width:480,height:480},{x:480,y:64,width:480,height:480},{x:960,y:64,width:480,height:480}],
  sha256:SHA('evidence/reference-demo.mp4'),ffprobe:metadata};
 fs.writeFileSync(path.join(EVIDENCE,'render-record.json'),JSON.stringify(record,null,2)+'\n');
 const inputRecord={format_version:1,status:record.status,simulated_input:true,seed:Model.REFERENCE.seed,model_step_ms:Model.REFERENCE.fixedDtMs,
  video_export_fps:fps,frame_count:frames,duration_ms:duration,themes:loaded.map(t=>t.id),
  input_rules:'For each frame merge input with theme=<selected theme>. Restore non_finite_numbers tags (NaN, Infinity, -Infinity) before exact JS replay. null is a JSON placeholder only and remains invalid without restoration.',
  reference_parameters:Model.REFERENCE,source_hashes:sourceHashes(),markers:Timeline.MARKERS,
  scenarios:Timeline.SCENARIOS,frames:frameInputs};
 fs.writeFileSync(path.join(EVIDENCE,'input-timeline.json'),JSON.stringify(inputRecord,null,2)+'\n');
 console.log('Exported '+frames+' frames / '+(duration/1000)+' seconds. Shared reference renderer only.');
})().catch(e=>{console.error(e.stack);process.exitCode=1;});

