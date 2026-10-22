#ifndef DRAGON_POSE_H
#define DRAGON_POSE_H

/* Same normalized coordinates and eyelid values as the approved timeline. */
typedef struct {
    float gaze_x;
    float gaze_y;
    float blink;
    float squint;
    float pupil_width;
    float tension;
} dragon_pose_t;

#endif
