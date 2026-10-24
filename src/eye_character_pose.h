/* SPDX-License-Identifier: Apache-2.0 */
#pragma once
#include "dragon.h"
#include "peek_orientation.h"
#include "eye_layers.h"
/* Pure presentation transform. Never write back into shared behavior/detection.
 * sleeping includes the450ms close; waking uses the existing150ms open.
 * Ordinary blinks keep their gaze, and other characters retain their pose. */
static inline dragon_pose_t eye_character_pose(unsigned character,const dragon_t *role){
    dragon_pose_t pose=role->pose;
    if(character==3&&(role->sleeping||role->waking)){
        /* Nearest nine-frame shutter is already visually closed from7.5/8. */
        float follow=1-pose.blink/(7.5f/8.f);
        if(follow<=0){pose.gaze_x=0;pose.gaze_y=0;}
        else {pose.gaze_x*=follow;pose.gaze_y*=follow;}
    }
    return pose;
}

/* Center in the source frame, then apply the already-calibrated inverse gaze
 * transform. Canvas quarter-turn is applied separately to the whole artwork. */
static inline dragon_pose_t eye_artwork_pose(unsigned character,const dragon_t *role,unsigned rotation){
    dragon_pose_t pose=eye_character_pose(character,role);
    peek_orientation_gaze(rotation,pose.gaze_x,pose.gaze_y,&pose.gaze_x,&pose.gaze_y);
    if(pose.gaze_x==0)pose.gaze_x=0;
    if(pose.gaze_y==0)pose.gaze_y=0;
    return pose;
}
