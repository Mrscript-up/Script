 **IDOR / Broken binding on profile picture** — [INFERRED]: `candidate[picture_cache]` in Request 4 (`POST /connect/profile`) — the value is a raw S3 path `8b336b81-a6ab-469b-b47e-e9fafe452ca8/screenshot_2026-07-14_234838_2_.png`,
 where the UUID prefix was issued by the server in Request 2 (`/uploads/presigned_data`) and the filename is client-controlled.
 There is no signature, token, or nonce binding this value — just a plain form field that tells the server "use this tmp object as my picture.
 " — Test: intercept the PATCH and set `candidate[picture_cache]` to (a) a tmp path generated under a _different_ session (register two accounts, cross the UUIDs), (b) an arbitrary/fabricated key, (c) a path with `../` segments.
 If the server accepts and binds the object, the upload binding has no ownership check.
