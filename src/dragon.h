/* SPDX-License-Identifier: Apache-2.0 */
#pragma once
#include "peek.h"
#include "dragon_pose.h"
typedef enum {DRAGON_IDLE,DRAGON_NOTICE,DRAGON_TRACKING,DRAGON_HOLD,DRAGON_LEAVE} dragon_mode_t;
typedef struct {bool flip_x,flip_y;unsigned rotation;} dragon_mapping_t;
typedef struct {
    dragon_pose_t pose;
    dragon_mode_t mode;
    dragon_mapping_t mapping;
    bool started,target_active,observation_held,stationary,has_observation,quiet;
    uint64_t now_ms,phase_ms,last_samples,last_capture_ms,quiet_since_ms,next_blink_ms;
    uint64_t observations,notices,blinks,transitions;
    float previous_x,previous_y,speed_px_s,goal_x,goal_y,vx,vy;
    uint32_t random;
} dragon_t;
void dragon_reset(dragon_t *c,uint32_t seed);
/* Caller supplies the production core's already-aged result at this same now.
 * Sample evidence uses last_seen/capture time; repeated animation updates never
 * manufacture observations or stationary evidence. Clock rollback is rejected. */
bool dragon_update(dragon_t *c,const peek_result_t *input,uint64_t now_ms);
bool dragon_map(const dragon_mapping_t *mapping,float sensor_x,float sensor_y,float *x,float *y);
const char *dragon_mode_name(dragon_mode_t mode);
