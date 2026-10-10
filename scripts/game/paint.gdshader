shader_type canvas_item;
uniform vec2 region_min = vec2(0.0);
uniform vec2 region_size = vec2(600.0);
varying vec2 local_point;
void vertex() { local_point = VERTEX; }
void fragment() {
    vec2 p = (local_point - region_min) / max(region_size, vec2(1.0));
    float saturation = max(COLOR.r, max(COLOR.g, COLOR.b)) - min(COLOR.r, min(COLOR.g, COLOR.b));
    float amount = smoothstep(0.04, 0.22, saturation);
    float glow = pow(clamp(1.0 - length((p - vec2(0.32, 0.24)) * 0.85), 0.0, 1.0), 2.0);
    vec3 painted = mix(COLOR.rgb * 0.77, COLOR.rgb, clamp(glow * 2.0, 0.0, 1.0));
    painted = mix(painted, vec3(1.0), glow * 0.26);
    COLOR.rgb = mix(COLOR.rgb, painted, amount);
}
