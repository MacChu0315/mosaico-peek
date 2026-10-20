#include "dragon_render.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SIZE 480U
#define STRIDE 488U
#define CANARY 0xA55AU

static const dragon_pose_t rest = {-0.05f, 0.035f, 0, 0.69f, 0.072f, 0.16f};

static unsigned bright_iris(const uint16_t *pixels, double *center_x)
{
    unsigned count = 0;
    double sum = 0;
    for (unsigned y = 0; y < SIZE; ++y) {
        for (unsigned x = 0; x < SIZE; ++x) {
            unsigned c = pixels[y * STRIDE + x];
            unsigned r = ((c >> 11) & 31) * 255 / 31;
            unsigned g = ((c >> 5) & 63) * 255 / 63;
            unsigned b = (c & 31) * 255 / 31;
            if (r > 80 && g > 75 && b * 2 < g && b * 2 < r) {
                ++count;
                sum += x;
            }
        }
    }
    if (center_x) *center_x = count ? sum / count : 0;
    return count;
}

static void write_ppm(const char *directory, const char *name,
                      const uint16_t *pixels)
{
    char path[1024];
    assert(snprintf(path, sizeof(path), "%s/%s.ppm", directory, name) > 0);
    FILE *out = fopen(path, "wb");
    assert(out);
    fprintf(out, "P6\n480 480\n255\n");
    for (unsigned y = 0; y < SIZE; ++y) {
        for (unsigned x = 0; x < SIZE; ++x) {
            unsigned c = pixels[y * STRIDE + x];
            unsigned char rgb[3] = {(unsigned char)(((c >> 11) & 31) * 255 / 31),
                                    (unsigned char)(((c >> 5) & 63) * 255 / 63),
                                    (unsigned char)((c & 31) * 255 / 31)};
            assert(fwrite(rgb, 1, 3, out) == 3);
        }
    }
    assert(fclose(out) == 0);
}

static void check_padding(const uint16_t *pixels)
{
    for (unsigned y = 0; y < SIZE; ++y)
        for (unsigned x = SIZE; x < STRIDE; ++x)
            assert(pixels[y * STRIDE + x] == CANARY);
}

int main(int argc, char **argv)
{
    const size_t count = STRIDE * SIZE;
    uint16_t *whole = malloc((count + 2) * sizeof(*whole));
    uint16_t *tiles = malloc((count + 2) * sizeof(*tiles));
    assert(whole && tiles);
    for (size_t i = 0; i < count + 2; ++i) whole[i] = tiles[i] = CANARY;
    dragon_renderer_t *renderer = dragon_renderer_create();
    assert(renderer);
    assert(dragon_renderer_heap_bytes() > 0);
    assert(dragon_renderer_heap_bytes() < 4*1024*1024);
    assert(dragon_renderer_asset_bytes() >= 641024);
    assert(dragon_renderer_asset_bytes() < 700000);
    assert(!dragon_renderer_draw(renderer, whole + 1, STRIDE * 2, 0, 0, 480, 480));
    dragon_pose_t pose = rest;
    assert(dragon_renderer_prepare(renderer, &pose));
    assert(memcmp(&pose, &rest, sizeof(pose)) == 0);
    assert(dragon_renderer_draw(renderer, whole + 1, STRIDE * 2, 0, 0, 480, 480));
    double rest_x;
    unsigned rest_bright = bright_iris(whole + 1, &rest_x);
    assert(rest_bright > 20000);
    /* The rotated hood sprite must leave source-exterior pixels transparent,
     * rather than stretching a bright edge texel into the top border. */
    assert(((whole[1 + 10 * STRIDE + 55] >> 11) & 31) < 3);
    /* A vertical dark slit separates the bright iris at the resting center. */
    unsigned dark = 0;
    for (unsigned y = 190; y < 290; ++y) {
        uint16_t c = whole[1 + y * STRIDE + 229];
        if (((c >> 11) & 31) < 3 && ((c >> 5) & 63) < 6) ++dark;
    }
    assert(dark > 40);
    if (argc > 1) write_ppm(argv[1], "rest", whole + 1);
    /* Irregular rectangles catch x/y origin and per-row stride mistakes. */
    for (unsigned y = 0; y < SIZE; y += 29) {
        unsigned h = SIZE - y < 29 ? SIZE - y : 29;
        for (unsigned x = 0; x < SIZE; x += 37) {
            unsigned w = SIZE - x < 37 ? SIZE - x : 37;
            assert(dragon_renderer_draw(renderer, tiles + 1 + y * STRIDE + x,
                                        STRIDE * 2, x, y, w, h));
        }
    }
    assert(memcmp(whole, tiles, (count + 2) * sizeof(*whole)) == 0);
    check_padding(whole + 1);
    assert(whole[0] == CANARY && whole[count + 1] == CANARY);
    assert(!dragon_renderer_draw(renderer, whole + 1, STRIDE * 2, 479, 0, 2, 1));
    assert(!dragon_renderer_draw(renderer, whole + 1, 4, 0, 0, 480, 1));
    assert(!dragon_renderer_draw(renderer, whole + 1, STRIDE * 2, 0, 0, 0, 1));
    assert(!dragon_renderer_draw(renderer, whole + 1, STRIDE * 2 + 1, 0, 0, 480, 1));
    pose.gaze_x = NAN;
    assert(!dragon_renderer_prepare(renderer, &pose));
    assert(dragon_renderer_draw(renderer, tiles + 1, STRIDE * 2, 0, 0, 480, 480));
    assert(memcmp(whole, tiles, (count + 2) * sizeof(*whole)) == 0);
    pose = (dragon_pose_t){0.58f, -0.25f, 0, 0.72f, 0.058f, 0.57f};
    assert(dragon_renderer_prepare(renderer, &pose));
    assert(dragon_renderer_draw(renderer, whole + 1, STRIDE * 2, 0, 0, 480, 480));
    double attention_x;
    unsigned side_bright = bright_iris(whole + 1, &attention_x);
    assert(side_bright > 15000);
    assert(attention_x > rest_x + 25);
    if (argc > 1) write_ppm(argv[1], "attention", whole + 1);
    /* The UI can repaint this union while both frames have no blink. All
     * changing open-eye geometry/shadows must stay within it. */
    assert(dragon_renderer_prepare(renderer,&rest));
    assert(dragon_renderer_draw(renderer,tiles+1,STRIDE*2,0,0,480,480));
    for(unsigned y=0;y<480;y++)for(unsigned x=0;x<480;x++){
        if(x<16||x>=464||y<80||y>=416)assert(whole[1+y*STRIDE+x]==tiles[1+y*STRIDE+x]);
    }
    pose = rest;
    pose.blink = 1;
    assert(dragon_renderer_prepare(renderer, &pose));
    assert(dragon_renderer_draw(renderer, whole + 1, STRIDE * 2, 0, 0, 480, 480));
    assert(bright_iris(whole + 1, NULL) == 0);
    if (argc > 1) write_ppm(argv[1], "closed", whole + 1);
    pose.gaze_x = 1;
    pose.gaze_y = -1;
    assert(dragon_renderer_prepare(renderer, &pose));
    assert(dragon_renderer_draw(renderer, whole + 1, STRIDE * 2, 0, 0, 480, 480));
    assert(bright_iris(whole + 1, NULL) == 0);
    pose.blink = 0.8f;
    assert(dragon_renderer_prepare(renderer, &pose));
    assert(dragon_renderer_draw(renderer, whole + 1, STRIDE * 2, 0, 0, 480, 480));
    assert(bright_iris(whole + 1, NULL) < rest_bright / 2);
    check_padding(whole + 1);
    if (argc > 1) write_ppm(argv[1], "extreme-reopen", whole + 1);
    dragon_renderer_destroy(renderer);
    dragon_renderer_destroy(NULL);
    free(whole);
    free(tiles);
    printf("dragon renderer: heap=%zu B, constant assets=%zu B; RGB565 plane=460800 B\n",
           dragon_renderer_heap_bytes(), dragon_renderer_asset_bytes());
    puts("dragon renderer: pixels, complete blink, gaze, clipping, tiles, stride and budget passed");
    return 0;
}
