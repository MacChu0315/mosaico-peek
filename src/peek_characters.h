/* SPDX-License-Identifier: Apache-2.0 */
#pragma once
#include <stdbool.h>
/* Stable IDs:1 is retired, never reuse it for another artwork. */
#define PEEK_CHARACTER_COUNT 3
static inline bool peek_character_valid(unsigned id){return id==0||id==2||id==3;}
static inline unsigned peek_character_cycle(unsigned id,int delta){
    static const unsigned ids[PEEK_CHARACTER_COUNT]={0,2,3};
    unsigned index=id==0?0:id==2?1:2;
    return ids[((int)index+PEEK_CHARACTER_COUNT+delta%PEEK_CHARACTER_COUNT)%PEEK_CHARACTER_COUNT];
}
