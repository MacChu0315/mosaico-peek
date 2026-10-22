/* Run the delivered HTML renderer with a minimal in-memory Canvas/Image adapter.
 * This tests the renderer and PNG pixels, not browser layout or interaction.
 * Requires the already-installed pngjs; does not install anything.
 */
const fs=require('fs'),path=require('path'),vm=require('vm');
const {PNG}=require(require.resolve('pngjs',{paths:[process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES]}));
const dir=path.resolve(__dirname,'../preview');
const evidence=path.resolve(__dirname,'../evidence');
const html=fs.readFileSync(path.join(dir,'index.html'),'utf8');
const code=html.match(/<script>([\s\S]*)<\/script>/)[1];
new Function(code);
class Element{
 constructor(id=''){this.id=id;this.value='0';this.checked=false;this.events={};this.children=[];}
 addEventListener(type,callback){this.events[type]=callback;}
 appendChild(value){this.children.push(value);}
 fire(type){this.events[type]?.({target:this});}
}
class Canvas extends Element{
 constructor(){super();this.width=480;this.height=480;this.buffer=new Uint8ClampedArray(480*480*4);this.context={
  createImageData:(w,h)=>({data:new Uint8ClampedArray(w*h*4),width:w,height:h}),
  drawImage:im=>{this.buffer=new Uint8ClampedArray(im.data);},
  getImageData:()=>({data:this.buffer,width:this.width,height:this.height}),
  putImageData:im=>{this.buffer=new Uint8ClampedArray(im.data);},
  fillRect:()=>{this.buffer.fill(0);for(let i=3;i<this.buffer.length;i+=4)this.buffer[i]=255;}
 };}
 getContext(){return this.context;}
}
class RasterImage{
 set src(value){try{const decoded=PNG.sync.read(Buffer.from(value.split(',')[1],'base64'));this.width=decoded.width;this.height=decoded.height;this.data=decoded.data;queueMicrotask(()=>this.onload());}catch(e){queueMicrotask(()=>this.onerror(e));}}
}
const elements=new Map();elements.set('screen',new Canvas());
const radios=[new Element(),new Element()];radios[0].value='timeline';radios[1].value='manual';
const document={getElementById(id){if(!elements.has(id))elements.set(id,new Element(id));return elements.get(id);},createElement(tag){return tag==='canvas'?new Canvas():new Element();},querySelectorAll(){return radios;}};
const get=id=>document.getElementById(id);
get('manualActive').checked=true;get('manualValid').checked=true;get('manualState').value='IDLE';get('loop').checked=true;
const sandbox={document,window:{},Image:RasterImage,requestAnimationFrame(){},performance,console,Math,Number,Error,Uint8ClampedArray,Uint8Array,Int16Array};
vm.createContext(sandbox);vm.runInContext(code,sandbox);
function assert(condition,message){if(!condition)throw Error(message);}
function stats(){let lit=0,opaque=0;const a=get('screen').buffer;for(let i=0;i<a.length;i+=4){if(a[i]||a[i+1]||a[i+2])lit++;if(a[i+3]===255)opaque++;}return{lit_pixels:lit,opaque_pixels:opaque};}
function save(name){fs.writeFileSync(path.join(evidence,name),PNG.sync.write({width:480,height:480,data:Buffer.from(get('screen').buffer)},{colorType:6}));}
(async()=>{
 await new Promise(resolve=>setImmediate(resolve));
 const api=sandbox.window.__MECHANICAL_C_REFERENCE__;
 assert(api.ready,'Renderer did not load embedded PNG assets.');
 const checks={center:stats()};assert(checks.center.lit_pixels>10000,'Empty center render.');save('node-reference-center.png');
 radios[1].fire('change');get('gx').value='.78';get('gy').value='-.58';get('sh').value='.5';get('manualState').value='TRACKING';get('sh').fire('input');
 checks.diagonal=stats();assert(checks.diagonal.lit_pixels>10000,'Empty diagonal render.');save('node-reference-diagonal.png');
 const s50=Buffer.from(get('screen').buffer);get('sh').value='.51';get('sh').fire('input');
 checks.nearest_frame_050_051_identical=s50.equals(Buffer.from(get('screen').buffer));assert(checks.nearest_frame_050_051_identical,'Shutter frames should use nearest selection.');
 get('manualActive').checked=false;get('manualActive').fire('change');checks.inactive=stats();assert(checks.inactive.lit_pixels===0,'Inactive output is not black.');
 get('manualActive').checked=true;get('manualActive').fire('change');checks.returned=stats();assert(checks.returned.lit_pixels>10000,'Re-entry failed.');
 const timing={};for(const t of [0,1000,16000,17175,18600,20400,21800,23500,28000])timing[t]=api.sampleTimeline(t);
 assert(timing[16000].candidate&&!timing[16000].confirmed&&timing[16000].state==='sleeping'&&timing[16000].shutter===1,'Candidate wakes eye.');
 assert(timing[17175].confirmed&&timing[17175].state==='waking'&&timing[17175].shutter===.5,'Wake midpoint incorrect.');
 assert(!timing[18600].active&&timing[20400].active,'Active step incorrect.');
 assert(!timing[21800].valid&&timing[21800].gaze_x===.55&&!timing[23500].valid&&timing[23500].gaze_x===0,'Invalid hold/recenter incorrect.');
 const report={kind:'actual HTML JavaScript renderer in Node with PNG/ImageData adapter',checks,timeline_checks:'passed',javascript_syntax:true,embedded_png_count:(html.match(/data:image\/png;base64,/g)||[]).length,browser_runtime_verified:false,browser_blocker:'Chromium executable and system browsers absent; no installation performed.',native_verified:false,device_verified:false};
 fs.writeFileSync(path.join(dir,'node-render-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
})().catch(error=>{console.error(error);process.exit(1);});
