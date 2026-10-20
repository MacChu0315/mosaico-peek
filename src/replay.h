/* SPDX-License-Identifier: Apache-2.0 */
#pragma once
#include "peek.h"
#include <stdio.h>
typedef struct {FILE *file; char *line; peek_frame_t frame; uint64_t due_ms; bool sample,ready,eof; unsigned line_number; char error[128];} peek_replay_t;
bool peek_replay_open(peek_replay_t *r,const char *path);
void peek_replay_close(peek_replay_t *r);
bool peek_replay_next(peek_replay_t *r);
/* Processes all due input events, then ages data to now. Returns false on parse errors. */
bool peek_replay_until(peek_replay_t *r,peek_detector_t *d,uint64_t now);
void peek_write_result(FILE *out,const peek_detector_t *d);
