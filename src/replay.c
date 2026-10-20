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
bool peek_replay_next(peek_replay_t *r)
{
    uint64_t previous=r->due_ms;
    r->ready=false;
    while(fgets(r->line,LINE_SIZE,r->file)){
        r->line_number++;
        if(r->line[0]=='#'||r->line[0]=='\n')continue;
        if(!strchr(r->line,'\n')&&!feof(r->file))return fail(r,"line too long");
        char kind;int used=0;uint64_t now;
        if(sscanf(r->line,"%c %" SCNu64 " %n",&kind,&now,&used)!=2 || (kind!='P'&&kind!='F'))return fail(r,"expected F or P event");
        if(r->line_number>1&&now<previous)return fail(r,"event clock rollback");
        r->due_ms=now;r->sample=kind=='F';char *p=r->line+used;
        if(r->sample){
            unsigned complete;int n=0;
            if(sscanf(p,"%" SCNu64 " %" SCNu64 " %u %n",&r->frame.sequence,&r->frame.captured_ms,&complete,&n)!=3||complete>1)return fail(r,"invalid frame header");
            p+=n;r->frame.complete=complete;
            for(unsigned i=0;i<768;i++){
                while(isspace((unsigned char)*p))p++;
                if(!*p)return fail(r,"expected 768 temperatures");
                char *end;errno=0;r->frame.c[i]=strtof(p,&end);
                if(end==p||errno==ERANGE)return fail(r,"invalid temperature token");
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
