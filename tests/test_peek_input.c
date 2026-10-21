/* SPDX-License-Identifier: Apache-2.0 */
#include "peek_input.h"
#include <assert.h>
#include <stdio.h>
int main(void){
    peek_input_t s={0};
    assert(!peek_input_update(&s,200,200,true,true,0));
    assert(peek_input_update(&s,204,203,false,true,80)==1);
    assert(!peek_input_update(&s,204,203,false,true,90));
    assert(!peek_input_update(&s,400,200,true,true,100));
    assert(!peek_input_update(&s,100,200,true,true,180));
    assert(peek_input_update(&s,90,200,false,true,200)==1);
    assert(!peek_input_update(&s,90,200,false,true,210));
    assert(!peek_input_update(&s,100,200,true,true,300));
    assert(peek_input_update(&s,148,200,false,true,400)==-1);
    /* Dead zone, vertical drag, drag-return and long hold do not become taps. */
    assert(!peek_input_update(&s,200,200,true,true,500));
    assert(!peek_input_update(&s,230,200,false,true,600));
    assert(!peek_input_update(&s,200,100,true,true,700));
    assert(!peek_input_update(&s,200,300,false,true,800));
    assert(!peek_input_update(&s,200,200,true,true,900));
    assert(!peek_input_update(&s,300,200,true,true,950));
    assert(!peek_input_update(&s,200,200,false,true,1000));
    assert(!peek_input_update(&s,200,200,true,true,1100));
    assert(!peek_input_update(&s,200,200,false,true,1800));
    /* A view change or outside/cancelled press cannot leave a trailing click. */
    assert(!peek_input_update(&s,200,200,true,true,1900));peek_input_cancel(&s);
    assert(!peek_input_update(&s,200,200,false,true,2000));
    assert(!peek_input_update(&s,-1,200,true,true,2100));
    assert(!peek_input_update(&s,200,200,true,true,2200));
    assert(!peek_input_update(&s,200,200,false,true,2300));
    assert(!peek_input_update(&s,200,200,true,false,2400));
    assert(!peek_input_update(&s,200,200,false,true,2500));
    assert(!peek_input_update(&s,200,200,true,true,2600));
    assert(!peek_input_update(&s,200,200,false,true,2500));
    puts("PASS tap, bidirectional swipe, release deduplication, cancellation and long/vertical drag");
}
