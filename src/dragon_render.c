#include "dragon_render.h"

#include <math.h>
#include <stdlib.h>

#include "dragon_assets.inc"

/* Reproduces review-inputs/peek-phase2-inputs/approved-dragon/render.mjs.
 * Texture quantization, RGB565 output and analytic shadow coverage are the
 * deliberate approximations; geometry, spherical gaze and layer order follow
 * the approved renderer. Numeric table and texture storage count as app Flash. */
#define FRAME_SIZE 480U
#define Q16 65536
#define Q15 32768
#define EDGE_MIN (-280)
#define EDGE_COUNT 561
#define IRIS_RADIUS_Q15 26870
#define PUPIL_HEIGHT_Q15 15401

typedef struct { int r, g, b; } color_t;

struct dragon_renderer {
    bool ready;
    dragon_pose_t pose;
    int32_t cy, sy, cp, sp;
    int32_t pupil_half_width;
    int32_t hood_v_scale, top_u_scale, top_v_scale, crease_offset;
    int32_t upper[EDGE_COUNT], lower[EDGE_COUNT];
    int32_t upper_outer[EDGE_COUNT], lower_outer[EDGE_COUNT];
    uint16_t upper_normal[EDGE_COUNT], lower_normal[EDGE_COUNT];
    uint16_t vignette[512];
};

static int clamp_int(int value, int low, int high)
{
    return value < low ? low : value > high ? high : value;
}

static int32_t fixed16(float value) { return (int32_t)lroundf(value * Q16); }
static int32_t fixed15(float value) { return (int32_t)lroundf(value * Q15); }

static color_t unpack(uint16_t pixel)
{
    color_t c = {(int)((pixel >> 11) & 31), (int)((pixel >> 5) & 63),
                 (int)(pixel & 31)};
    c.r = (c.r << 3) | (c.r >> 2);
    c.g = (c.g << 2) | (c.g >> 4);
    c.b = (c.b << 3) | (c.b >> 2);
    return c;
}

static uint16_t pack(color_t c)
{
    unsigned r = (unsigned)clamp_int(c.r, 0, 255);
    unsigned g = (unsigned)clamp_int(c.g, 0, 255);
    unsigned b = (unsigned)clamp_int(c.b, 0, 255);
    return (uint16_t)(((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3));
}

static color_t over(color_t under, color_t upper, int alpha)
{
    alpha = clamp_int(alpha, 0, 256);
    color_t c = {under.r + ((upper.r - under.r) * alpha >> 8),
                 under.g + ((upper.g - under.g) * alpha >> 8),
                 under.b + ((upper.b - under.b) * alpha >> 8)};
    return c;
}

/* Four palette lookups interpolate color, never the palette indices. */
static color_t sample(const uint8_t *indices, const uint16_t *palette,
                      unsigned size, int32_t u, int32_t v)
{
    const int32_t maximum = (int32_t)(size - 1) * Q16;
    u = clamp_int(u, 0, maximum);
    v = clamp_int(v, 0, maximum);
    unsigned x = (unsigned)u >> 16, y = (unsigned)v >> 16;
    unsigned x1 = x + (x + 1 < size), y1 = y + (y + 1 < size);
    int fx = (u & 65535) >> 8, fy = (v & 65535) >> 8;
    color_t a = unpack(palette[indices[y * size + x]]);
    color_t b = unpack(palette[indices[y * size + x1]]);
    color_t c = unpack(palette[indices[y1 * size + x]]);
    color_t d = unpack(palette[indices[y1 * size + x1]]);
    return over(over(a, b, fx), over(c, d, fx), fy);
}

static color_t skin(int32_t u, int32_t v)
{
    return sample(dragon_skin_indices, dragon_skin_palette, 480, u, v);
}

static float bezier(float a, float b, float c, float d, float t)
{
    float s = 1.0f - t;
    return s*s*s*a + 3*s*s*t*b + 3*s*t*t*c + t*t*t*d;
}

/* All four source contours are monotonic in x. A 640-segment inverse table
 * preserves the authored cubic, including the reversed coincident close seam. */
static void contour(int32_t *values, const float x[4], const float y[4])
{
    unsigned segment = 1;
    float ax = x[0], ay = y[0];
    float bx = bezier(x[0], x[1], x[2], x[3], 1.0f/640);
    float by = bezier(y[0], y[1], y[2], y[3], 1.0f/640);
    for (int i = 0; i < EDGE_COUNT; ++i) {
        float at = (float)(i + EDGE_MIN);
        if (at <= x[0]) { values[i] = fixed16(y[0]); continue; }
        if (at >= x[3]) { values[i] = fixed16(y[3]); continue; }
        while (bx < at && segment < 640) {
            ax = bx; ay = by; ++segment;
            float t = (float)segment / 640;
            bx = bezier(x[0], x[1], x[2], x[3], t);
            by = bezier(y[0], y[1], y[2], y[3], t);
        }
        values[i] = fixed16(ay + (by-ay) * (at-ax)/(bx-ax));
    }
}

static void normals(const int32_t *edge, uint16_t *out)
{
    for (unsigned i = 0; i < EDGE_COUNT; ++i) {
        unsigned a = i ? i-1 : i, b = i+1 < EDGE_COUNT ? i+1 : i;
        float slope = (float)(edge[b]-edge[a]) / (Q16 * (float)(b-a));
        out[i] = (uint16_t)fixed15(1.0f/sqrtf(1.0f+slope*slope));
    }
}

static int32_t edge_at(const int32_t *table, int32_t x)
{
    int32_t at = x - EDGE_MIN * Q16;
    if (at <= 0) return table[0];
    if (at >= (EDGE_COUNT-1)*Q16) return table[EDGE_COUNT-1];
    unsigned i = (unsigned)at >> 16;
    return table[i] + (int32_t)(((int64_t)(table[i+1]-table[i]) * (at & 65535)) >> 16);
}

static int edge_normal(const uint16_t *table, int32_t x)
{
    int i = clamp_int((x >> 16)-EDGE_MIN, 0, EDGE_COUNT-1);
    return table[i];
}

/* sqrt(r2) in Q15, using the reversed baked sqrt(1-r2) table. */
static int root_q15(int64_t r2)
{
    if (r2 <= 0) return 0;
    if (r2 >= (int64_t)Q15*Q15) return 32767;
    unsigned i = (unsigned)(r2 >> 18);
    unsigned f = (unsigned)(r2 & 262143);
    int a = dragon_sqrt_q15[4096-i], b = dragon_sqrt_q15[4095-i];
    return a + (int)(((int64_t)(b-a)*f) >> 18);
}

static int sine(int32_t radians_q15)
{
    /* 1024/(2*pi), with Q10 coefficient. Unsigned mask wraps negative phase. */
    int index = (int)(((int64_t)radians_q15 * 166886) >> 25);
    return dragon_sin_q15[(unsigned)index & 1023U];
}

static int coverage(int32_t distance_q16)
{
    return clamp_int((distance_q16 + Q16/2) >> 8, 0, 256);
}

static int stroke(int32_t distance_q16, int half_width_q16, int alpha)
{
    int d = distance_q16 < 0 ? -distance_q16 : distance_q16;
    return coverage(half_width_q16-d) * alpha >> 8;
}

static color_t eyeball(const dragon_renderer_t *r, int32_t x, int32_t y)
{
    int nx = (int)(((int64_t)x * Q15) / (233 * Q16));
    int ny = (int)(((int64_t)y * Q15) / (233 * Q16));
    int64_t r2 = (int64_t)nx*nx + (int64_t)ny*ny;
    if (r2 >= (int64_t)Q15*Q15) return (color_t){0,0,0};
    int nz = root_q15((int64_t)Q15*Q15-r2);
    int lx = (r->cy*nx-r->sy*nz) >> 15;
    int az = (r->sy*nx+r->cy*nz) >> 15;
    int ly = (r->cp*ny-r->sp*az) >> 15;
    int64_t radial2 = (int64_t)lx*lx + (int64_t)ly*ly;
    const int64_t iris2 = (int64_t)IRIS_RADIUS_Q15*IRIS_RADIUS_Q15;
    color_t c;
    if (radial2 < iris2) {
        int32_t u = 320*Q16 + (int32_t)((int64_t)lx*61000/82);
        int32_t v = 320*Q16 + (int32_t)((int64_t)ly*61000/82);
        c = sample(dragon_iris_indices, dragon_iris_palette, 640, u, v);
        if (radial2 * 10000 > iris2 * 7744) {
            int radial = root_q15(radial2*Q15*Q15/iris2);
            int limbus = Q15 - (int)(((int64_t)(radial-28836)*13763)/3932);
            limbus = clamp_int(limbus, 19005, Q15);
            c.r = c.r*limbus >> 15; c.g = c.g*limbus >> 15; c.b = c.b*limbus >> 15;
        }
    } else {
        int vein = (sine(lx*75+ly*18)*sine(ly*53-lx*29)) >> 15;
        c = (color_t){49+(vein*5 >> 15), 63+(vein*7 >> 15), 23+(vein*4 >> 15)};
    }
    int abs_y = ly < 0 ? -ly : ly;
    if (abs_y < PUPIL_HEIGHT_Q15) {
        int at = abs_y*256*256/PUPIL_HEIGHT_Q15;
        unsigned i = (unsigned)at >> 8;
        int curve = dragon_pupil_q15[i] +
            ((int)(dragon_pupil_q15[i+1]-dragon_pupil_q15[i])*(at&255) >> 8);
        int half_width = r->pupil_half_width * curve >> 15;
        int abs_x = lx < 0 ? -lx : lx;
        int edge_q8 = ((abs_x-half_width)*233) >> 7;
        int alpha = clamp_int((307-edge_q8)*256/410, 0, 256);
        c = over(c, (color_t){2,3,2}, alpha);
    }
    int dot = (nx*-9503+ny*-12452+nz*28803) >> 15;
    int light = 9830 + ((dot > 0 ? dot : 0)*24576 >> 15);
    int rim = Q15-nz;
    rim = (int)(((int64_t)rim*rim) >> 15);
    rim = (int)(((int64_t)rim*(Q15-nz)*563) >> 38);
    c.r = (c.r*light >> 15)+rim;
    c.g = (c.g*light >> 15)+rim;
    c.b = (c.b*light >> 15)+rim;
    return c;
}

static color_t gloss(color_t c, int32_t x, int32_t y)
{
    int32_t dx = (x+71*Q16) >> 8, dy = (y+57*Q16) >> 8;
    int64_t d2 = (int64_t)dx*dx + (int64_t)dy*dy;
    const int64_t radius2 = (int64_t)48*48*65536;
    if (d2 < radius2) {
        int radius = root_q15(d2*Q15*Q15/radius2);
        c = over(c, (color_t){230,242,192}, (Q15-radius)*36 >> 15);
    }
    /* First ellipse is rotated -0.28 radians in eye-local coordinates. */
    dx = (x+76*Q16) >> 8; dy = (y+51*Q16) >> 8;
    int ex = (int)(((int64_t)dx*31492-(int64_t)dy*9056) >> 15);
    int ey = (int)(((int64_t)dx*9056+(int64_t)dy*31492) >> 15);
    int64_t ellipse = (int64_t)ex*ex*1024/3030384 + (int64_t)ey*ey*1024/629801;
    if (ellipse < 1152) c = over(c, (color_t){250,250,218}, clamp_int((1152-(int)ellipse),0,256)*123 >> 8);
    dx = (x+64*Q16) >> 8; dy = (y+46*Q16) >> 8;
    ellipse = (int64_t)dx*dx*1024/317194 + (int64_t)dy*dy*1024/110756;
    if (ellipse < 1152) c = over(c, (color_t){243,245,202}, clamp_int((1152-(int)ellipse),0,256)*59 >> 8);
    return c;
}

static color_t shade_top_lip(color_t c, int32_t y)
{
    int t = clamp_int((y+175*Q16)/57088, 0, 256);
    int a;
    color_t tint;
    if (t <= 133) {
        int f = t*256/133;
        tint = over((color_t){61,43,67}, (color_t){3,2,6}, f);
        a = 10 + (39*f >> 8);
    } else {
        int f = (t-133)*256/123;
        tint = over((color_t){3,2,6}, (color_t){0,1,0}, f);
        a = 49 + (156*f >> 8);
    }
    return over(c, tint, a);
}

static color_t render_pixel(const dragon_renderer_t *r, unsigned sx, unsigned sy)
{
    /* Fixed inverse rotation of the source canvas's translate(240,247),
     * rotate(-0.16). Pixel centers keep region subdivision deterministic. */
    int32_t px = ((int32_t)sx-240)*Q16+Q16/2;
    int32_t py = ((int32_t)sy-247)*Q16+Q16/2;
    int32_t x = (int32_t)(((int64_t)px*32349-(int64_t)py*5221) >> 15);
    int32_t y = (int32_t)(((int64_t)px*5221+(int64_t)py*32349) >> 15);
    color_t c = over(skin((int32_t)sx*Q16, (int32_t)sy*Q16), (color_t){5,3,10}, 72);
    int32_t upper = edge_at(r->upper, x), lower = edge_at(r->lower, x);
    int us = edge_normal(r->upper_normal,x), ls = edge_normal(r->lower_normal,x);
    int32_t du = (int32_t)(((int64_t)(y-upper)*us) >> 15);
    int32_t dl = (int32_t)(((int64_t)(lower-y)*ls) >> 15);
    int32_t hood_edge = upper;
    if (x < -214*Q16) hood_edge = -280*Q16+(int32_t)((int64_t)(x+280*Q16)*288/66);
    if (x > 214*Q16) hood_edge = -8*Q16-(int32_t)((int64_t)(x-214*Q16)*272/56);
    int hood_alpha = coverage(hood_edge-y);
    if (x < -280*Q16 || x > 270*Q16 || y < -280*Q16) hood_alpha = 0;
    if (hood_alpha) {
        int32_t v = (int32_t)(((int64_t)(y+247*Q16)*r->hood_v_scale) >> 16);
        int32_t u = x+240*Q16;
        /* Canvas drawImage leaves pixels outside its destination rectangle
         * untouched; clamp-to-edge here would visibly smear the top border. */
        color_t h = c;
        if (u >= 0 && u < 480*Q16 && v >= 0 && v < 480*Q16)
            h = skin(u,v);
        h = over(h, (color_t){4,2,9}, 79);
        c = over(c,h,hood_alpha);
    }
    if (r->pose.blink < 1.0f && x >= -214*Q16 && x <= 214*Q16) {
        int32_t inside = du < dl ? du : dl;
        int32_t shadow_u = du-5*Q16, shadow_l = dl+5*Q16;
        int32_t shadow_d = shadow_u < shadow_l ? shadow_u : shadow_l;
        if (shadow_d < 0 && shadow_d > -20*Q16) {
            int a = 256 + shadow_d/5120;
            c = over(c, (color_t){0,0,0}, a*a*115 >> 16);
        }
        int alpha = coverage(inside);
        if (alpha) {
            color_t eye = eyeball(r,x,y);
            eye = over(eye, (color_t){0,4,0}, stroke(du-2*Q16,15*Q16,87));
            eye = over(eye, (color_t){0,4,0}, stroke(du-2*Q16,11*Q16/2,64));
            eye = over(eye, (color_t){1,3,1}, stroke(dl-Q16,7*Q16,115));
            eye = gloss(eye,x,y);
            c = over(c,eye,alpha);
        }
    }
    if (x >= -217*Q16 && x <= 217*Q16) {
        int32_t outer = edge_at(r->upper_outer,x);
        int32_t d = y-outer < upper-y ? y-outer : upper-y;
        int alpha = coverage(d);
        if (alpha) {
            int32_t u = (int32_t)(((int64_t)(x+223*Q16)*r->top_u_scale) >> 16);
            int32_t v = (int32_t)(((int64_t)(y+224*Q16)*r->top_v_scale) >> 16);
            c = over(c,shade_top_lip(skin(u,v),y),alpha);
        }
        outer = edge_at(r->lower_outer,x);
        d = outer-y < y-lower ? outer-y : y-lower;
        alpha = coverage(d);
        if (alpha) c = over(c,over(skin(x+237*Q16,y+222*Q16),(color_t){7,5,11},90),alpha);
    }
    if (x >= -214*Q16 && x <= 214*Q16) {
        c = over(c,(color_t){1,2,1},stroke(du+Q16,3*Q16,225));
        c = over(c,(color_t){34,24,36},stroke(du+4*Q16,72090,174));
        c = over(c,(color_t){1,3,1},stroke(dl+Q16,5*Q16/2,202));
        c = over(c,(color_t){100,103,65},stroke(dl+5*Q16,39322,67));
        c = over(c,(color_t){4,3,7},stroke(du-r->crease_offset,3*Q16/2,67));
    }
    int vx = (int)sx-240, vy = (int)sy-244;
    unsigned distance2 = (unsigned)(vx*vx+vy*vy);
    unsigned at = distance2 >> 8, frac = distance2 & 255;
    int a = r->vignette[at] + ((int)(r->vignette[at+1]-r->vignette[at])*(int)frac >> 8);
    return over(c,(color_t){0,0,0},a);
}

dragon_renderer_t *dragon_renderer_create(void)
{
    dragon_renderer_t *r = calloc(1,sizeof(*r));
    if (!r) return NULL;
    for (unsigned i = 0; i < 512; ++i) {
        float t = (sqrtf((float)i*256)-157)/176;
        float alpha = t <= 0 ? 0 : t < .6f ? t*.26f/.6f :
                      t < 1 ? .26f+(t-.6f)*.49f/.4f : .75f;
        r->vignette[i] = (uint16_t)lroundf(alpha*256);
    }
    return r;
}

void dragon_renderer_destroy(dragon_renderer_t *r) { free(r); }

bool dragon_renderer_prepare(dragon_renderer_t *r, const dragon_pose_t *p)
{
    if (!r || !p || !isfinite(p->gaze_x) || !isfinite(p->gaze_y) ||
        !isfinite(p->blink) || !isfinite(p->squint) ||
        !isfinite(p->pupil_width) || !isfinite(p->tension) ||
        p->gaze_x < -1 || p->gaze_x > 1 || p->gaze_y < -1 || p->gaze_y > 1 ||
        p->blink < 0 || p->blink > 1 || p->squint < 0 || p->squint > 1 ||
        p->pupil_width < 0 || p->pupil_width > 1 || p->tension < 0 || p->tension > 1)
        return false;
    r->pose = *p;
    r->cy = fixed15(cosf(p->gaze_x*.83f));
    r->sy = fixed15(sinf(p->gaze_x*.83f));
    r->cp = fixed15(cosf(p->gaze_y*.72f));
    r->sp = fixed15(sinf(p->gaze_y*.72f));
    r->pupil_half_width = fixed15(.82f*p->pupil_width*1.30f);
    r->hood_v_scale = fixed16(1/(1+p->blink*.25f));
    r->top_u_scale = fixed16(480.0f/450);
    r->crease_offset = fixed16(-32+7*p->tension);
    r->top_v_scale = fixed16(480/(450*(1+p->blink*.16f)));
    float top_h = 158-p->squint*55-p->tension*7;
    float low_h = 186-p->squint*19;
    float b = p->blink;
    float a_y = -top_h*(1-b)+30*b, b_y = -top_h*1.19f*(1-b)+43*b;
    float low_a_x = 130*(1-b)+61*b, low_a_y = low_h*(1-b)+43*b;
    float low_b_x = -91*(1-b)-135*b, low_b_y = low_h*1.04f*(1-b)+30*b;
    const float ux[4] = {-214,-135,61,214}, uy[4] = {8,a_y,b_y,-8};
    const float lx[4] = {-214,low_b_x,low_a_x,214}, ly[4] = {8,low_b_y,low_a_y,-8};
    const float uox[4] = {-217,-139,69,217}, uoy[4] = {4,a_y-32,b_y-37,-14};
    const float lox[4] = {-216,low_b_x-3,low_a_x+2,217}, loy[4] = {13,low_b_y+21,low_a_y+25,-3};
    contour(r->upper,ux,uy); contour(r->lower,lx,ly);
    contour(r->upper_outer,uox,uoy); contour(r->lower_outer,lox,loy);
    normals(r->upper,r->upper_normal); normals(r->lower,r->lower_normal);
    r->ready = true;
    return true;
}

bool dragon_renderer_draw(const dragon_renderer_t *r, uint16_t *pixels,
                          size_t stride_bytes, unsigned x, unsigned y,
                          unsigned width, unsigned height)
{
    if (!r || !r->ready || !pixels || !width || !height ||
        x >= FRAME_SIZE || y >= FRAME_SIZE || width > FRAME_SIZE-x ||
        height > FRAME_SIZE-y || stride_bytes < width*sizeof(*pixels) ||
        stride_bytes % sizeof(*pixels) ||
        (uintptr_t)pixels % _Alignof(uint16_t) ||
        (height > 1 && stride_bytes > (SIZE_MAX-width*sizeof(*pixels))/(height-1)))
        return false;
    for (unsigned row = 0; row < height; ++row) {
        uint16_t *out = (uint16_t *)((uint8_t *)pixels+row*stride_bytes);
        for (unsigned col = 0; col < width; ++col)
            out[col] = pack(render_pixel(r,x+col,y+row));
    }
    return true;
}

size_t dragon_renderer_heap_bytes(void) { return sizeof(dragon_renderer_t); }
size_t dragon_renderer_asset_bytes(void)
{
    return sizeof(dragon_skin_indices)+sizeof(dragon_iris_indices)+
        sizeof(dragon_skin_palette)+sizeof(dragon_iris_palette)+
        sizeof(dragon_sqrt_q15)+sizeof(dragon_pupil_q15)+sizeof(dragon_sin_q15);
}
