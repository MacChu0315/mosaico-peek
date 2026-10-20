#!/usr/bin/env python3
"""Report actual firmware/UI bytes, target-ABI structure sizes and explicit RAM limits."""
import argparse,hashlib,json,re,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'evidence/phase2/resource-budget.json');args=parser.parse_args()
    build=ROOT/'projects/peek/build';out=args.output.parent;out.mkdir(parents=True,exist_ok=True)
    compiler_file=next((build/'CMakeFiles').glob('*/CMakeCCompiler.cmake'))
    compiler=Path(re.search(r'set\(CMAKE_C_COMPILER "([^"]+)"',compiler_file.read_text())[1])
    objcopy=compiler.with_name(compiler.name.replace('-gcc','-objcopy'))
    obj=ROOT/'build-host/memory-layout.o';binary=obj.with_suffix('.bin')
    subprocess.run([str(compiler),'-std=c11','-c','-Isrc','-Itests/stubs','-Ibuild-host/dragon-generated','tools/memory_layout.c','-o',str(obj)],cwd=ROOT,check=True)
    subprocess.run([str(objcopy),'--dump-section','.rodata.peek_layout='+str(binary),str(obj)],check=True)
    names=['detector','input_frame','role_controller','shared_ui','display_snapshot','device_app','renderer','acquisition_owner','renderer_fixed_cache']
    sizes=dict(zip(names,struct.unpack('<9I',binary.read_bytes())))
    assets=json.loads((ROOT/'assets/dragon/metadata.json').read_text())['generated_include']['total_data_bytes']
    # Source implementation sizeof(renderer), also independently asserted by its native pixel test.
    renderer=sizes['renderer']+sizes['renderer_fixed_cache']
    allocated=sizes['device_app']+2*sizes['display_snapshot']+sizes['acquisition_owner']+renderer
    images={name:{'bytes':(build/name).stat().st_size,'sha256':hashlib.sha256((build/name).read_bytes()).hexdigest()} for name in ['peek.bin','ui_apps.bin']}
    assert images['ui_apps.bin']['bytes']<=0x100000 and images['peek.bin']['bytes']<=0xcf0000
    report={'flash':{'images':images,'ui_apps_partition_bytes':0x100000,'ui_apps_free_bytes':0x100000-images['ui_apps.bin']['bytes'],'ota_0_partition_bytes':0xcf0000,'normal_app_fits_ota_0':True,'factory_partition_bytes':0x1c0000,'normal_app_fits_retained_factory':images['peek.bin']['bytes']<=0x1c0000,'indexed_textures_and_LUT_bytes_in_app':assets,'texture_cost_is_included_in_peek_bin':True,'partition_layout_changed':False},
      'ram_static_estimate':{'target_abi':'ESP32-S31 GCC16.1.0, compile-only actual device structs; GSP handles stubbed as identical opaque pointers','struct_bytes':sizes,'renderer_heap_bytes':renderer,'device_app_plus_producer_consumer_queue_and_renderer_bytes':allocated,'sensor_task_stack_bytes':8192,'single_RGB565_plane_bytes':460800,'eye_plus_diagnostic_canvas_planes_if_both_cached_bytes':460800+384*288*2,'app_temperature_storage_note':'Acquisition owner and display snapshot include complete temperature arrays; counted in struct totals above.','texture_decode_to_RAM_bytes':0,'additional_not_measured':['FreeRTOS queue/task control metadata','GSP Canvas caches and native draw surfaces','GSP scene/font/image caches and scratch','display-presenter framebuffer count, DMA buffers, driver memory','global SDK heaps/stacks and peak allocation overlaps'],'device_peak_RAM_measured':False,'warning':'Known allocations are not a measured device RAM peak; native process RSS includes a different runtime.'}}
    metrics=ROOT/'evidence/phase2/dragon/live-metrics.json'
    if metrics.exists():
        report['native_live_measurements']=json.loads(metrics.read_text())
        report['native_live_measurements_note']='Archived phase2 screenshot/poll runs; current paired A/B measurements are in evidence/followup/performance/'
    args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
