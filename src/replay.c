/* SPDX-License-Identifier: Apache-2.0 */
#include "replay.h"
#include <errno.h>
#include <inttypes.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#define LINE_SIZE 32768
void peek_replay_close(peek_replay_t *r){if(r->file)fclose(r->file);free(r->line);memset(r,0,sizeof(*r));}
static bool fail(peek_replay_t *r,const char *reason){snprintf(r->error,sizeof(r->error),"line %u: %s",r->line_number,reason);r->ready=false;return false;}
/* Require a complete unsigned decimal token; scanf integer conversion accepts
 * negative values and out-of-range text, and can narrow complete into 0/1. */
static bool decimal(char **cursor,uint64_t maximum,uint64_t *out)
{
    char *p=*cursor;while(isspace((unsigned char)*p))p++;
    if(*p<'0'||*p>'9')return false;
    uint64_t value=0;
    do {
        unsigned digit=(unsigned)(*p-'0');
        if(digit>maximum || value>(maximum-digit)/10)return false;
        value=value*10+digit;p++;
    } while(*p>='0' && *p<='9');
    if(*p && !isspace((unsigned char)*p))return false;
    *cursor=p;*out=value;return true;
}
bool peek_replay_next(peek_replay_t *r)
{
    uint64_t previous=r->due_ms;
    r->ready=false;
    while(fgets(r->line,LINE_SIZE,r->file)){
        r->line_number++;
        if(r->line[0]=='#'||r->line[0]=='\n')continue;
        if(!strchr(r->line,'\n')&&!feof(r->file))return fail(r,"line too long");
        char kind=r->line[0],*p=r->line+1;uint64_t now;
        if((kind!='P' && kind!='F') || !isspace((unsigned char)*p) || !decimal(&p,UINT64_MAX,&now))return fail(r,"expected F/P and unsigned decimal time");
        if(r->line_number>1&&now<previous)return fail(r,"event clock rollback");
        r->due_ms=now;r->sample=kind=='F';
        if(r->sample){
            uint64_t complete;
            if(!decimal(&p,UINT64_MAX,&r->frame.sequence) || !decimal(&p,UINT64_MAX,&r->frame.captured_ms) || !decimal(&p,1,&complete))return fail(r,"invalid unsigned frame header or complete (0/1)");
            r->frame.complete=complete!=0;
            for(unsigned i=0;i<768;i++){
                while(isspace((unsigned char)*p))p++;
                if(!*p)return fail(r,"expected 768 temperatures");
                char *end;errno=0;r->frame.c[i]=strtof(p,&end);
                if(end==p||errno==ERANGE||(*end && !isspace((unsigned char)*end)))return fail(r,"invalid temperature token");
                r->frame.valid[i]=1;p=end;
            }
        }
        while(isspace((unsigned char)*p))p++;
        if(*p)return fail(r,"unexpected trailing data");
        r->ready=true;return true;
    }
    if(ferror(r->file))return fail(r,"read failure");
    r->eof=true;return true;
}
bool peek_replay_open(peek_replay_t *r,const char *path)
{
    memset(r,0,sizeof(*r));r->file=fopen(path,"r");r->line=malloc(LINE_SIZE);
    if(!r->file||!r->line){snprintf(r->error,sizeof(r->error),"cannot open/allocate %s",path);if(r->file)fclose(r->file);free(r->line);r->file=NULL;r->line=NULL;return false;}
    return peek_replay_next(r);
}
bool peek_replay_until(peek_replay_t *r,peek_detector_t *d,uint64_t now)
{
    while(r->ready && r->due_ms<=now){
        if(r->sample)(void)peek_submit(d,&r->frame,r->due_ms);else if(!peek_tick(d,r->due_ms))return false;
        if(!peek_replay_next(r))return false;
    }
    return peek_tick(d,now);
}
void peek_write_result(FILE *out,const peek_detector_t *d)
{
    const peek_result_t *r=&d->result;
    fprintf(out,"{\"now_ms\":%" PRIu64 ",\"sequence\":%" PRIu64 ",\"data\":\"%s\",\"has_valid\":%s,\"target\":%s,\"held\":%s,\"x\":%.5f,\"y\":%.5f,\"area\":%u,\"candidates\":%u,\"background_c\":%.5f,\"last_valid_ms\":%" PRIu64 ",\"last_seen_ms\":%" PRIu64 ",\"samples\":%" PRIu64 "}",d->now_ms,r->sequence,peek_data_name(r->data),r->has_valid?"true":"false",r->has_target?"true":"false",r->held?"true":"false",r->x,r->y,r->area,r->candidates,r->background_c,r->last_valid_ms,r->last_seen_ms,r->accepted_samples);
}
