/* SPDX-License-Identifier: Apache-2.0 */
/* Fail real renderer allocations, asserting partial ownership is released. */
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
static unsigned attempt,fail_at,live;
static void *checked_malloc(size_t n){if(++attempt==fail_at)return NULL;void *p=malloc(n);if(p)live++;return p;}
static void *checked_calloc(size_t n,size_t s){if(++attempt==fail_at)return NULL;void *p=calloc(n,s);if(p)live++;return p;}
static void checked_free(void *p){if(p){assert(live);live--;}free(p);}
#define malloc checked_malloc
#define calloc checked_calloc
#define free checked_free
#include "../src/eye_pack.c"
#undef malloc
#undef calloc
#undef free
int main(void){
    for(fail_at=1;fail_at<=3;fail_at++){attempt=0;assert(!eye_pack_create());assert(!live);}
    fail_at=0;attempt=0;eye_pack_t *r=eye_pack_create();assert(r&&live==3);
    assert(!eye_pack_select(r,0));assert(eye_pack_select(r,1));dragon_pose_t p={0};assert(eye_pack_prepare(r,&p));
    uint16_t pixel;assert(eye_pack_draw(r,&pixel,2,0,0,1,1));eye_pack_destroy(r);assert(!live);
    eye_pack_destroy(NULL);puts("PASS renderer partial allocation failures release ownership");
}
