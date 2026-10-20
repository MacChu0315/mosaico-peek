# Device rendering and acceptance

The real-device target is MAC `30:ed:a0:f4:52:a0`. Device measurements are independent of Host30Hz, which remains unmet and is not investigated in this continuation.

The first dragon build `d27bc7f` rendered about1.66 non-idle GSP frames/s, with tiled Canvas callbacks about17.64/s; average full-frame raster about557ms plus32ms submit. Its detector incorrectly processed only1.66 samples/s because input was behind the latest-only render mailbox. The corrected acquisition-side owner in `9389137` restores about7.84 accepted samples/s (sequence equals accepted count at every observed snapshot), without detector/role parameter changes. It deliberately does not claim to fix drawing throughput.

After that corrected install the user reported: “太卡太卡了。看不出来”. The120s physical observation captured NOTICE/TRACKING/HOLD/LEAVE and changing sensor coordinates, but the user could not judge visual follow/direction. Do **not** describe that run as accepted. No IDLE was captured after leaving in that particular unlabelled scene; persistent other hot sources are not excluded.

The user suggested consulting sibling Echoy. Its performance work at5c9ae92f showed analogous invisible-geometry/repeated-work costs and exact-pixel checks. Only read-only investigation occurred; no code/dependency/configuration copied. MIT provenance is in THIRD_PARTY and `render-cost-notes.json`.

The Peek renderer's highlighter evaluated four software64-bit ellipse divisions across the entire eye even outside the small highlight's support. Changes use conservative exact support bounds; uint32 numerators are proven below2^32; sphere normalization cancels common scale factors; texture normalization products remain within signed32-bit iris bounds. Circle-highlight scaling uses an exact quotient/remainder decomposition. Zero/full-alpha and integer-coordinate texture cases return the exact old value. No fast-math, texture/geometry/color reduction, renderer downsampling, dependency change or changed detection threshold.

Verification:

- All230400 screen coordinates ×3 channel inputs compare actual production highlights against the retained original expression, plus alpha endpoints and exact normalization.
-43 full-frame poses (seeded random, extreme, open/closed) contain9,907,200 identical RGB565 pixels versus the pre-optimization executable. Hashes/poses are retained;19 prior actual GSP frames also match the new full raster and independent aperture mask.
- Debug/Release CTest10/10 includes the slow-render ownership and exact arithmetic checks. Complete655-event/511-array recorded replay remains unchanged. Final native dynamic replay is retained separately.
- Target relocation sites for `__divdi3` fall from6 to1. This is static code inspection, not a runtime operation count or a measured speedup.

Final installed source/ELF, physical timing/RAM and remaining acceptance gaps are recorded in HANDOFF and `evidence/device-dragon/` after actual installation. GSP engine-render rates, tiled draw callbacks and physical screen FPS remain different quantities. Neither movie encoding nor a callback counter proves panel-visible FPS.
