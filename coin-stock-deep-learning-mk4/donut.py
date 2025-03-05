import numpy as np
import math
import time

def render_frame(A, B):
    # 도넛 파라미터
    theta_spacing = 0.10  # 증가
    phi_spacing = 0.05    # 증가
    screen_width = 35     # 감소
    screen_height = 35    # 감소
    R1 = 1  # 도넛의 반지름
    R2 = 2  # 도넛의 중심에서 회전축까지의 거리
    K2 = 5
    K1 = screen_width * K2 * 3/(8 * (R1 + R2))

    output = [[' ' for _ in range(screen_width)] for _ in range(screen_height)]
    zbuffer = [[0 for _ in range(screen_width)] for _ in range(screen_height)]

    cosA, sinA = math.cos(A), math.sin(A)
    cosB, sinB = math.cos(B), math.sin(B)

    for theta in np.arange(0, 2*math.pi, theta_spacing):
        costheta, sintheta = math.cos(theta), math.sin(theta)

        for phi in np.arange(0, 2*math.pi, phi_spacing):
            cosphi, sinphi = math.cos(phi), math.sin(phi)

            # 3D 좌표 계산
            x = R2 + R1*costheta
            y = R1*sintheta
            
            # 3D 회전 변환
            x1 = x*(cosB*cosphi + sinA*sinB*sinphi) - y*cosA*sinB
            y1 = x*(sinB*cosphi - sinA*cosB*sinphi) + y*cosA*cosB
            z1 = K2 + cosA*x*sinphi + y*sinA
            
            # 2D 투영
            ooz = 1/z1
            xp = int(screen_width/2 + K1*ooz*x1)
            yp = int(screen_height/2 - K1*ooz*y1)
            
            # 화면 범위 체크
            if 0 <= xp < screen_width and 0 <= yp < screen_height:
                if ooz > zbuffer[yp][xp]:
                    zbuffer[yp][xp] = ooz
                    # 음영값 계산 및 범위 제한
                    luminance = (cosphi*costheta*sinB - cosA*costheta*sinphi - sinA*sintheta + sinB*sinphi*sintheta)
                    luminance = max(-1, min(1, luminance))  # 값을 -1에서 1 사이로 제한
                    output[yp][xp] = ".,-~:;=!*#$@"[int((luminance + 1) * 5)]  # 인덱스 범위를 0-11로 조정

    # 화면 출력 (원래 방식으로 복구)
    print('\x1b[H')
    for row in output:
        print(''.join(row))

# 메인 루프
if __name__ == '__main__':
    A = 0
    B = 0
    while True:
        render_frame(A, B)
        A += 0.10
        B += 0.05
        time.sleep(0.03)