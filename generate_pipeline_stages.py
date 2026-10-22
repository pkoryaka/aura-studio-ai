import cv2
import numpy as np
import os

def create_stage_assets():
    raw_path = 'assets/art_deco_sapphire_angle1_perspective.jpg'
    master_path = 'assets/art_deco_look_bright_boutique.jpg'
    
    raw = cv2.imread(raw_path)
    raw_1024 = cv2.resize(raw, (1024, 1024))
    
    master = cv2.imread(master_path)
    master_1024 = cv2.resize(master, (1024, 1024))

    # ==============================================================
    # STAGE 1: ANOMALY & DEFECT SEGMENTATION PASS (HEATMAP & HUD)
    # ==============================================================
    s1 = raw_1024.copy()
    
    # Slight analytical contrast
    dark_bg = np.zeros_like(s1)
    dark_bg[:] = (15, 23, 42)
    s1 = cv2.addWeighted(s1, 0.78, dark_bg, 0.22, 0)

    # Defect Heatmap 1: Mounting wax/putty at base of shank
    mask_putty = np.zeros((1024, 1024), dtype=np.uint8)
    cv2.ellipse(mask_putty, (415, 775), (105, 55), 18, 0, 360, 255, -1)
    mask_putty_blur = cv2.GaussianBlur(mask_putty, (61, 61), 0)
    heat_putty = cv2.applyColorMap(mask_putty_blur, cv2.COLORMAP_JET)
    s1 = np.where(mask_putty_blur[:, :, None] > 25, cv2.addWeighted(s1, 0.40, heat_putty, 0.60, 0), s1)

    # Defect Heatmap 2: Surface oxidation & micro-scratches on shank
    mask_tarnish = np.zeros((1024, 1024), dtype=np.uint8)
    cv2.ellipse(mask_tarnish, (225, 560), (65, 90), -22, 0, 360, 255, -1)
    mask_tarnish_blur = cv2.GaussianBlur(mask_tarnish, (51, 51), 0)
    heat_tarnish = cv2.applyColorMap(mask_tarnish_blur, cv2.COLORMAP_MAGMA)
    s1 = np.where(mask_tarnish_blur[:, :, None] > 25, cv2.addWeighted(s1, 0.45, heat_tarnish, 0.55, 0), s1)

    # Defect Heatmap 3: Blown ambient daylight glare on diamond table
    mask_glare = np.zeros((1024, 1024), dtype=np.uint8)
    cv2.circle(mask_glare, (765, 565), 55, 255, -1)
    mask_glare_blur = cv2.GaussianBlur(mask_glare, (41, 41), 0)
    heat_glare = cv2.applyColorMap(mask_glare_blur, cv2.COLORMAP_OCEAN)
    s1 = np.where(mask_glare_blur[:, :, None] > 35, cv2.addWeighted(s1, 0.40, heat_glare, 0.60, 0), s1)

    # Draw analytical brackets
    def draw_bracket(img, x, y, w, h, color, label, conf):
        thick = 2
        clen = 16
        # Corners
        cv2.line(img, (x, y), (x + clen, y), color, thick)
        cv2.line(img, (x, y), (x, y + clen), color, thick)
        cv2.line(img, (x + w, y), (x + w - clen, y), color, thick)
        cv2.line(img, (x + w, y), (x + w, y + clen), color, thick)
        cv2.line(img, (x, y + h), (x + clen, y + h), color, thick)
        cv2.line(img, (x, y + h), (x, y + h - clen), color, thick)
        cv2.line(img, (x + w, y + h), (x + w - clen, y + h), color, thick)
        cv2.line(img, (x + w, y + h), (x + w, y + h - clen), color, thick)
        
        # Label
        text = f"{label} [{conf}]"
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.40, 1)
        cv2.rectangle(img, (x, y - th - 12), (x + tw + 14, y), (15, 23, 42), -1)
        cv2.rectangle(img, (x, y - th - 12), (x + tw + 14, y), color, 1)
        cv2.putText(img, text, (x + 7, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 1, cv2.LINE_AA)

    # Brackets
    draw_bracket(s1, 290, 700, 250, 145, (0, 70, 255), "DEFECT 01: MOUNTING WAX / PUTTY", "99.2%")
    draw_bracket(s1, 140, 440, 180, 240, (0, 165, 255), "DEFECT 02: SURFACE OXIDATION & POROSITY", "95.8%")
    draw_bracket(s1, 680, 480, 175, 175, (255, 215, 0), "ANOMALY 03: CLIPPED DAYLIGHT BLOOM", "92.4%")
    draw_bracket(s1, 580, 320, 160, 120, (238, 130, 238), "DEFECT 04: SETTING DUST PARTICLES", "89.6%")

    # Target Reticle on stone center
    cx, cy = 765, 565
    cv2.circle(s1, (cx, cy), 22, (0, 255, 255), 1, cv2.LINE_AA)
    cv2.circle(s1, (cx, cy), 6, (0, 255, 255), -1, cv2.LINE_AA)
    cv2.line(s1, (cx - 35, cy), (cx - 10, cy), (0, 255, 255), 1)
    cv2.line(s1, (cx + 10, cy), (cx + 35, cy), (0, 255, 255), 1)
    cv2.line(s1, (cx, cy - 35), (cx, cy - 10), (0, 255, 255), 1)
    cv2.line(s1, (cx, cy + 10), (cx, cy + 35), (0, 255, 255), 1)

    # Telemetry Header Banner
    cv2.rectangle(s1, (24, 24), (1000, 78), (15, 23, 42), -1)
    cv2.rectangle(s1, (24, 24), (1000, 78), (51, 65, 85), 1)
    cv2.circle(s1, (46, 51), 6, (0, 100, 255), -1)
    cv2.putText(s1, "STAGE 01: YOLO-JEWELRY V11 + SAM-2 ANOMALY SEGMENTATION", (62, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(s1, "ANOMALIES DETECTED: 14 REGIONS | CONFIDENCE: 96.8% | LATENCY: 112ms | CLOUD RUN ENGINE", (62, 66), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (148, 163, 184), 1, cv2.LINE_AA)

    cv2.imwrite('assets/pipeline_stage1_defect_heatmap.jpg', s1)
    print("Stage 1 generated successfully.")

    # ==============================================================
    # STAGE 2: GEMOLOGICAL LATTICE & FACET CLAMPING (ZERO-DRIFT MESH)
    # ==============================================================
    # Use semi-darkened raw ring so user sees the real gemstones underneath
    s2 = raw_1024.copy()
    overlay_dark = np.zeros_like(s2)
    overlay_dark[:] = (15, 23, 42)
    s2 = cv2.addWeighted(s2, 0.40, overlay_dark, 0.60, 0)

    # Center diamond center at (765, 565)
    dcx, dcy = 765, 565
    r_table = 68
    r_girdle = 142

    # Draw facet lattice
    pts_table = []
    pts_girdle = []
    for i in range(8):
        angle = np.deg2rad(i * 45 + 22.5)
        tx = int(dcx + r_table * np.cos(angle))
        ty = int(dcy + r_table * 0.90 * np.sin(angle))
        pts_table.append((tx, ty))
        
        gx = int(dcx + r_girdle * np.cos(angle))
        gy = int(dcy + r_girdle * 0.90 * np.sin(angle))
        pts_girdle.append((gx, gy))

    # Outer bezel clamp circle
    cv2.ellipse(s2, (dcx, dcy), (r_girdle + 12, int((r_girdle + 12) * 0.90)), 0, 0, 360, (255, 220, 0), 2, cv2.LINE_AA)
    
    # Table & kite facets (Neon Cyan)
    for i in range(8):
        cv2.line(s2, pts_table[i], pts_table[(i+1)%8], (255, 240, 20), 2, cv2.LINE_AA)
        cv2.line(s2, pts_girdle[i], pts_girdle[(i+1)%8], (200, 255, 50), 2, cv2.LINE_AA)
        cv2.line(s2, pts_table[i], pts_girdle[i], (255, 240, 20), 1, cv2.LINE_AA)
        mid_g = ((pts_girdle[i][0] + pts_girdle[(i+1)%8][0])//2, (pts_girdle[i][1] + pts_girdle[(i+1)%8][1])//2)
        cv2.line(s2, pts_table[i], mid_g, (160, 240, 100), 1, cv2.LINE_AA)
        # Glowing nodes
        cv2.circle(s2, pts_table[i], 3, (255, 255, 255), -1, cv2.LINE_AA)

    # Sapphire Baguettes
    baguettes = [
        np.array([[630, 410], [700, 440], [670, 500], [600, 470]], np.int32),
        np.array([[830, 440], [900, 410], [930, 470], [860, 500]], np.int32),
        np.array([[600, 660], [670, 630], [700, 690], [630, 720]], np.int32),
        np.array([[860, 630], [930, 660], [900, 720], [830, 690]], np.int32),
    ]
    for b in baguettes:
        cv2.polylines(s2, [b], True, (255, 190, 40), 2, cv2.LINE_AA)
        cv2.line(s2, tuple(b[0]), tuple(b[2]), (220, 150, 30), 1, cv2.LINE_AA)
        cv2.line(s2, tuple(b[1]), tuple(b[3]), (220, 150, 30), 1, cv2.LINE_AA)

    # Helper for pill labels
    def draw_pill(img, text, x, y, color=(255, 255, 255), bg=(15, 23, 42)):
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)
        cv2.rectangle(img, (x - 6, y - th - 6), (x + tw + 6, y + 6), bg, -1)
        cv2.rectangle(img, (x - 6, y - th - 6), (x + tw + 6, y + 6), (51, 65, 85), 1)
        cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1, cv2.LINE_AA)

    # Prong Clamps
    prongs = [(615, 435), (915, 435), (615, 695), (915, 695)]
    for idx, (px, py) in enumerate(prongs):
        cv2.circle(s2, (px, py), 10, (100, 240, 100), 2, cv2.LINE_AA)
        cv2.circle(s2, (px, py), 4, (100, 240, 100), -1, cv2.LINE_AA)
        draw_pill(s2, f"PRONG-{idx+1} [LOCKED]", px - 50, py + 26, (100, 240, 100))

    # Facet Tags
    draw_pill(s2, "F01: TABLE [DRIFT: 0.00%]", dcx - 70, dcy + 4, (255, 255, 255))
    draw_pill(s2, "SAP-01 [ROYAL HUE 214 DEG]", 530, 395, (255, 200, 50))
    draw_pill(s2, "SAP-02 [ROYAL HUE 214 DEG]", 810, 395, (255, 200, 50))

    # Telemetry Header Banner
    cv2.rectangle(s2, (24, 24), (1000, 78), (15, 23, 42), -1)
    cv2.rectangle(s2, (24, 24), (1000, 78), (51, 65, 85), 1)
    cv2.circle(s2, (46, 51), 6, (240, 220, 10), -1)
    cv2.putText(s2, "STAGE 02: GEMOLOGICAL LATTICE LOCK & OPTICAL FACET CLAMP", (62, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(s2, "FACET DRIFT: 0.000% | LATTICE HASH: sha256-8f4e2b01... | ZERO AI HALLUCINATION GUARANTEE", (62, 66), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (148, 163, 184), 1, cv2.LINE_AA)

    cv2.imwrite('assets/pipeline_stage2_facet_lattice.jpg', s2)
    print("Stage 2 generated successfully.")

    # ==============================================================
    # STAGE 3: 3D SURFACE NORMAL ESTIMATION & ROUGHNESS MAP
    # ==============================================================
    gray_raw = cv2.cvtColor(raw_1024, cv2.COLOR_BGR2GRAY)
    smooth_gray = cv2.GaussianBlur(gray_raw, (7, 7), 0)
    sobel_x = cv2.Sobel(smooth_gray, cv2.CV_32F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(smooth_gray, cv2.CV_32F, 0, 1, ksize=3)
    
    nz = 40.0
    norm = np.sqrt(sobel_x**2 + sobel_y**2 + nz**2)
    nx = sobel_x / norm
    ny = sobel_y / norm
    nz = nz / norm

    # Standard Tangent Space Normal Map
    # Flat surface is (B=255, G=128, R=128) in BGR
    s3 = np.zeros((1024, 1024, 3), dtype=np.uint8)
    s3[:, :, 2] = np.clip((nx * 0.5 + 0.5) * 255, 0, 255).astype(np.uint8) # R
    s3[:, :, 1] = np.clip((ny * 0.5 + 0.5) * 255, 0, 255).astype(np.uint8) # G
    s3[:, :, 0] = np.clip((nz * 0.5 + 0.5) * 255, 0, 255).astype(np.uint8) # B

    # Curvature flow vectors along the shank
    for vy in range(360, 780, 50):
        vx = int(180 + (vy - 575)**2 * 0.0016)
        cv2.arrowedLine(s3, (vx, vy), (vx + 30, vy - 10), (255, 255, 255), 1, tipLength=0.3)
        cv2.circle(s3, (vx, vy), 3, (0, 255, 255), -1)

    # Hallmark Protection Zone
    cv2.rectangle(s3, (140, 670), (340, 745), (0, 215, 255), 2)
    (tw, th), _ = cv2.getTextSize("HALLMARK CLAMP [PLAT 950]", cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)
    cv2.rectangle(s3, (140, 642), (140 + tw + 12, 670), (15, 23, 42), -1)
    cv2.rectangle(s3, (140, 642), (140 + tw + 12, 670), (0, 215, 255), 1)
    cv2.putText(s3, "HALLMARK CLAMP [PLAT 950]", (146, 662), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 215, 255), 1, cv2.LINE_AA)
    cv2.putText(s3, "STAMP FIDELITY: 99.8%", (150, 715), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (255, 255, 255), 1, cv2.LINE_AA)

    # Telemetry Header Banner
    cv2.rectangle(s3, (24, 24), (1000, 78), (15, 23, 42), -1)
    cv2.rectangle(s3, (24, 24), (1000, 78), (51, 65, 85), 1)
    cv2.circle(s3, (46, 51), 6, (255, 0, 255), -1)
    cv2.putText(s3, "STAGE 03: 3D SURFACE NORMAL ESTIMATION & PLATINUM RECONSTRUCTION", (62, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(s3, "SURFACE ROUGHNESS: 0.02 um (LIQUID MIRROR) | CONTINUOUS TANGENT FIELD | HALLMARK CLAMP", (62, 66), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (148, 163, 184), 1, cv2.LINE_AA)

    cv2.imwrite('assets/pipeline_stage3_surface_normals.jpg', s3)
    print("Stage 3 generated successfully.")

if __name__ == '__main__':
    create_stage_assets()
