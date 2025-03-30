import numpy as np
import math
import time

def render_frame(A, B):
    # 도넛 파라미터
    theta_spacing = 0.07  # 더 촘촘한 간격
    phi_spacing = 0.02    # 더 촘촘한 간격
    screen_width = 50     # 더 큰 화면
    screen_height = 50    # 더 큰 화면
    R1 = 1.5  # 도넛 두께 증가l
    R2 = 3    # 도넛 크기 증가
    K2 = 7    # 깊이감 증가
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
                    # 더 다양한 음영 문자 사용
                    output[yp][xp] = " .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"[
                        int((luminance + 1) * 30)]  # 더 많은 음영 단계

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
        A += 0.07  # 회전 속도 조정
        B += 0.03  # 회전 속도 조정
        time.sleep(0.02)  # 더 부드러운 애니메이션